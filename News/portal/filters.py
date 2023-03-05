from django_filters import FilterSet, CharFilter, ModelChoiceFilter, \
    DateFromToRangeFilter
from .models import Author, Category, Post, PostCategory, Comment

from django.contrib.auth.models import User


# создаём фильтр
class PostFilter(FilterSet):
    pubDate = DateFromToRangeFilter(label='Dates From To Range')

    # Здесь в мета классе надо предоставить модель и указать поля, по которым будет фильтроваться (т. е. подбираться) информация о товарах
    class Meta:
        model = Post
        # fields = ('author', 'postTitle', 'pubDate')  # поля, которые мы будем фильтровать (т. е. отбирать по каким-то критериям, имена берутся из моделей)
        fields = {
            # 'pubDate': ['gt', 'lt'],  # дата должна быть позже той, что указал пользователь
            'postTitle': ['icontains'],  # по названию публикации
            'author': ['exact'],  # по имени пользователя автора (выбор из существуещего списка)
            'postCategory': ['exact'],  # по категории
        }
