import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Модель Author
class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    authorRating = models.SmallIntegerField("рейтинг автора", default=0)

    def __str__(self):
        # return self.commentPost.author.authorUser.username  # получить имя автора поста
        return f'{self.authorUser.username}'

    def update_rating(self):
        postRat = self.post_set.aggregate(postRating=Sum('rating'))
        pRat = 0
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating'))
        cRat = 0
        cRat += commentRat.get('commentRating')

        self.authorRating = pRat * 3 + cRat
        self.save()


# Модель Category
class Category(models.Model):
    categoryName = models.CharField('Выберите категорию публикаций для подписки:', max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscriber', blank=True)

    def __str__(self):
        return f'{self.categoryName}'


# Модель Post
class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORIES = [
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья')
    ]
    categoryType = models.CharField(max_length=2,
                                    choices=CATEGORIES,
                                    default=ARTICLE)
    pubDate = models.DateTimeField('Publication date ', auto_now_add=True)
    postCategory = models.ManyToManyField(Category, through='postCategory')
    postTitle = models.CharField('Title ', max_length=128)
    postText = models.TextField('Text')
    rating = models.SmallIntegerField("рейтинг статьи/новости", default=0)
    isUpdated = models.BooleanField(default=False)

    # Методы like() и dislike() в модели Post, которые увеличивают/уменьшают рейтинг на единицу.
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    # Метод preview() модели Post, который возвращает начало статьи (предварительный просмотр)
    # длиной 124 символа и добавляет многоточие в конце.
    def preview(self):
        return f'{self.postText[:124]} ...'

    def __str__(self):
        # получить название поста
        return f'{self.postTitle}. {self.postText[:124]} ...'

    def get_category(self):
        return f'{self.postCategory}'

    def get_absolute_url(self):
        return f'http://127.0.0.1:8000/news/{self.id}'
        # return f'/news/{self.id}'

    def message_subscriber(self):
        return f'Новая статья - "{self.postTitle}" в разделе "{self.postCategory.first()}" '


# Модель PostCategory
# Промежуточная модель для связи «многие ко многим»:
class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        # получить название поста
        return f'{self.postThrough}. {self.categoryThrough}'


# Модель Comment
class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    commentText = models.CharField('текст комментария', max_length=200)
    pubDate = models.DateTimeField('дата и время публикации комментария', auto_now_add=True)
    rating = models.SmallIntegerField("рейтинг комментария", default=0)

    # Метод __str__ выводит фамилию автора комментария
    def __str__(self):
        # return self.commentPost.author.authorUser.username  # получить имя автора поста
        return f'{self.commentUser.username}'

    # Методы like() и dislike() в модели Comment, которые увеличивают/уменьшают рейтинг на единицу.
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
