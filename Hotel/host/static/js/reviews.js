// Функции для работы с модальными окнами отзывов
function openReviewModal() {
    document.getElementById('reviewModal').style.display = 'block';
}

function closeReviewModal() {
    document.getElementById('reviewModal').style.display = 'none';
}

function openEditReviewModal(reviewId, comment, rating) {
    document.getElementById('edit_review_id').value = reviewId;
    document.getElementById('edit_comment').value = comment;
    document.getElementById('edit_rating').value = rating;
    document.getElementById('editReviewModal').style.display = 'block';
}

function closeEditReviewModal() {
    document.getElementById('editReviewModal').style.display = 'none';
}

// Функция для создания HTML элемента отзыва
function createReviewElement(review) {
    const stars = '⭐'.repeat(review.rating);
    return `
        <div class="review-card" id="review-${review.id}">
            <div class="review-header">
                <div class="reviewer-info">
                    <h3>${review.user_name}</h3>
                    <p class="review-date">${review.date}</p>
                </div>
                <div class="review-rating">
                    <span class="stars">${stars}</span>
                    <span class="rating-number">${review.rating}/5</span>
                </div>
            </div>
            <div class="review-content">
                <p>${review.comment}</p>
            </div>
            <div class="review-actions">
                <button onclick="openEditReviewModal(${review.id}, '${review.comment.replace(/'/g, "\\'")}', ${review.rating})" class="edit-review-btn">Редактировать</button>
                <button onclick="deleteReview(${review.id})" class="delete-review-btn">Удалить</button>
            </div>
        </div>
    `;
}

// Функция для отправки нового отзыва
async function submitReview(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch(`/add_review/${hotelId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка при отправке отзыва');
        }

        const data = await response.json();
        const reviewsGrid = document.querySelector('.reviews-grid');
        const noReviews = reviewsGrid.querySelector('.no-reviews');
        
        if (noReviews) {
            noReviews.remove();
        }
        
        reviewsGrid.insertAdjacentHTML('afterbegin', createReviewElement(data));
        closeReviewModal();
        form.reset();

    } catch (error) {
        alert('Произошла ошибка при отправке отзыва');
        console.error('Error:', error);
    }
}

// Функция для редактирования отзыва
async function submitEditReview(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const reviewId = formData.get('review_id');
    
    try {
        const response = await fetch(`/edit_review/${reviewId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка при редактировании отзыва');
        }

        const data = await response.json();
        const reviewCard = document.getElementById(`review-${reviewId}`);
        const stars = '⭐'.repeat(data.rating);
        
        reviewCard.querySelector('.stars').innerHTML = stars;
        reviewCard.querySelector('.rating-number').textContent = `${data.rating}/5`;
        reviewCard.querySelector('.review-content p').textContent = data.comment;
        
        closeEditReviewModal();

    } catch (error) {
        alert('Произошла ошибка при редактировании отзыва');
        console.error('Error:', error);
    }
}

// Функция для удаления отзыва
async function deleteReview(reviewId) {
    if (!confirm('Вы уверены, что хотите удалить этот отзыв?')) {
        return;
    }
    
    try {
        const response = await fetch(`/delete_review/${reviewId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка при удалении отзыва');
        }

        const reviewCard = document.getElementById(`review-${reviewId}`);
        reviewCard.remove();

        const reviewsGrid = document.querySelector('.reviews-grid');
        if (!reviewsGrid.children.length) {
            reviewsGrid.innerHTML = '<p class="no-reviews">Пока нет отзывов об этом отеле</p>';
        }

    } catch (error) {
        alert('Произошла ошибка при удалении отзыва');
        console.error('Error:', error);
    }
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

// Закрытие модальных окон при клике вне их области
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}; 