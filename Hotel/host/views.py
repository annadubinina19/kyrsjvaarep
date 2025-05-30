from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Count
from .models import User 
from .models import Hotel,Room,HotelAmenity
from django.utils import timezone
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from .forms import HotelForm
from .forms import HotelAmenityForm
from django.db.models import Prefetch
from django.urls import reverse
from django.http import HttpResponse


def index(request):
    return render(request, 'host/index.html')
# Create your views here.
def search(request):
    location = request.GET.get('location', '').strip()
    check_in = request.GET.get('check_in')
    sort_by = request.GET.get('sort_by')
    today = timezone.now().date().isoformat()
    hotels = Hotel.objects.prefetch_related(
        Prefetch('hotelamenity_set', queryset=HotelAmenity.objects.select_related('amenity'))
    )
    hotels = []
    hotel_count = 0

    if location:
        hotels = Hotel.objects.filter(location__icontains=location).annotate(room_count=Count('rooms'))
        
        if sort_by in ['rating', '-rating' , 'room_count', '-room_count']:
            hotels = hotels.order_by(sort_by)
        hotel_count = hotels.count()
        paginator = Paginator(hotels, 1)  # по 3 отеля на страницу
        page_number = request.GET.get('page', 1)
        try:
            hotels = paginator.page(page_number)
        except PageNotAnInteger:
            hotels = paginator.page(1)
        except EmptyPage:
            hotels = paginator.page(paginator.num_pages)
    return render(request, 'host/search.html', {
        'hotels': hotels,
        'hotel_count': hotel_count,
        'location': location,
        'check_in': check_in,
        'sort_by': sort_by,
        'today': today
    })
 # Импортируйте свою модель пользователя

def register_user(request):
    if request.method == "POST":
        last_name = request.POST['last_name']
        first_name = request.POST['first_name']
        email = request.POST['email']
        password = request.POST['password']
        phone_number = request.POST['phone_number']

        # Сохраняем пользователя с ролью "гость"
        User.objects.create(
            last_name=last_name,
            first_name=first_name,
            email=email,
            password=password,
            phone_number=phone_number,
            role='гость'
        )
        return redirect('/')  # или вернуть JSON в случае Ajax
    return redirect('/')    
def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            request.session['user_name'] = user.first_name
            return redirect('profile')  # перенаправление на личный кабинет
        except User.DoesNotExist:
            return render(request, 'host/login_error.html', {'error': 'Неверный email или пароль'})

    return redirect('/')
def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/')  # если не авторизован

    user = get_object_or_404(User, id=user_id)
    today = timezone.now().date().isoformat()
    return render(request, 'host/profile.html', {'user': user, 'today': today})
def logout_user(request):
    request.session.flush()
    return redirect('/')

def index(request):
    today = timezone.now().date().isoformat()
    return render(request, 'host/index.html', {'today': today})


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
        form.save(commit=True)
        return redirect(next_url)

    return render(request, 'host/hotel_form.html', {'form': form,'next': next_url})


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
            return redirect(next_url)

    return render(request, 'host/hotel_amenity_form.html', {
        'form': form,
        'hotel': hotel,
        'next': next_url
    })
