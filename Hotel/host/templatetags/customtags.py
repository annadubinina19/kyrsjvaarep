from django import template
from host.models import Room, Hotel

register = template.Library()

@register.simple_tag
def site_title():
    return "FunnyTravel"
@register.simple_tag(takes_context=True)
def user_greeting(context):
    user = context['request'].user
    if user.is_authenticated:
        return f"Добро пожаловать, {user.first_name or user.username}!"
    return "Добро пожаловать, гость!"
@register.filter
def currency_format(value):
    try:
        value = float(value)
        return f"{value:,.0f} ₽".replace(',', ' ')
    except (ValueError, TypeError):
        return value
@register.simple_tag
def get_rooms_by_hotel(hotel_id):
    return Room.objects.by_hotel(hotel_id).available().order_by_price()
@register.filter
def get_range(value):
    """
    Фильтр для создания диапазона чисел.
    Используется для отображения звезд рейтинга.
    """
    return range(value)