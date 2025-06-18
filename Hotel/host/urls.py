from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_user, name='logout_user'),
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('hotel/add/', views.hotel_create, name='hotel_create'),
    path('hotel/<int:pk>/edit/', views.hotel_update, name='hotel_update'),
    path('hotel/<int:pk>/delete/', views.hotel_delete, name='hotel_delete'),
    path('hotel/<int:hotel_id>/edit-amenities/', views.hotel_edit_amenities, name='hotel_edit_amenities'),
    path('my-bookings/', views.user_bookings, name='user_bookings'),
    path('add_review/<int:hotel_id>/', views.add_review, name='add_review'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('book-room/<int:room_id>/', views.book_room, name='book_room'),
]



