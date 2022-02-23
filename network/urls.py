
from django.urls import path

from . import views

urlpatterns = [
    # GET Routes
    path("", views.index, name="index"),
    path('profile/<int:profile_id>', views.profile, name="profile"),
    path('following', views.following, name="following"),

    # POST Routes
    path("post", views.post, name="post"),
    path('follow/<int:profile_id>', views.follow, name="follow"),

    # Authentication Routes
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("posts/<str:page>/<int:pagenum>", views.posts, name="posts"),
    path("profile/posts/<int:profile_id>/<int:pagenum>", views.profile_posts, name="profile_posts"),
    path("post/<int:post_id>", views.edit_post, name="edit_post")
]
