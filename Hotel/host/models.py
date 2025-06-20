from django.db import models
from django.urls import reverse
# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords

class RoomManager(models.Manager):
    def by_hotel(self, hotel):
        return self.filter(hotel=hotel)

    def available(self):
        return self.filter(availability=True)

    def order_by_price(self):
        return self.order_by('price_per_night')
class RoomQuerySet(models.QuerySet):
    def by_hotel(self, hotel):
        return self.filter(hotel=hotel)

    def available(self):
        return self.exclude(availability=False)

    def order_by_price(self):
        return self.order_by('price_per_night')    
# Модель Пользователи
class User(models.Model):
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефона")
    password = models.CharField(max_length=100, verbose_name="Пароль")
    role = models.CharField(max_length=50, verbose_name="Роль")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

# Модель Отели
class Hotel(models.Model):
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    name = models.CharField(max_length=255, verbose_name="Название")
    location = models.CharField(
        max_length=255,
        verbose_name="Местоположение",
        db_index=True,
        db_collation='NOCASE'
    )
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Рейтинг")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    contact_info = models.CharField(max_length=255, verbose_name="Контакты")
    website = models.URLField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name="Веб-сайт",
        help_text="Официальный сайт отеля"
    )
    booking_url = models.URLField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name="Ссылка на бронирование",
        help_text="Прямая ссылка на страницу бронирования"
    )
    photo = models.ImageField(upload_to='hotel_photos/', blank=True, null=True, verbose_name="Фото")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    history = HistoricalRecords()
    class Meta:
        ordering = ['name']
        verbose_name = "Отели" 
        verbose_name_plural = "Отели"
    def get_absolute_url(self):
        return reverse('hotel_detail', kwargs={'hotel_id': self.id})
    amenities = models.ManyToManyField(
        'Amenity',
        through='HotelAmenity',
        related_name='hotels',
        blank=True,
        verbose_name="Удобства"
    )
    

         
    def __str__(self):
        return self.name

# Модель Удобства
class Amenity(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Удобства"
        verbose_name_plural = "Удобства"
        

    def __str__(self):
        return self.name

# Связь многие-ко-многим между Отель и Удобства
class HotelAmenity(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Отель")
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, verbose_name="Удобство")
    history = HistoricalRecords()

    class Meta:
        
        unique_together = ('hotel', 'amenity')

    def __str__(self):
        return f"{self.hotel.name} - {self.amenity.name}"

# Модель Номера
class Room(models.Model):
    room_type = [
        ('SGL', 'Одноместный'),
        ('DBL', 'Двухместный'),
        ('FAM', 'Семейный'),
        ('LUX', 'Люкс'),
    ]
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Отель", related_name='rooms')
    room_type = models.CharField(max_length=3, choices=room_type,verbose_name="Тип номера")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость за ночь")
    max_guests = models.IntegerField(verbose_name="Максимальное количество гостей")
    availability = models.BooleanField(default=True, verbose_name="Доступность")
    photo = models.ImageField(upload_to='room_photos/', blank=True, null=True, verbose_name="Фото")
     
    objects = RoomQuerySet.as_manager()
    history = HistoricalRecords()
     
    class Meta:
        verbose_name = "Номера"
        verbose_name_plural = "Номера"
    
    def save(self, *args, **kwargs):
        
        if self.price_per_night < 0:
            self.price_per_night = 0
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.room_type} at {self.hotel.name}"

# Модель Отзывы
class Review(models.Model):
    rating = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Отель")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.IntegerField(choices=rating, verbose_name="Рейтинг")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Отзывы"
        verbose_name_plural = "Отзывы"
    

    def __str__(self):
        return f"Review by {self.user} for {self.hotel}"

# Модель Акции
class Promotion(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Отель")
    title = models.CharField(max_length=255, verbose_name="Название акции")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    details_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Подробности акции",
        help_text="Ссылка на страницу с подробным описанием акции"
    )
    booking_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Ссылка на бронирование",
        help_text="Прямая ссылка для бронирования по акции"
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Акции"
        verbose_name_plural = "Акции"

    def __str__(self):
        return self.title

# Модель Услуги отеля
class HotelService(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Отель")
    service_name = models.CharField(max_length=255, verbose_name="Название услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Услуги отеля"
        verbose_name_plural = "Услуги отеля"
    

    def __str__(self):
        return self.service_name

# Модель Бронирования
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Номер")
    check_in_date = models.DateField(verbose_name="Дата заезда")
    check_out_date = models.DateField(verbose_name="Дата выезда")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая стоимость")
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус бронирования"
    )
    confirmation_pdf = models.FileField(
        upload_to='booking_confirmations/%Y/%m/%d/', 
        verbose_name="PDF подтверждение",
        blank=True,
        null=True,
        help_text="PDF файл с подтверждением бронирования"
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Бронирования"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"Booking by {self.user} for {self.room}"

    def save(self, *args, **kwargs):
        if self.confirmation_pdf:
            # Удаляем старый файл при обновлении
            try:
                old_booking = Booking.objects.get(pk=self.pk)
                if old_booking.confirmation_pdf != self.confirmation_pdf:
                    old_booking.confirmation_pdf.delete(save=False)
            except Booking.DoesNotExist:
                pass
        super().save(*args, **kwargs)

# Модель Платеж
class Payment(models.Model):
    payment_method = [
        ('CARD', 'Картой'),
        ('CASH', 'Наличными'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, verbose_name="Бронирование")
    payment_method = models.CharField(
        max_length=5,
        choices=payment_method,
        default='CARD',
        verbose_name='Способ оплаты'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платеж"

    def __str__(self):
        return f"Payment for booking {self.booking}"