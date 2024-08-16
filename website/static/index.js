const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

function deletePost(postId){ // Currently not needed
    fetch('/delete_post',{
        method: 'POST',
        body: JSON.stringify({ postId: postId })
    }).then((_res) => {
        window.location.href = "/";
    })
}

function openProfile(username){ // Currently not needed
    fetch('/open_profile',{
        method: 'POST',
        body: JSON.stringify({ username: username })
    })
}

function addComment(username){ // Currently not needed
    fetch('/open_profile',{
        method: 'POST',
        body: JSON.stringify({ username: username })
    }).then((_res) => {
        window.location.href = "/";
    })
}

function followUser(username){
    const followButton = document.getElementById(`follow-button-${username}`);

    fetch(`/follow_user/${username}/`,{ 
        method: 'POST',     
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }, 
    }).then((res) => res.json())
    .then((data) => {
        if (data["followed"] === true ) {
            followButton.innerHTML = "Unfollow";
        } else {
            followButton.innerHTML = "Follow";
        }
    });
}

function likeComment(comment_id){
    const likeCount = document.getElementById(`likes-count-${comment_id}`);
    const likeButton = document.getElementById(`like-button-${comment_id}`);

    fetch(`/like_comment/${comment_id}/`,{
        method: 'POST',     
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
    }).then((res) => res.json())
    .then((data) => {
        likeCount.innerHTML = data["likes"]+" likes";
        if (data["liked"] === true ) {
            likeButton.className = "bi bi-heart-fill text-danger";
        } else {
            likeButton.className = "bi bi-heart";
        }
    });
}

function likePost(post_id){
    const likeCount = document.getElementById(`likes-post-count-${post_id}`);
    const likeButton = document.getElementById(`like-post-button-${post_id}`);
    console.log(csrfToken)

    fetch(`/like_post/${post_id}/`,{
        method: 'POST',     
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
    }).then((res) => res.json())
    .then((data) => {
        likeCount.innerHTML = "Post likes: "+data["likes"];
        if (data["liked"] === true ) {
            likeButton.className = "bi bi-heart-fill text-danger";
        } else {
            likeButton.className = "bi bi-heart";
        }
    });
}

function checkNotifications(){
    const notificationCount = document.getElementById(`notification-count`);

    if (notificationCount) {
    fetch(`/checkNotfications`,{
        method: 'POST',     
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
    }).then(() => {
        notificationCount.remove()
    });
    }
}

function copyClipboard(link) {
     /* Copy the text */
    navigator.clipboard.writeText(link);
}