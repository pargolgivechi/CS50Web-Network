document.addEventListener('DOMContentLoaded', function () {

    const editBtn = document.querySelectorAll('.editBtn');
    const formEdit = document.querySelectorAll('.formEdit');
    formEdit.forEach(element => element.style.display = 'none');


    // Follow & Unfollow
    document.querySelector('.follow') && (document.querySelector('.follow').onclick = function () {
        fetch(`/follow/${this.id}`)
        .then(response => response.json())
        .then(data => {
            this.querySelector('.btn').innerHTML = data.follow_btn;
            let follower = parseInt(document.querySelector('.follower').innerHTML);
            if (data.follow_btn == 'Unfollow'){
                follower += 1;
                document.querySelector('.follower').innerHTML = follower;
            }else{
                follower -= 1;
                document.querySelector('.follower').innerHTML = follower;
            }
        });
    })


    // Like & Unlike
    document.querySelectorAll('.fa-heart').forEach(element => { element.onclick = function () {
        fetch(`/like/${this.dataset.id}`)
        .then(response => response.json())
        .then(data => {
            this.querySelector('.counter').innerHTML = data.total_likes;
            this.className = data.class_name;
        });
      };
    });

    
    // Edit Posts
    editBtn && (editBtn.forEach(element => {element.onclick = function(e) {
        document.querySelector(`#form${this.dataset.edit}`).style.display = 'block';
        const text = document.querySelector(`#change${this.dataset.edit}`);
        const textarea = document.querySelector(`#textarea${this.dataset.edit}`);
        text.style.display = 'none';
        textarea.value = text.textContent

        var _this = this;
        document.querySelector(`#form${this.dataset.edit}`).onsubmit = function(e) {
            fetch(`/edit_post/${_this.dataset.edit}`,{
                method: 'PUT',
                body: JSON.stringify({
                    text: document.querySelector(`#textarea${_this.dataset.edit}`).value
                })
            })
            .then(
                document.querySelector(`#form${_this.dataset.edit}`).style.display = 'none',
                text.textContent = document.querySelector(`#textarea${_this.dataset.edit}`).value,
                text.style.display = 'block'
            );
            e.preventDefault();
        }

        document.querySelector(`#close${this.dataset.edit}`).onclick = function(e) {
            document.querySelector(`#form${_this.dataset.edit}`).style.display = 'none';
            text.style.display = 'block';
            e.preventDefault();
        }
        e.preventDefault();
    }}))
    

});