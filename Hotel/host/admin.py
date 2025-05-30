

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User, Hotel, Amenity, HotelAmenity, Room, Review, Promotion, HotelService, Booking, Payment,ADexam
)

# Inline для связи HotelAmenity
class HotelAmenityInline(admin.TabularInline):
    model = HotelAmenity
    extra = 1

# Inline для услуг отеля
class HotelServiceInline(admin.TabularInline):
    model = HotelService
    extra = 1

# Inline для отзывов
class ReviewInline(admin.StackedInline):
    model = Review
    extra = 1

# Inline для бронирований
class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1

# Inline для платежей
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

# Админка для User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'phone_number', 'role')
    list_filter = ('role',)
    search_fields = ('last_name', 'first_name', 'email')
    readonly_fields = ('password',)

# Админка для Hotel
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'rating', 'contact_info', 'display_amenities_count')
    
    list_filter = ('location', 'rating')
    search_fields = ('name', 'location')
    inlines = [HotelAmenityInline, HotelServiceInline, ReviewInline]
    date_hierarchy = 'created_at'
    list_display_links = ('name', 'location')
    

    @admin.display(description="Количество удобств")
    def display_amenities_count(self, obj):
        return obj.hotelamenity_set.count()
    display_amenities_count.short_description = "Количество удобств"

# Админка для Amenity
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# Админка для Room
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'hotel', 'price_per_night', 'max_guests', 'availability')
    list_filter = ('availability', 'hotel')
    search_fields = ('room_type', 'hotel__name')
    raw_id_fields = ('hotel',)

# Админка для Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__last_name', 'hotel__name')
    raw_id_fields = ('user', 'hotel')

# Админка для Promotion
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'hotel', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('title', 'hotel__name')
    raw_id_fields = ('hotel',)

# Админка для Booking
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in_date', 'check_out_date', 'final_price')
    list_filter = ('check_in_date', 'check_out_date')
    search_fields = ('user__last_name', 'room__room_type')
    raw_id_fields = ('user', 'room')
    inlines = [PaymentInline]

# Админка для Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'payment_method', 'amount', 'date')
    list_filter = ('payment_method', 'date')
    search_fields = ('booking__user__last_name',)
    raw_id_fields = ('booking',)

@admin.register(ADexam)
class ADexamAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_date', 'is_public', 'created_at')
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "-"
    image_tag.short_description = 'Задание (изображение)'
    list_filter = ('is_public', 'created_at', 'exam_date')  # Фильтры справа
    search_fields = ('name', 'users__email')  # Поиск по названию экзамена и email пользователя
    filter_horizontal = ('users',)  # Удобный вид M2M выбора пользователей
    date_hierarchy = 'exam_date'  # Навигация по дате проведения экзамена    