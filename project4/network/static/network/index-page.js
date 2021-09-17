document.addEventListener('DOMContentLoaded', function() {
  prepare_edit_links();
});

function prepare_edit_links(){
  let posts = document.querySelectorAll("div.post-edit-link");
  posts.forEach((input) => {
    input.addEventListener('click', ()=>edit_post(input));
  });
}

function edit_post(post){
  let post_text_div = post.querySelector("div.post-context")
  //post_text_div.style.display = "none"

  const edit_div = document.createElement('div');
  let html = `
      <div class="row" m-2>
        <div class="col">
            <form method="post" action="">
                {% csrf_token %}
                <div class="form-group">
                    <textarea type="text" name="post-text" class="form-control mb-2" id="newPostText" rows="3"></textarea>
                </div>
                <button type="button" class="btn btn-primary mb-2">Save</button>
            </form>
        </div>
    </div>`

  post_text_div.innerHTML = html;

}