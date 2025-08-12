// helper
function handleJSONResponse(res){
  if (!res.ok) return res.json().then(j => Promise.reject(j));
  return res.json();
}

// delete book button on home page
document.addEventListener('click', function (e) {
  if (e.target && e.target.matches('.delete-book-btn')) {
    const id = e.target.dataset.id;
    if (!confirm('Delete this book?')) return;
    fetch(`/api/delete_book/${id}`, { method: 'DELETE' })
      .then(handleJSONResponse)
      .then(() => {
        const tr = e.target.closest('tr');
        tr && tr.remove();
      })
      .catch(err => alert(err.error || 'Could not delete'));
  }
});

// add book form
const addForm = document.getElementById('add-book-form');
if (addForm) {
  addForm.addEventListener('submit', function (ev) {
    ev.preventDefault();
    const title = document.getElementById('book-title').value.trim();
    const author = document.getElementById('book-author').value.trim();
    const qty = document.getElementById('book-quantity').value || 1;
    fetch('/api/add_book', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ title, author, quantity: qty })
    })
    .then(handleJSONResponse)
    .then(data => {
      document.getElementById('add-result').textContent = 'Book added!';
      // redirect to home to see list
      setTimeout(()=> location.href = '/', 600);
    })
    .catch(err => {
      document.getElementById('add-result').textContent = err.error || 'Error adding book';
    });
  });
}

// issue book page — load available books and wire issue action
const availArea = document.getElementById('available-books-area');
if (availArea) {
  fetch('/api/available_books')
    .then(handleJSONResponse)
    .then(data => {
      const books = data.books;
      if (!books.length) {
        availArea.innerHTML = '<p>No available books to issue.</p>';
        return;
      }
      const ul = document.createElement('div');
      ul.className = 'table';
      let inner = '<table><thead><tr><th>Title</th><th>Author</th><th>Qty</th><th>Action</th></tr></thead><tbody>';
      for (const b of books) {
        inner += `<tr data-book-id="${b.id}"><td>${b.title}</td><td>${b.author}</td><td>${b.quantity}</td>
          <td><button class="issue-btn" data-id="${b.id}">Issue</button></td></tr>`;
      }
      inner += '</tbody></table>';
      availArea.innerHTML = inner;
    })
    .catch(()=> availArea.innerHTML = '<p>Error loading books.</p>');
}

document.addEventListener('click', function (e) {
  if (e.target && e.target.matches('.issue-btn')) {
    const id = e.target.dataset.id;
    if (!confirm('Issue this book to yourself?')) return;
    fetch('/api/issue_book', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ book_id: id })
    })
    .then(handleJSONResponse)
    .then(() => {
      alert('Book issued! Check My Account.');
      location.href = '/user_account';
    })
    .catch(err => alert(err.error || 'Could not issue book'));
  }
});

// user account page — load issued books
const issuedArea = document.getElementById('issued-area');
if (issuedArea) {
  fetch('/api/user_issued')
    .then(handleJSONResponse)
    .then(data => {
      const issued = data.issued;
      if (!issued.length) {
        issuedArea.innerHTML = '<p>You have not issued any books.</p>';
        return;
      }
      let html = '<table class="table"><thead><tr><th>Title</th><th>Author</th><th>Issued</th><th>Returned</th></tr></thead><tbody>';
      for (const i of issued) {
        html += `<tr><td>${i.title}</td><td>${i.author}</td><td>${i.issue_date}</td><td>${i.return_date || '-'}</td></tr>`;
      }
      html += '</tbody></table>';
      issuedArea.innerHTML = html;
    })
    .catch(()=> issuedArea.innerHTML = '<p>Error loading issued books.</p>');
}
