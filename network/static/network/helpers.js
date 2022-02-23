// populates .posts div with a specified set of posts
function load_posts(page, pagenum) {
    // page options: 'index', 'following', or int(profile_id)
    fetch(`posts/${page}/${pagenum}`)
    .then(response => response.json())
    .then(posts => {
        
        let header = posts[0];
        posts = posts.slice(1,);
        // post contains id, poster, poster_id, content, timestamp, likes
        // profile link can be derived from poster_id field
        
        // console.log(header);
        // console.log(posts);

        // identify posts div and pagination ul, clear them
        let divPosts = document.querySelector('.posts');
        let ulPagination = document.querySelector('.pagination');
        divPosts.innerHTML = '';
        ulPagination.innerHTML = '';

        for (let i = 0; i < posts.length; i++) {

            // create post container
            let divPost = document.createElement('div');
            divPost.classList.add('post', 'mb-2', 'p-2');

            // create content container and content divs
            let divContentContainer = document.createElement('div');
                let divContent = document.createElement('div');
                divContent.classList.add('post-content', 'm-2');
                divContent.innerHTML = posts[i].content;
                divContentContainer.append(divContent);
            divPost.append(divContentContainer);

            // create metadata div
            let divMeta = document.createElement('div');
            divMeta.classList.add('post-meta');        
            // create link to profile
            let aProfile = document.createElement('a');
            aProfile.classList.add('post-link');
            // build the href using post.id
            aProfile.href = location.origin + "/profile/" + posts[i].poster_id;
            aProfile.innerHTML = posts[i].poster;
            divMeta.append('posted by ', aProfile, ' on ', posts[i].timestamp);
            divPost.append(divMeta);
            
            // create likes div
            let divLikes = document.createElement('div');
            divLikes.classList.add('post-likes', 'm-1');

            // create like span
            let spanLikeArea = document.createElement('span');
            // create like button
            let aLikes = document.createElement('a');
            aLikes.classList.add('like-button', 'mr-1');
            // create like text
            let spanLikes = document.createElement('span');
            spanLikes.classList.add('like-count');

            spanLikeArea.append(aLikes, spanLikes, " likes");
            divLikes.append(spanLikeArea);
            divPost.append(divLikes);

            // initializes like information at page load
            spanLikes.innerHTML = posts[i].likes_count;

            // determine like icon
            if (posts[i].is_liked) {
                aLikes.innerHTML = '&#127378;'; // 'cool'
            } else {
                aLikes.innerHTML = '&#128307;'; // 'square'
            }
            
                // if you're logged in, then add the like/unlike functionality
                if (header.user_id !== null) {
                    // 1 listener that oscillates between 2 kinds of PUT requests on click
                    aLikes.addEventListener('click', () => like(!posts[i].is_liked));
                    function like(liked) {
                        fetch(`/post/${posts[i].id}`, {
                            method: 'PUT',
                            body: JSON.stringify({like: liked})
                        })
                        .then(() => {
                            // once the 204 is received, reflect the change onto the screen!!!
                            // console.log(liked);
                            if (liked === true) {
                                aLikes.innerHTML = '&#127378;'; // 'cool'
                                spanLikes.innerHTML = parseInt(spanLikes.innerHTML) + 1;
                            } else if (liked === false) {
                                aLikes.innerHTML = '&#128307;'; // 'square'
                                spanLikes.innerHTML = parseInt(spanLikes.innerHTML) - 1;
                            }
                            // edit the specific post's is_liked with javascript too!!!!!!!! 
                            // for the next call of the SAME event listener!!! 
                            posts[i].is_liked = !posts[i].is_liked;
                        });
                    }
                }



            // if logged-in user is also the posts' owner, add edit functionality
            if (header.user_id == posts[i].poster_id) {

                // create edit button, content textarea, & save button
                let buttonEdit = document.createElement('button');
                buttonEdit.classList.add('btn', 'btn-secondary', 'btn-sm', 'ml-2');
                buttonEdit.innerHTML = 'Edit';
                buttonEdit.addEventListener('click', () => edit_post());

                let buttonSave = document.createElement('button');
                buttonSave.classList.add('btn', 'btn-secondary', 'btn-sm', 'ml-2');
                buttonSave.innerHTML = 'Save';
                buttonSave.addEventListener('click', () => save_post());

                let textareaContent = document.createElement('textarea');
                textareaContent.classList.add('edit-post', 'form-control');
                textareaContent.setAttribute('maxlength', 280);
                textareaContent.name = "edit-post";
                
                textareaContent.style.display = 'none';
                buttonSave.style.display = 'none';

                divContentContainer.append(textareaContent);
                divLikes.append(buttonEdit, buttonSave);

                function edit_post() {
                    textareaContent.value = posts[i].content;
                    divContent.style.display = 'none';
                    buttonEdit.style.display = 'none';
                    textareaContent.style.display = 'inline-block';
                    buttonSave.style.display = 'inline-block';
                }

                function save_post() {
                    fetch(`/post/${posts[i].id}`, {
                        method: 'PUT',
                        body: JSON.stringify({content: textareaContent.value})
                    })
                    .then(() => {
                        divContent.innerHTML = textareaContent.value;
                        posts[i].content = textareaContent.value;
                        textareaContent.value = '';
                        divContent.style.display = 'block';
                        buttonEdit.style.display = 'inline-block';
                        textareaContent.style.display = 'none';
                        buttonSave.style.display = 'none';
                    });
                }
            }

            // append completed post to the posts container
            divPosts.append(divPost);
        }
        
        // create Previous button
        let liPrevious = document.createElement('li');
        liPrevious.classList.add('page-item');
            let buttonPrevious = document.createElement('button');
            buttonPrevious.classList.add('page-link');
            buttonPrevious.innerHTML = 'Previous';
            if (header.has_previous) {
                buttonPrevious.addEventListener('click', () => {
                    load_posts(page, pagenum - 1);
                    if(page === 'index') {
                        let indexMessage = document.querySelector('.new-post-message');
                        if (indexMessage) {
                            indexMessage.remove();
                        }
                    }
                });
            } else {
                liPrevious.classList.add('disabled');
            }
        liPrevious.append(buttonPrevious);
        ulPagination.append(liPrevious);

        // create page info
        let liInfo = document.createElement('li');
        liInfo.classList.add('page-item', 'disabled', 'page-info');
            let buttonInfo = document.createElement('button');
            buttonInfo.classList.add('page-link');
            buttonInfo.append('Page ', header.page_number, ' of ', header.total_pages);
        liInfo.append(buttonInfo);
        ulPagination.append(liInfo);

        // create Next button
        let liNext = document.createElement('li');
        liNext.classList.add('page-item');
            let buttonNext = document.createElement('button');
            buttonNext.classList.add('page-link');
            buttonNext.innerHTML = 'Next';
            if (header.has_next) {
                buttonNext.addEventListener('click', () => {
                    load_posts(page, pagenum + 1);
                    if(page === 'index') {
                        let indexMessage = document.querySelector('.new-post-message');
                        if (indexMessage) {
                            indexMessage.remove();
                        }
                    }
                });
            } else {
                liNext.classList.add('disabled');
            }
        liNext.append(buttonNext);
        ulPagination.append(liNext);
        
    })
    .catch(error => {
        console.log(error);
      });
}