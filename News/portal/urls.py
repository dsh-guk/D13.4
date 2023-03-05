from django.urls import path
from .views import PostsList, SearchList, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, \
    CategorySubscribeView, subscribe_category


urlpatterns = [
    # path — означает путь. В данном случае путь ко всем товарам у нас останется пустым, позже станет ясно, почему
    path('', PostsList.as_view(), name='news'),
    path('search/', SearchList.as_view()),
    # т. к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого вызываем метод as_view
    # path('<int:pk>', PostDetail.as_view()),  # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),  # Ссылка на детали публикации
    path('create/', PostCreateView.as_view(), name='post_create'),  # Ссылка на создание публикации
    path('create/<int:pk>', PostUpdateView.as_view(), name='post_update'),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
    path('category/', CategorySubscribeView.as_view()),
    path('category/<int:pk>', subscribe_category, name='subscribe_category'),

]
