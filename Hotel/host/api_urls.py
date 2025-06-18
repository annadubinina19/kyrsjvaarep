from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    UserViewSet, HotelViewSet, AmenityViewSet, RoomViewSet,
    ReviewViewSet, PromotionViewSet, HotelServiceViewSet,
    BookingViewSet, PaymentViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'hotels', HotelViewSet)
router.register(r'amenities', AmenityViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'promotions', PromotionViewSet)
router.register(r'services', HotelServiceViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 