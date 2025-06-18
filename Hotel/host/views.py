from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
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
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse
import requests

from .models import (
    User as CustomUser, Hotel, Amenity, HotelAmenity, Room, Review, 
    Promotion, HotelService, Booking, Payment
)
from .forms import HotelForm, HotelAmenityForm

# Здесь должны быть только обычные Django views для HTML-страниц, без DRF ViewSet-классов.
# ... ваши обычные views ...

def search(request):
    location = request.GET.get('location', '').strip()
    check_in = request.GET.get('check_in')
    sort_by = request.GET.get('sort_by')
    page = request.GET.get('page', 1)
    today = timezone.now().date().isoformat()

    params = {
        'location': location,
        'page': page,
        'page_size': 1,
    }
    if sort_by:
        params['ordering'] = sort_by

    api_url = request.build_absolute_uri('/api/hotels/')
    response = requests.get(api_url, params=params, cookies=request.COOKIES)
    data = response.json()

    hotels = data.get('results', [])
    hotel_count = data.get('count', 0)
    next_url = data.get('next')
    previous_url = data.get('previous')
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 1)
    num_pages = (hotel_count // page_size) + (1 if hotel_count % page_size else 0)
    current_page = int(page)

    class HotelsPage:
        def __init__(self, hotels, number, num_pages, next_url, previous_url):
            self.object_list = hotels
            self.number = number
            self.paginator = self
            self.num_pages = num_pages
            self.has_next = bool(next_url)
            self.has_previous = bool(previous_url)
            self.next_page_number = number + 1 if self.has_next else number
            self.previous_page_number = number - 1 if self.has_previous else number
        def __iter__(self):
            return iter(self.object_list)

    hotels_page = HotelsPage(hotels, current_page, num_pages, next_url, previous_url)

    return render(request, 'host/search.html', {
        'hotels': hotels_page,
        'hotel_count': hotel_count,
        'location': location,
        'check_in': check_in,
        'sort_by': sort_by,
        'today': today
    })

@require_POST
def register_user(request):
    try:
        last_name = request.POST['last_name']
        first_name = request.POST['first_name']
        email = request.POST['email']
        password = request.POST['password']
        phone_number = request.POST['phone_number']

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email уже зарегистрирован'})

        CustomUser.objects.create(
            last_name=last_name,
            first_name=first_name,
            email=email,
            password=password,  
            phone_number=phone_number,
            role='гость'
        )
        return JsonResponse({'success': True, 'message': 'Регистрация прошла успешно'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
def login_user(request):
    email = request.POST.get("email")
    password = request.POST.get("password")

    try:
        user = CustomUser.objects.get(email=email, password=password)
        request.session['user_id'] = user.id
        request.session['user_name'] = user.first_name
        return JsonResponse({
            'success': True,
            'message': f'Добро пожаловать, {user.first_name}!'
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Неверный email или пароль'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при входе'
        })

def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/')  # если не авторизован

    user = get_object_or_404(CustomUser, id=user_id)
    bookings = user.booking_set.all().select_related('room__hotel').order_by('-created_at')
    today = timezone.now().date().isoformat()
    return render(request, 'host/profile.html', {
        'user': user,
        'bookings': bookings,
        'today': today
    })

def logout_user(request):
    request.session.flush()
    return redirect('/')

def index(request):
    today = timezone.now().date().isoformat()
    
    # Проверяем наличие отелей в базе
    has_hotels = Hotel.objects.exists()
    
    if not has_hotels:
        return render(request, 'host/index.html', {
            'today': today,
            'no_hotels': True
        })
    
    # Получаем топ 5 отелей с использованием values()
    top_hotels = list(Hotel.objects.filter(
    ~Q(rating__lt=2) & 
    (Q(location='Москва') | ~Q(photo='')) 
).values(
    'id', 'name', 'location', 'rating', 'description', 'photo'
).order_by('-rating')[:5])
    # Добавляем URL изображения для каждого отеля
    for hotel in top_hotels:
        if hotel['photo']:
            # Преобразуем путь к файлу в URL
            hotel['photo_url'] = os.path.join(settings.MEDIA_URL, str(hotel['photo']))
        hotel['rating_range'] = range(int(hotel['rating']))  # Для отображения звезд

    # Получаем список уникальных городов с помощью values_list
    cities = Hotel.objects.values_list('location', flat=True).distinct()
    
    # Получаем статистику по рейтингам отелей в каждом городе
    city_stats = Hotel.objects.values('location').annotate(
        avg_rating=Avg('rating'),
        hotel_count=Count('id')
    ).order_by('-avg_rating')

    # Получаем активные акции
    current_date = timezone.now().date()
    active_promotions = Promotion.objects.select_related('hotel').filter(
        start_date__lte=current_date,
        end_date__gte=current_date
    ).order_by('end_date')

    # Получаем топ отзывы (с рейтингом 4 или 5)
    top_reviews = Review.objects.select_related('hotel', 'user').filter(
    Q(rating__gte=4) &
    (Q(comment__isnull=False) | Q(rating__gt=4)) &
    ~Q(hotel__photo__isnull=True)
).order_by('-created_at')[:6]  # Последние 6 отзывов

    return render(request, 'host/index.html', {
        'today': today,
        'top_hotels': top_hotels,
        'cities': cities,
        'city_stats': city_stats,
        'has_hotels': has_hotels,
        'active_promotions': active_promotions,
        'top_reviews': top_reviews
    })

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    rooms = Room.objects.by_hotel(hotel).available().order_by_price().select_related('hotel')

    return render(request, 'host/hotel_detail.html', {
        'hotel': hotel,
        'rooms': rooms
    })

def custom_page_not_found_view(request, exception):
    print("⚠️  Кастомная 404 вызвана. Исключение:", exception)
    return render(request, '404.html', status=404)

def rooms_list(request):
    rooms = Room.objects.all().order_by('price_per_night')  # сортировка по возрастанию цены
    return render(request, 'host/hotel_detail.html', {'rooms': rooms})

def hotel_create(request):
    form = HotelForm(request.POST or None, request.FILES or None)
    next_url = request.GET.get('next', reverse('index'))

    if request.method == 'POST' and form.is_valid():
        # Получаем очищенные данные формы
        cleaned_data = form.cleaned_data
        name = cleaned_data.get('name')
        location = cleaned_data.get('location')
        print(f"Добавляется отель: {name}, город: {location}")

        form.save(commit=True)
        return redirect(next_url)

    return render(request, 'host/hotel_form.html', {'form': form, 'next': next_url})

def hotel_update(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    form = HotelForm(request.POST or None, request.FILES or None, instance=hotel)
    next_url = request.GET.get('next', reverse('index'))

    if request.method == 'POST' and form.is_valid():
        form.save(commit=True)
        return redirect(next_url)

    return render(request, 'host/hotel_form.html', {'form': form,'next': next_url})

def hotel_delete(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    next_url = request.GET.get('next', reverse('index'))

    if request.method == 'POST':
        hotel.delete()
        return redirect(next_url)

    return render(request, 'host/hotel_confirm_delete.html', {'hotel': hotel,'next': next_url})

def hotel_edit_amenities(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    form = HotelAmenityForm(instance=hotel)
    next_url = request.GET.get('next', reverse('index'))

    if request.method == 'POST':
        form = HotelAmenityForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(next_url)

    return render(request, 'host/hotel_amenity_form.html', {
        'form': form,
        'hotel': hotel,
        'next': next_url
    })

def user_bookings(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/')  # если не авторизован

    user = get_object_or_404(CustomUser, id=user_id)
    bookings = user.booking_set.all().select_related('room__hotel').order_by('-created_at')
    
    return render(request, 'host/user_bookings.html', {
        'user': user,
        'bookings': bookings
    })

def add_review(request, hotel_id):
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)
    
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=request.session['user_id'])
        hotel = get_object_or_404(Hotel, id=hotel_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating or not comment:
            return JsonResponse({'error': 'Заполните все поля'}, status=400)

        review = Review.objects.create(
            user=user,
            hotel=hotel,
            rating=rating,
            comment=comment
        )

        # Возвращаем данные для обновления на странице
        return JsonResponse({
            'id': review.id,
            'user_name': f"{user.first_name} {user.last_name}",
            'rating': review.rating,
            'comment': review.comment,
            'date': review.created_at.strftime("%d.%m.%Y")
        })

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def edit_review(request, review_id):
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)

    review = get_object_or_404(Review, id=review_id)
    
    # Проверяем, что отзыв принадлежит текущему пользователю
    if review.user.id != request.session['user_id']:
        return JsonResponse({'error': 'Нет прав на редактирование'}, status=403)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating or not comment:
            return JsonResponse({'error': 'Заполните все поля'}, status=400)

        review.rating = rating
        review.comment = comment
        review.save()

        return JsonResponse({
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'date': review.created_at.strftime("%d.%m.%Y")
        })

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def delete_review(request, review_id):
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)

    review = get_object_or_404(Review, id=review_id)
    
    # Проверяем, что отзыв принадлежит текущему пользователю
    if review.user.id != request.session['user_id']:
        return JsonResponse({'error': 'Нет прав на удаление'}, status=403)

    if request.method == 'POST':
        review.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@require_POST
def book_room(request, room_id):
    if not request.session.get('user_id'):
        return JsonResponse({
            'success': False,
            'message': 'Необходима авторизация'
        }, status=401)

    try:
        user = get_object_or_404(CustomUser, id=request.session['user_id'])
        room = get_object_or_404(Room, id=room_id)
        
        # Устанавливаем даты бронирования
        check_in = timezone.now().date()
        check_out = check_in + timezone.timedelta(days=1)
        
        # Рассчитываем итоговую стоимость
        days = (check_out - check_in).days
        final_price = room.price_per_night * days
        
        # Создаем бронирование
        booking = Booking.objects.create(
            user=user,
            room=room,
            check_in_date=check_in,
            check_out_date=check_out,
            final_price=final_price,
            status='pending'  # Статус "ожидает подтверждения"
        )

        return JsonResponse({
            'success': True,
            'message': 'Номер успешно забронирован',
            'booking_id': booking.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
