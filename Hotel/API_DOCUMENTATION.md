# API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
API использует сессионную аутентификацию Django. Для доступа к защищенным эндпоинтам необходимо войти в систему.

## Endpoints

### Users (Пользователи)
- `GET /api/users/` - Список пользователей
- `POST /api/users/` - Создать пользователя
- `GET /api/users/{id}/` - Детали пользователя
- `PUT /api/users/{id}/` - Обновить пользователя
- `DELETE /api/users/{id}/` - Удалить пользователя
- `GET /api/users/{id}/bookings/` - Бронирования пользователя
- `GET /api/users/{id}/reviews/` - Отзывы пользователя

**Фильтры:**
- `role` - фильтр по роли
- `search` - поиск по имени, фамилии, email

### Hotels (Отели)
- `GET /api/hotels/` - Список отелей
- `POST /api/hotels/` - Создать отель
- `GET /api/hotels/{id}/` - Детали отеля
- `PUT /api/hotels/{id}/` - Обновить отель
- `DELETE /api/hotels/{id}/` - Удалить отель
- `GET /api/hotels/{id}/rooms/` - Номера отеля
- `GET /api/hotels/{id}/available_rooms/` - Доступные номера
- `GET /api/hotels/{id}/promotions/` - Акции отеля
- `GET /api/hotels/{id}/services/` - Услуги отеля
- `GET /api/hotels/{id}/stats/` - Статистика отеля
- `GET /api/hotels/top_rated/` - Топ отелей по рейтингу
- `GET /api/hotels/by_location/` - Отели по местоположению

**Фильтры:**
- `min_rating`, `max_rating` - диапазон рейтинга
- `location` - поиск по местоположению
- `has_amenities` - отели с удобствами
- `search` - поиск по названию, местоположению, описанию

### Rooms (Номера)
- `GET /api/rooms/` - Список номеров
- `POST /api/rooms/` - Создать номер
- `GET /api/rooms/{id}/` - Детали номера
- `PUT /api/rooms/{id}/` - Обновить номер
- `DELETE /api/rooms/{id}/` - Удалить номер
- `GET /api/rooms/available/` - Доступные номера
- `GET /api/rooms/by_price_range/` - Номера по диапазону цен

**Фильтры:**
- `min_price`, `max_price` - диапазон цен
- `min_guests` - минимальное количество гостей
- `hotel_name` - поиск по названию отеля
- `hotel`, `room_type`, `availability` - точные фильтры

### Reviews (Отзывы)
- `GET /api/reviews/` - Список отзывов
- `POST /api/reviews/` - Создать отзыв
- `GET /api/reviews/{id}/` - Детали отзыва
- `PUT /api/reviews/{id}/` - Обновить отзыв
- `DELETE /api/reviews/{id}/` - Удалить отзыв
- `GET /api/reviews/recent/` - Последние отзывы

**Фильтры:**
- `min_rating`, `max_rating` - диапазон рейтинга
- `hotel_name` - поиск по названию отеля
- `hotel`, `user`, `rating` - точные фильтры

### Bookings (Бронирования)
- `GET /api/bookings/` - Список бронирований
- `POST /api/bookings/` - Создать бронирование
- `GET /api/bookings/{id}/` - Детали бронирования
- `PUT /api/bookings/{id}/` - Обновить бронирование
- `DELETE /api/bookings/{id}/` - Удалить бронирование
- `POST /api/bookings/{id}/confirm/` - Подтвердить бронирование
- `POST /api/bookings/{id}/cancel/` - Отменить бронирование
- `GET /api/bookings/upcoming/` - Предстоящие бронирования
- `GET /api/bookings/user_bookings/` - Бронирования текущего пользователя

**Фильтры:**
- `check_in_after`, `check_in_before` - диапазон дат заезда
- `check_out_after`, `check_out_before` - диапазон дат выезда
- `min_price`, `max_price` - диапазон цен
- `user`, `room`, `status` - точные фильтры

### Payments (Платежи)
- `GET /api/payments/` - Список платежей
- `POST /api/payments/` - Создать платеж
- `GET /api/payments/{id}/` - Детали платежа
- `PUT /api/payments/{id}/` - Обновить платеж
- `DELETE /api/payments/{id}/` - Удалить платеж
- `GET /api/payments/by_date_range/` - Платежи по диапазону дат
- `GET /api/payments/total_revenue/` - Общая выручка

**Фильтры:**
- `booking`, `payment_method` - точные фильтры

### Promotions (Акции)
- `GET /api/promotions/` - Список акций
- `POST /api/promotions/` - Создать акцию
- `GET /api/promotions/{id}/` - Детали акции
- `PUT /api/promotions/{id}/` - Обновить акцию
- `DELETE /api/promotions/{id}/` - Удалить акцию
- `GET /api/promotions/active/` - Активные акции

**Фильтры:**
- `hotel` - фильтр по отелю
- `search` - поиск по названию и описанию

### Services (Услуги)
- `GET /api/services/` - Список услуг
- `POST /api/services/` - Создать услугу
- `GET /api/services/{id}/` - Детали услуги
- `PUT /api/services/{id}/` - Обновить услугу
- `DELETE /api/services/{id}/` - Удалить услугу

**Фильтры:**
- `hotel` - фильтр по отелю
- `search` - поиск по названию и описанию

### Amenities (Удобства)
- `GET /api/amenities/` - Список удобств
- `POST /api/amenities/` - Создать удобство
- `GET /api/amenities/{id}/` - Детали удобства
- `PUT /api/amenities/{id}/` - Обновить удобство
- `DELETE /api/amenities/{id}/` - Удалить удобство

**Фильтры:**
- `search` - поиск по названию и описанию

## Примеры запросов

### Получить все отели с рейтингом 4 и выше
```
GET /api/hotels/?min_rating=4
```

### Поиск отелей в Москве
```
GET /api/hotels/?location=Москва
```

### Получить доступные номера в определенном отеле
```
GET /api/hotels/1/available_rooms/
```

### Получить номера в диапазоне цен
```
GET /api/rooms/?min_price=1000&max_price=5000
```

### Получить бронирования пользователя
```
GET /api/users/1/bookings/
```

### Создать новое бронирование
```json
POST /api/bookings/
{
    "room_id": 1,
    "check_in_date": "2024-01-15",
    "check_out_date": "2024-01-20",
    "final_price": 15000,
    "status": "pending"
}
```

### Подтвердить бронирование
```
POST /api/bookings/1/confirm/
```

## Пагинация
API использует пагинацию по страницам. По умолчанию на странице 20 элементов.

Пример ответа с пагинацией:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/hotels/?page=2",
    "previous": null,
    "results": [...]
}
```

## Обработка ошибок
API возвращает стандартные HTTP коды состояния:
- `200` - Успешный запрос
- `201` - Объект создан
- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `500` - Внутренняя ошибка сервера 