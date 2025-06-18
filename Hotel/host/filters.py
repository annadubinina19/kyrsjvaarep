import django_filters
from django_filters import rest_framework as filters
from .models import Hotel, Room, Booking, Review


class HotelFilter(filters.FilterSet):
    min_rating = filters.NumberFilter(field_name="rating", lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name="rating", lookup_expr='lte')
    location = filters.CharFilter(lookup_expr='icontains')
    has_amenities = filters.BooleanFilter(method='filter_has_amenities')
    
    class Meta:
        model = Hotel
        fields = {
            'name': ['icontains'],
            'location': ['icontains'],
            'rating': ['exact', 'gte', 'lte'],
        }
    
    def filter_has_amenities(self, queryset, name, value):
        if value:
            return queryset.filter(amenities__isnull=False).distinct()
        return queryset


class RoomFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price_per_night", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price_per_night", lookup_expr='lte')
    min_guests = filters.NumberFilter(field_name="max_guests", lookup_expr='gte')
    hotel_name = filters.CharFilter(field_name="hotel__name", lookup_expr='icontains')
    
    class Meta:
        model = Room
        fields = {
            'hotel': ['exact'],
            'room_type': ['exact'],
            'availability': ['exact'],
            'price_per_night': ['exact', 'gte', 'lte'],
            'max_guests': ['exact', 'gte', 'lte'],
        }


class BookingFilter(filters.FilterSet):
    check_in_after = filters.DateFilter(field_name="check_in_date", lookup_expr='gte')
    check_in_before = filters.DateFilter(field_name="check_in_date", lookup_expr='lte')
    check_out_after = filters.DateFilter(field_name="check_out_date", lookup_expr='gte')
    check_out_before = filters.DateFilter(field_name="check_out_date", lookup_expr='lte')
    min_price = filters.NumberFilter(field_name="final_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="final_price", lookup_expr='lte')
    
    class Meta:
        model = Booking
        fields = {
            'user': ['exact'],
            'room': ['exact'],
            'status': ['exact'],
            'check_in_date': ['exact', 'gte', 'lte'],
            'check_out_date': ['exact', 'gte', 'lte'],
            'final_price': ['exact', 'gte', 'lte'],
        }


class ReviewFilter(filters.FilterSet):
    min_rating = filters.NumberFilter(field_name="rating", lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name="rating", lookup_expr='lte')
    hotel_name = filters.CharFilter(field_name="hotel__name", lookup_expr='icontains')
    
    class Meta:
        model = Review
        fields = {
            'hotel': ['exact'],
            'user': ['exact'],
            'rating': ['exact', 'gte', 'lte'],
            'created_at': ['exact', 'gte', 'lte'],
        } 