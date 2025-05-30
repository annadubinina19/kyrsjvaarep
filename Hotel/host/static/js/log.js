document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();  // Остановить обычную отправку формы

    const formData = new FormData(this);

    fetch('/login/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
  },
  body: formData
})
    .then(response => response.json())
    .then(data => {
        const msg = document.getElementById('login-message');
        if (data.success) {
            msg.style.color = 'green';
            msg.textContent = data.message;
            // Можно скрыть форму
            document.getElementById('loginForm').style.display = 'none';

            // Или обновить интерфейс как надо — например, показать имя пользователя
            // document.body.insertAdjacentHTML('beforeend', `<p>Привет, ${data.message}</p>`);
        } else {
            msg.style.color = 'red';
            msg.textContent = data.message;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
});
function openLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function showRegisterForm() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

function showLoginForm() {
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
}

