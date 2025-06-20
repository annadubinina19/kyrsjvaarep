# forms.py
from django import forms
from .models import Hotel,HotelAmenity
from django.core.exceptions import ValidationError

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'location', 'rating', 'description', 'contact_info', 'photo']
        exclude = ['created_at']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название отеля',
                'required': True,
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город или адрес'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание отеля'
            }),
            'contact_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Телефон / Email / Адрес'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

        help_texts = {
            'name': 'Введите название отеля (минимум 3 символа)',
            'rating': 'Выберите рейтинг от 1 до 5',
            'photo': 'Загрузите фотографию отеля в формате jpg, png и т.д.',
        }

        error_messages = {
            'name': {
                'required': 'Название отеля обязательно для заполнения',
                'max_length': 'Название слишком длинное',
            },
            'rating': {
                'invalid_choice': 'Выберите корректный рейтинг',
                'required': 'Рейтинг обязателен',
            },
        }
    class Media:
        css = {
            'all': ('css/hotel.css',)  # путь к вашему CSS файлу в static
        }
          
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError("Название должно содержать минимум 3 символа")
        return name    
from django import forms
from .models import Hotel, Amenity

class HotelAmenityForm(forms.ModelForm):
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Выберите удобства"
    )

    class Meta:
        model = Hotel
        fields = ['amenities']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['amenities'].initial = self.instance.amenities.all()

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
        
        # Сохраняем связь ManyToMany
        amenities = self.cleaned_data['amenities']
        HotelAmenity.objects.filter(hotel=instance).delete()

        for amenity in amenities:
            HotelAmenity.objects.create(hotel=instance, amenity=amenity)

        return instance    