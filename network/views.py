from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.forms.widgets import Textarea
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post

from django import forms
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

class NewPostForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'new-post', 'maxlength': 280}), label="What's on your mind?")

# GET Routes

def index(request):

    if 'message' not in request.session:
        request.session['message'] = None

    message = None
    if request.session['message']:
        message = request.session['message']
    request.session['message'] = None

    return render(request, "network/index.html", {
        'new_post_form': NewPostForm(),
        'message': message
    })


def profile(request, profile_id):
    try:
        profile_user = User.objects.get(id=profile_id)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    try:
        is_following = profile_user.followers.get(id=request.user.id)
    except:
        is_following = False

    return render(request, "network/profile.html", {
        'profile_user': profile_user,
        'following': profile_user.following.count(),
        'followers':profile_user.followers.count(),
        'is_owner': profile_user == request.user,
        'is_following': is_following
    })

@login_required(login_url="login")
def following(request):
    return render(request, 'network/following.html')

# POST Routes

@login_required(login_url="login")
def post(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)

    form = NewPostForm(request.POST)
    if not form.is_valid():
        request.session['message'] = 'Invalid post.'
        return HttpResponseRedirect(reverse('index'))

    content = form.cleaned_data['content']
    if len(content) > 280:
        request.session['message'] = 'Post exceeds 280 characters.'
        return HttpResponseRedirect(reverse('index'))

    post = Post(poster=request.user, content=content)
    post.save()
    request.session['message'] = 'Successfully posted.'
    return HttpResponseRedirect(reverse('index'))

@login_required(login_url="login")
def follow(request, profile_id):
    # confirm user existence, else redirect to index
    try:
        profile_user = User.objects.get(id=profile_id)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    # given request.user & profile_id of user you want to follow
    # request.user follows/unfollows profile_id    
    if request.method == "POST":
        try:
            is_following = profile_user.followers.get(id=request.user.id)
        except:
            is_following = False
        if request.POST.get('unfollow', False) and is_following:
            profile_user.followers.remove(request.user)
        elif request.POST.get('follow', False) and not is_following:
            profile_user.followers.add(request.user)

    return HttpResponseRedirect(reverse('profile', kwargs={'profile_id':profile_id}))

# Authentication Routes

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

# API routes

def posts(request, page, pagenum):
    # get the correct set of posts as per the requested page, in the correct order

    if page == "index":
        posts = Post.objects.all()
    elif page == "following" and request.user.is_authenticated:
        following = request.user.following.all()
        posts = Post.objects.filter(poster__in=following)
    else:
        return JsonResponse({'error': 'Invalid page request.'}, status=400)

    # pass that list of json-like dicts as a json string
    return serialize_posts(request, posts, pagenum)


def profile_posts(request, profile_id, pagenum):
    try:
        profile_user = User.objects.get(id=profile_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid page request.'}, status=400)
    # get only user's posts, serialize, send as json string
    posts = Post.objects.filter(poster=profile_user)
    return serialize_posts(request, posts, pagenum)


def serialize_posts(request, posts, pagenum):
    # takes posts queryset, returns list of json-like dicts

    posts = posts.order_by('-timestamp').all()

    paginator = Paginator(posts, 10)
    try:
        page = paginator.page(pagenum)
    except:
        return JsonResponse({'error': 'Invalid page request.'}, status=400)

    header = {
        'page_number': pagenum,
        'total_pages': paginator.num_pages,
        'has_previous': page.has_previous(),
        'has_next': page.has_next(),
        'user_id': request.user.id
    }
    dicts = [header]

    # serialize each object into a json-like dict
    for post in page.object_list:

        post_dict = post.serialize()

        # determine if request.user has liked the post
        try:
            is_liked = post.likes.get(id=request.user.id)
        except:
            is_liked = False
        if request.user.is_authenticated and is_liked:
            post_dict['is_liked'] = True
        else:
            post_dict['is_liked'] = False

        # then collect all json-like dicts into a list
        dicts.append(post_dict)

    return JsonResponse(dicts, safe=False)


@csrf_exempt
@login_required(login_url="login")
def edit_post(request, post_id):
    # can only accept PUT requests
    if request.method != "PUT":
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)

    # confirm post existence, else return error
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({
            "error": "Post does not exist."
        }, status=400)

    # given post_id and a PUT request
    # like/unlike a post, or edit content of post
    
    data = json.loads(request.body)

    if data.get("like") is not None:
        try:
            is_liked = post.likes.get(id=request.user.id)
        except:
            is_liked = False
        if data['like'] == False and is_liked:
            post.likes.remove(request.user)
        elif data['like'] == True and not is_liked:
            post.likes.add(request.user)

    if data.get("content") is not None:

        # check if request.user owns this post
        if post.poster != request.user:
            return JsonResponse({
                "error": "Post can only be edited by its owner."
            }, status=400)

        # check content length
        if len(data['content']) > 280:
            return JsonResponse({
                "error": "Post cannot exceed 280 characters."
            }, status=400)

        post.content = data['content']
        post.save()

    return HttpResponse(status=204)