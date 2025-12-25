from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 10}
            ),
            'pub_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'pub_date': 'Дата и время публикации',
            'location': 'Местоположение',
            'category': 'Категория',
            'image': 'Изображение',
            'is_published': 'Опубликовать',
        }
        help_texts = {
            'is_published': 'Снимите галочку, чтобы сохранить пост как черновик',
        }
    
    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        if pub_date:
            if timezone.is_naive(pub_date):
                pub_date = timezone.make_aware(pub_date, timezone.get_current_timezone())
            
            # Проверяем только при создании нового поста (не при редактировании)
            if not self.instance.pk:
                current_time = timezone.now()
                three_days_ago = current_time - timezone.timedelta(days=3)
                
                if pub_date < three_days_ago:
                    raise forms.ValidationError(
                        'Дата публикации не может быть старше 3 дней. '
                        'Пожалуйста, выберите дату не ранее чем 3 дня назад.'
                    )
        return pub_date


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
