document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
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
                if (data.success) {
                    // После успешного входа просто перезагружаем текущую страницу
                    window.location.reload();
                } else {
                    const msg = document.getElementById('login-message');
                    msg.style.color = 'red';
                    msg.textContent = data.message;
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при входе');
            });
        });
    }

    // Обработчик формы регистрации
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch('/register/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const msg = document.getElementById('register-message');
                if (data.success) {
                    msg.style.color = 'green';
                    msg.textContent = data.message;
                    // После успешной регистрации показываем форму входа
                    showLoginForm();
                } else {
                    msg.style.color = 'red';
                    msg.textContent = data.message;
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при регистрации');
            });
        });
    }
});

function openLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
    showLoginForm(); // По умолчанию показываем форму входа
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

// Закрытие модальных окон при клике вне их области
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
};

