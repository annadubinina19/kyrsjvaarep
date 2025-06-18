from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    User, Hotel, Amenity, HotelAmenity, Room, Review, 
    Promotion, HotelService, Booking, Payment
)
from .serializers import (
    UserSerializer, HotelSerializer, AmenitySerializer, HotelAmenitySerializer,
    RoomSerializer, ReviewSerializer, PromotionSerializer, HotelServiceSerializer,
    BookingSerializer, PaymentSerializer, HotelStatsSerializer
)
from .filters import HotelFilter, RoomFilter, BookingFilter, ReviewFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role']
    search_fields = ['last_name', 'first_name', 'email']
    ordering_fields = ['last_name', 'first_name']

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """Получить все бронирования пользователя"""
        user = self.get_object()
        bookings = Booking.objects.filter(user=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Получить все отзывы пользователя"""
        user = self.get_object()
        reviews = Review.objects.filter(user=user)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HotelFilter
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['name', 'rating', 'created_at']

    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        """Получить все номера отеля"""
        hotel = self.get_object()
        rooms = hotel.rooms.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def available_rooms(self, request, pk=None):
        """Получить доступные номера отеля"""
        hotel = self.get_object()
        rooms = hotel.rooms.filter(availability=True)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def promotions(self, request, pk=None):
        """Получить все акции отеля"""
        hotel = self.get_object()
        promotions = hotel.promotion_set.all()
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        """Получить все услуги отеля"""
        hotel = self.get_object()
        services = hotel.hotelservice_set.all()
        serializer = HotelServiceSerializer(services, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Получить статистику отеля"""
        hotel = self.get_object()
        serializer = HotelStatsSerializer(hotel)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Получить топ отелей по рейтингу"""
        hotels = Hotel.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10]
        serializer = HotelSerializer(hotels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """Получить отели по местоположению"""
        location = request.query_params.get('location', '')
        if location:
            hotels = Hotel.objects.filter(location__icontains=location)
            serializer = HotelSerializer(hotels, many=True)
            return Response(serializer.data)
        return Response({'error': 'Location parameter is required'}, status=400)


class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RoomFilter
    search_fields = ['hotel__name']
    ordering_fields = ['price_per_night', 'max_guests']

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Получить все доступные номера"""
        rooms = Room.objects.filter(availability=True)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_price_range(self, request):
        """Получить номера по диапазону цен"""
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        queryset = Room.objects.all()
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
            
        serializer = RoomSerializer(queryset, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'rating']

    def perform_create(self, serializer):
        # Принудительно загружаем пользователя, чтобы избежать SimpleLazyObject
        user = User.objects.get(id=self.request.user.id)
        serializer.save(user=user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Получить последние отзывы"""
        reviews = Review.objects.order_by('-created_at')[:10]
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['hotel']
    search_fields = ['title', 'description']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить активные акции"""
        today = timezone.now().date()
        promotions = Promotion.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        )
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)


class HotelServiceViewSet(viewsets.ModelViewSet):
    queryset = HotelService.objects.all()
    serializer_class = HotelServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['hotel']
    search_fields = ['service_name', 'description']


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = BookingFilter
    ordering_fields = ['created_at', 'check_in_date', 'final_price']

    def perform_create(self, serializer):
        # Принудительно загружаем пользователя, чтобы избежать SimpleLazyObject
        user = User.objects.get(id=self.request.user.id)
        serializer.save(user=user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Подтвердить бронирование"""
        booking = self.get_object()
        booking.status = 'confirmed'
        booking.save()
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отменить бронирование"""
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.save()
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Получить предстоящие бронирования"""
        today = timezone.now().date()
        # Принудительно загружаем пользователя, чтобы избежать SimpleLazyObject
        user = User.objects.get(id=request.user.id)
        bookings = Booking.objects.filter(
            user=user,
            check_in_date__gte=today,
            status='confirmed'
        ).order_by('check_in_date')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user_bookings(self, request):
        """Получить бронирования текущего пользователя"""
        # Принудительно загружаем пользователя, чтобы избежать SimpleLazyObject
        user = User.objects.get(id=request.user.id)
        bookings = Booking.objects.filter(user=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['booking', 'payment_method']
    ordering_fields = ['date', 'amount']

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Получить платежи по диапазону дат"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = Payment.objects.all()
        if start_date:
            queryset = queryset.filter(date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__date__lte=end_date)
            
        serializer = PaymentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def total_revenue(self, request):
        """Получить общую выручку"""
        total = Payment.objects.aggregate(total=Sum('amount'))
        return Response({'total_revenue': total['total'] or 0}) 