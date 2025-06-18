function bookRoom(button) {
    const roomId = button.getAttribute('data-room-id');
    
    // Проверяем, авторизован ли пользователь
    if (!document.querySelector('.auth-buttons .user-info')) {
        alert('Для бронирования необходимо войти в систему');
        openLoginModal();
        return;
    }

    // Disable the button immediately to prevent double booking
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = 'Бронирование...';

    // Отправляем запрос на бронирование
    fetch(`/book-room/${roomId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json().then(data => ({status: response.status, data})))
    .then(({status, data}) => {
        if (data.success) {
            // Показываем сообщение об успехе
            alert('Номер успешно забронирован! Перейдите в личный кабинет, чтобы увидеть детали бронирования.');
            // Обновляем кнопку
            button.textContent = 'Забронировано';
            button.classList.add('booked');
        } else {
            // В случае ошибки возвращаем кнопку в исходное состояние
            button.disabled = false;
            button.textContent = originalText;
            // Показываем сообщение об ошибке
            alert(data.message || 'Произошла ошибка при бронировании');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        // В случае ошибки возвращаем кнопку в исходное состояние
        button.disabled = false;
        button.textContent = originalText;
        alert('Произошла ошибка при бронировании. Пожалуйста, попробуйте позже.');
    });
}

// Функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 