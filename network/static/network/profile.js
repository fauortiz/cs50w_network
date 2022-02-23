

document.addEventListener('DOMContentLoaded', () => {
    let id = document.querySelector('#profileId').dataset.id;
    load_posts(id, 1);
});