document.addEventListener("DOMContentLoaded", function() {

  see_posts(page, pages, follow, profile);

});

function see_posts(page, pages, follow, profile) {
  page = Number(page);
  pages = Number(pages);
  console.log(page, pages);

  var post_source = '';
  var div_source = '';

  // Get correct source to fetch posts
  if (follow) {

    post_source = '/following';
    div_source = '#follow-posts';
  
  } else if (profile) {

    post_source = `/user-posts/${profile_user}`;
    div_source = '#all-posts';

  } else {

    post_source = '/all-posts';
    div_source = '#all-posts';

  }

  fetch(`${post_source}/${page}`)
  .then(response => response.json())
  .then(posts => {

    document.querySelector(div_source).innerHTML = '';
    
    posts.forEach(post => {
      console.log(post);
    const post_div = document.createElement('div');
    post_div.id = `post${post.id}`
    post_div.innerHTML = `
      <h5><a class="profile" href="/profile/${post.poster}" data-id=${post.poster}>${post.poster}</a></h5>
      <p class="content">${post.content}</p>
      `
    if (post.edited) {
      post_div.innerHTML += `
      <p class='edited'>(Edited)</p>
      `;
    }
    post_div.innerHTML += `
      <h6>${post.timestamp}</h6>
      <p><a class="like" data-id = ${post.id}>❤</a><span id='likenum${post.id}'>${post.likes}</span></p>
      `;
    if (user === post.poster) {
      post_div.innerHTML += `
          <a class='edit-post' style='color:rgb(0, 127, 231);' data-id=${post.id}>Edit</a>
      `;
    }

    document.querySelector(div_source).append(post_div);
    });

    // Add pagination nav
    document.querySelector(div_source).innerHTML += `
    <nav id="pagination-nav">
      <ul class="pagination">
        <li class="page-item"><button id="previous" class="page-link">Previous</button></li>
    `;

    if (page === 1) {
      document.getElementById("previous").disabled = true;
    }
    
    for (i=1; i<=pages; i++) {
      document.querySelector(".pagination").innerHTML += `
      <li class="page-item"><button id="go-to-page" class="page-link" data-page=${i}>${i}</button></li>
    `;
    }

    document.querySelector(".pagination").innerHTML += `
    <li class="page-item"><button id="next" class="page-link">Next</button></li>
    `;
    if (page === pages) {
      document.getElementById("next").disabled = true;

    }
    
    document.querySelector(div_source).innerHTML += `
      </ul>
    </nav>
    `;

    if (document.querySelector("#new-post") !== null) {
      document.querySelector("#new-post").onsubmit = () => {
        fetch(`/new-post`, {
          method: 'POST',
          body: JSON.stringify({
              content:document.querySelector("#new-post-content").value
          })
        })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result);
        });
    
        see_posts(page, pages, follow, profile);
      }
    }
    
    document.querySelectorAll(".edit-post").forEach(link => {
      link.addEventListener("click", () => edit_post(link.dataset.id));
    });

    document.querySelectorAll("#next").forEach(button => {
      button.addEventListener("click", () => see_posts(page+1, pages, follow, profile));
    });

    document.querySelectorAll("#go-to-page").forEach(button => {
      button.addEventListener("click", () => see_posts(Number(button.dataset.page), pages, follow, profile));
    });

    document.querySelectorAll("#previous").forEach(button => {
      button.addEventListener("click", () => see_posts(page-1, pages, follow, profile));
    });

    document.querySelectorAll(".like").forEach(link => {
      link.addEventListener("click", () => like(link.dataset.id));
  
    });
 });

}

function edit_post(post_id) {

  const div = document.querySelector(`#post${post_id}`);
  var content = document.querySelector(`#post${post_id} .content`);

  const form = document.createElement("form");
  form.className = "edit-post-form";
  form.dataset.id = post_id;
  form.addEventListener("submit", () => {
    fetch(`/edit/${form.dataset.id}`, {
      method: 'POST',
      body: JSON.stringify({
          content:document.querySelector(`#content${form.dataset.id}`).value,
          edited:true
      })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);
    });

    see_posts(page, pages, follow, profile);
  });

  const edited_content = document.createElement("textarea");
  edited_content.name = "content";
  edited_content.textContent = content.innerHTML;
  edited_content.id = `content${post_id}`;

  const save = document.createElement("input");
  save.type = "submit";
  save.value = "Save";
  save.className = "btn btn-primary";

  form.appendChild(edited_content);
  form.appendChild(document.createElement("br"))
  form.appendChild(save);

  content.innerHTML = '';
  content.appendChild(form);
  document.querySelector(".edit-post").style.display = 'none';

}

function like(post_id) {

  fetch(`/like/${post_id}`)
  .then(response => response.json())
  .then(post => {
    document.getElementById(`likenum${post_id}`).innerHTML = post.likes;
  })

}