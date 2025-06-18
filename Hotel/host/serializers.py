from rest_framework import serializers
from .models import (
    User, Hotel, Amenity, HotelAmenity, Room, Review, 
    Promotion, HotelService, Booking, Payment
)
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'last_name', 'first_name', 'email', 'phone_number', 'role']
        read_only_fields = ['id']


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'description']


class HotelAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer(read_only=True)
    amenity_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = HotelAmenity
        fields = ['id', 'hotel', 'amenity', 'amenity_id']


class HotelServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelService
        fields = ['id', 'hotel', 'service_name', 'price', 'description']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = ['id', 'hotel', 'user', 'user_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']


class HotelSerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True, read_only=True)
    services = HotelServiceSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'location', 'rating', 'description', 
            'contact_info', 'website', 'booking_url', 'photo', 
            'created_at', 'amenities', 'services', 'reviews',
            'average_rating', 'reviews_count'
        ]
        read_only_fields = ['created_at']

    def get_average_rating(self, obj):
        reviews = obj.review_set.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_reviews_count(self, obj):
        return obj.review_set.count()


class RoomSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)
    hotel_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'hotel', 'hotel_id', 'room_type', 'price_per_night',
            'max_guests', 'availability', 'photo'
        ]


class PromotionSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)
    hotel_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Promotion
        fields = [
            'id', 'hotel', 'hotel_id', 'title', 'description',
            'start_date', 'end_date', 'details_url', 'booking_url'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'payment_method', 'amount', 'date']
        read_only_fields = ['date']


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    room = RoomSerializer(read_only=True)
    room_id = serializers.IntegerField(write_only=True)
    payments = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_id', 'room', 'room_id',
            'check_in_date', 'check_out_date', 'final_price',
            'status', 'created_at', 'confirmation_pdf',
            'payments', 'total_paid'
        ]
        read_only_fields = ['created_at', 'confirmation_pdf']

    def get_payments(self, obj):
        payments = obj.payment_set.all()
        return PaymentSerializer(payments, many=True).data

    def get_total_paid(self, obj):
        return sum(payment.amount for payment in obj.payment_set.all())

    def validate(self, data):
        """
        Проверка дат бронирования
        """
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        
        if check_in and check_out and check_in >= check_out:
            raise serializers.ValidationError(
                "Дата выезда должна быть позже даты заезда"
            )
        
        return data


# Сериализаторы для создания объектов
class HotelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = [
            'name', 'location', 'rating', 'description',
            'contact_info', 'website', 'booking_url', 'photo'
        ]


class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'hotel', 'room_type', 'price_per_night',
            'max_guests', 'availability', 'photo'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'room', 'check_in_date', 'check_out_date',
            'final_price', 'status'
        ]
    

        

# Сериализаторы для статистики
class HotelStatsSerializer(serializers.ModelSerializer):
    total_rooms = serializers.SerializerMethodField()
    available_rooms = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'total_rooms', 'available_rooms',
            'total_bookings', 'revenue'
        ]

    def get_total_rooms(self, obj):
        return obj.rooms.count()

    def get_available_rooms(self, obj):
        return obj.rooms.filter(availability=True).count()

    def get_total_bookings(self, obj):
        return Booking.objects.filter(room__hotel=obj).count()

    def get_revenue(self, obj):
        bookings = Booking.objects.filter(room__hotel=obj, status='completed')
        return sum(booking.final_price for booking in bookings) 