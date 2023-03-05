from django.http import HttpResponse
from django.views import View

from .tasks import subscribe_category_confirmation_message

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models.signals import ModelSignal
from django.shortcuts import render, redirect
from django.template.defaultfilters import truncatechars
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.core.paginator import Paginator  # импортируем класс, позволяющий удобно осуществлять постраничный вывод
from django.contrib.auth.models import User
from datetime import datetime

from .models import Author, Category, Post, PostCategory, Comment
from .filters import PostFilter  # импортируем недавно написанный фильтр
from .forms import PostForm  # импортируем нашу форму

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from django.contrib.auth.mixins import PermissionRequiredMixin

from django.core.cache import cache


# дженерик для редактирования объекта
class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'news/post_create.html'
    permission_required = ('news.change_post',)
    form_class = PostForm

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        post = Post.objects.get(pk=id)
        post.isUpdated = True
        return post

    def form_valid(self, form):
        self.object = form.save()  # вызван save() значит отправляется сигнал без категории
        cat = Category.objects.get(pk=self.request.POST['postCategory'])
        self.object.postCategory.add(cat)  # добавляем категорию
        return super().form_valid(form)  # у родителя еще раз вызывается метод save(), вторая отправка сигнала.


class PostsList(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'news'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    ordering = ['-pubDate']  # вывод списка публикаций в обратном порядке, от более новых к более старым
    paginate_by = 10  # поставим постраничный вывод в один элемент

    # метод get_context_data нужен нам для того, чтобы мы могли передать переменные в шаблон. В возвращаемом словаре context будут храниться все переменные. Ключи этого словаря и есть переменные, к которым мы сможем потом обратиться через шаблон
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()  # добавим переменную текущей даты time_now
        context[
            'news_list'] = Post.objects.all()  # добавим переменную всего списка публикаций, не подверженного эффекту пагинации
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


# дженерик для получения деталей о товаре
class PostDetailView(DetailView):
    template_name = 'news/post_detail.html'
    queryset = Post.objects.all()


# дженерик для создания объекта. Надо указать только имя шаблона и класс формы, который мы написали в прошлом юните. Остальное он сделает за вас
class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'news/post_create.html'
    permission_required = ('news.add_post',)
    form_class = PostForm  # добавляем форм класс, чтобы получать доступ к форме через метод POST

    def form_valid(self, form):
        self.object = form.save()  # вызван save() значит отправляется сигнал без категории
        cat = Category.objects.get(pk=self.request.POST['postCategory'])
        self.object.postCategory.add(cat)  # добавляем категорию
        return super().form_valid(form)  # у родителя еще раз вызывается метод save(), вторая отправка сигнала.

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     # self.object.author = Author.objects.get(authorUsername=self.request.user)
    #     self.object.save()
    #
    #     cat = Category.objects.get(pk=self.request.POST['category'])
    #     self.object.postCategory.add(cat)
    #     custom_create_signal.send(sender=Post, instance=self.object, created=True, request=self.request)
    #
    #     validated = super().form_valid(form)
    #     return validated


# дженерик для удаления поста
class PostDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'news/post_delete.html'
    permission_required = ('news.delete_post',)
    queryset = Post.objects.all()
    success_url = '/news/'


class SearchList(ListView):
    model = Post
    template_name = 'news/news_search.html'
    context_object_name = 'news'
    ordering = ['-pubDate']
    paginate_by = 10  # поставим постраничный вывод в 10 элементов

    def get_filter(self):
        return PostFilter(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()  # добавим переменную текущей даты time_now
        context[
            'news_list'] = Post.objects.all()  # добавим переменную всего списка публикаций, не подверженного эффекту пагинации
        context['filter'] = self.get_filter()
        context['categories'] = Category.objects.all()
        return context


class CategorySubscribeView(ListView):
    model = Category
    template_name = 'news/post_category.html'
    context_object_name = 'post_category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
def subscribe_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    id_u = request.user.id
    email = category.subscribers.get(id=id_u).email
    user_name = request.user.username
    category_name = Category.objects.get(id=pk).categoryName

    subscribe_category_confirmation_message.delay(user_name, email, category_name)

    #     send_mail(
    #         subject=f'News Portal: подписка на обновления категории {category}',
    #         message=f'«{request.user}», вы подписались на обновление категории: «{category}».',
    #         from_email='example@yandex.ru',
    #         recipient_list=[f'{email}', ],
    #     )
    return redirect('/news')
