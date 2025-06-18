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
                    // Закрываем модальное окно
                    closeLoginModal();
                    
                    // Обновляем интерфейс
                    const authButtons = document.querySelector('.auth-buttons');
                    if (authButtons) {
                        const userName = data.message.split(',')[1].trim().replace('!', '');
                        authButtons.innerHTML = `
                            <div class="user-info">Добро пожаловать, ${userName}!</div>
                            <a href="/profile/" class="profile-btn">👤 Личный кабинет</a>
                            <a href="/logout/" class="logout-btn">Выход</a>
                        `;
                    }
                } else {
                    const msg = document.getElementById('login-message');
                    if (msg) {
                        msg.style.display = 'block';
                        msg.style.color = 'red';
                        msg.textContent = data.message;
                    }
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
                if (msg) {
                    msg.style.display = 'block';
                    if (data.success) {
                        msg.style.color = 'green';
                        msg.textContent = data.message;
                        // После успешной регистрации показываем форму входа
                        setTimeout(() => {
                            showLoginForm();
                            msg.style.display = 'none';
                        }, 2000);
                    } else {
                        msg.style.color = 'red';
                        msg.textContent = data.message;
                    }
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
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'block';
        showLoginForm();
    }
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'none';
        // Очищаем сообщения при закрытии
        const loginMsg = document.getElementById('login-message');
        const registerMsg = document.getElementById('register-message');
        if (loginMsg) loginMsg.style.display = 'none';
        if (registerMsg) registerMsg.style.display = 'none';
    }
}

function showRegisterForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    if (loginForm && registerForm) {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        // Очищаем сообщения при переключении форм
        const loginMsg = document.getElementById('login-message');
        if (loginMsg) loginMsg.style.display = 'none';
    }
}

function showLoginForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    if (loginForm && registerForm) {
        registerForm.style.display = 'none';
        loginForm.style.display = 'block';
        // Очищаем сообщения при переключении форм
        const registerMsg = document.getElementById('register-message');
        if (registerMsg) registerMsg.style.display = 'none';
    }
}

// Закрытие модальных окон при клике вне их области
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        closeLoginModal();
    }
};

