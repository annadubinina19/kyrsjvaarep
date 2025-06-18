from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
from django.contrib import messages
from django.utils import timezone
from django.core.files.base import ContentFile
from .admin_export import ExcelExportMixin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    User, Hotel, Amenity, HotelAmenity, Room, Review, Promotion, HotelService, Booking, Payment
)

# Регистрация шрифта для поддержки кириллицы
font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts')
if not os.path.exists(font_path):
    os.makedirs(font_path)

# Путь к шрифту Arial
FONT_PATH = os.path.join(font_path, 'arial.ttf')

# Проверяем наличие шрифта и регистрируем его
if not os.path.exists(FONT_PATH):
    from shutil import copyfile
    windows_font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'arial.ttf')
    if os.path.exists(windows_font_path):
        copyfile(windows_font_path, FONT_PATH)

# Регистрация шрифта
pdfmetrics.registerFont(TTFont('Arial', FONT_PATH))

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
class UserAdmin(SimpleHistoryAdmin):
    list_display = ('last_name', 'first_name', 'email', 'phone_number', 'role')
    list_filter = ('role',)
    search_fields = ('last_name', 'first_name', 'email')
    readonly_fields = ('password',)
    history_list_display = ['last_name', 'first_name', 'email', 'phone_number', 'role']

# Админка для Hotel
@admin.register(Hotel)
class HotelAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'location', 'rating', 'contact_info', 'website', 'display_amenities_count')
    list_filter = ('location', 'rating')
    search_fields = ('name', 'location')
    inlines = [HotelAmenityInline, HotelServiceInline, ReviewInline]
    date_hierarchy = 'created_at'
    list_display_links = ('name', 'location')
    history_list_display = ['name', 'location', 'rating', 'contact_info', 'website']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'location', 'rating', 'description')
        }),
        ('Контактная информация', {
            'fields': ('contact_info', 'website', 'booking_url')
        }),
        ('Медиа', {
            'fields': ('photo',)
        }),
    )

    @admin.display(description="Количество удобств")
    def display_amenities_count(self, obj):
        return obj.hotelamenity_set.count()
    display_amenities_count.short_description = "Количество удобств"

# Админка для Amenity
@admin.register(Amenity)
class AmenityAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    history_list_display = ['name', 'description']

# Админка для Room
@admin.register(Room)
class RoomAdmin(SimpleHistoryAdmin):
    list_display = ('room_type', 'hotel', 'price_per_night', 'max_guests', 'availability')
    list_filter = ('availability', 'hotel')
    search_fields = ('room_type', 'hotel__name')
    raw_id_fields = ('hotel',)
    history_list_display = ['room_type', 'hotel', 'price_per_night', 'max_guests', 'availability']

# Админка для Review
@admin.register(Review)
class ReviewAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'hotel', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__last_name', 'hotel__name')
    raw_id_fields = ('user', 'hotel')
    history_list_display = ['user', 'hotel', 'rating', 'comment']

# Админка для Promotion
@admin.register(Promotion)
class PromotionAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'hotel', 'start_date', 'end_date', 'has_details_url', 'has_booking_url')
    list_filter = ('start_date', 'end_date', 'hotel')
    search_fields = ('title', 'hotel__name')
    raw_id_fields = ('hotel',)
    history_list_display = ['title', 'hotel', 'start_date', 'end_date', 'details_url', 'booking_url']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'hotel', 'description')
        }),
        ('Сроки акции', {
            'fields': ('start_date', 'end_date')
        }),
        ('Ссылки', {
            'fields': ('details_url', 'booking_url'),
            'description': 'Ссылки на подробную информацию и бронирование'
        }),
    )

    @admin.display(description="Подробности", boolean=True)
    def has_details_url(self, obj):
        return bool(obj.details_url)

    @admin.display(description="Бронирование", boolean=True)
    def has_booking_url(self, obj):
        return bool(obj.booking_url)

# Админка для Booking
@admin.register(Booking)
class BookingAdmin(ExcelExportMixin, SimpleHistoryAdmin):
    list_display = ('user', 'room', 'check_in_date', 'check_out_date', 'final_price', 'has_pdf')
    list_filter = ('check_in_date', 'check_out_date')
    search_fields = ('user__last_name', 'room__room_type')
    raw_id_fields = ('user', 'room')
    readonly_fields = ('confirmation_pdf',)
    inlines = [PaymentInline]
    actions = ['generate_pdf', 'export_as_excel']
    history_list_display = ['user', 'room', 'check_in_date', 'check_out_date', 'final_price', 'status']

    def get_export_fields(self):
        
        return ['user', 'room', 'check_in_date', 'check_out_date', 'final_price', 'status']

    def dehydrate_user(self, obj):
       
        return f"{obj.user.first_name} {obj.user.last_name}"

    def dehydrate_room(self, obj):
        
        return f"{obj.room.hotel.name} - {obj.room.get_room_type_display()}"

    def get_user_header(self):
        
        return "Guest Name"

    def get_room_header(self):
        
        return "Hotel and Room"

    def has_pdf(self, obj):
        """Проверяет, есть ли PDF файл у бронирования"""
        return bool(obj.confirmation_pdf)
    has_pdf.boolean = True
    has_pdf.short_description = "PDF сгенерирован"

    def generate_pdf(self, request, queryset):
       
        buffer = BytesIO()
        
        
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='Arial',
            fontSize=16,
            spaceAfter=30
        )
        
        for booking in queryset:
            # Add title
            elements.append(Paragraph(f'Подтверждение бронирования #{booking.id}', title_style))
            
            
            data = [
                ['Информация о бронировании', ''],
                ['Гость', f'{booking.user.first_name} {booking.user.last_name}'],
                ['Отель', booking.room.hotel.name],
                ['Номер', booking.room.get_room_type_display()],
                ['Дата заезда', booking.check_in_date.strftime('%d.%m.%Y')],
                ['Дата выезда', booking.check_out_date.strftime('%d.%m.%Y')],
                ['Стоимость', f'{booking.final_price} руб.'],
                ['Дата генерации', timezone.now().strftime('%d.%m.%Y %H:%M:%S')],
            ]
            
            
            table = Table(data, colWidths=[200, 300])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        
        
        doc.build(elements)
        
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Сохраняем PDF для каждого бронирования
        for booking in queryset:
            # Создаем временный файл
            filename = f'booking_confirmation_{booking.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            
            # Если есть старый файл, удаляем его
            if booking.confirmation_pdf:
                booking.confirmation_pdf.delete()
            
            # Сохраняем новый файл
            booking.confirmation_pdf.save(filename, ContentFile(pdf_content), save=True)
        
        # Добавляем сообщение об успешной генерации
        messages.success(request, f'PDF успешно сгенерирован для {len(queryset)} бронирований')
        
        # Возвращаем последний сгенерированный PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="booking_confirmations.pdf"'
        return response
    
    generate_pdf.short_description = "Сгенерировать PDF подтверждение"

# Админка для Payment
@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = ('booking', 'payment_method', 'amount', 'date')
    list_filter = ('payment_method', 'date')
    search_fields = ('booking__user__last_name',)
    raw_id_fields = ('booking',)
    history_list_display = ['booking', 'payment_method', 'amount', 'date']