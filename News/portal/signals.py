from .models import Post, Category
from django.db.models.signals import post_save
from django.dispatch import receiver  # импортируем нужный декоратор
from django.core.mail import mail_managers
from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
# from django.db.models.signals import ModelSignal
# from .views import custom_create_signal


# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    # if instance.postCategory:
    if instance.postCategory.first():
        print(instance.postCategory.first())

        cat = instance.postCategory.first()
        subscribers = cat.subscribers.all()
        subscribers_emails = cat.subscribers.all().values('email')
        subscribers_names = cat.subscribers.all().values('username')

        print(subscribers_emails)
        print(subscribers_names)

        # user_emails = []
        # for user in category.subscribers.all():
        #         user_emails.append(user.email)

        user_emails = []
        user_names = []

        for subscriber in subscribers:
            user_emails.append(subscriber.email)
            user_names.append(subscriber.username)

            if created:
                subject = f'{subscriber.username}, новая публикация - {instance.postTitle}, в разделе {instance.postCategory.first()} ... {instance.pubDate.strftime("%d %m %Y")}'
            else:
                subject = f'{subscriber.username}, новая публикация - {instance.postTitle}, в разделе {instance.postCategory.first()} ... {instance.pubDate.strftime("%d %m %Y")}'

            msg = EmailMultiAlternatives(
                subject=subject,
                body=f'Привет {subscriber.username}, новая публикация - {instance.postTitle}, в разделе {instance.postCategory.first()}',  # это то же, что и message
                from_email='subscribecategory@yandex.ru',
                to=[f'{subscriber.email}'],  # это то же, что и recipients_list
            )

            # получаем наш html
            html_content = render_to_string(
                'post_created.html',
                {
                    'post': instance,
                    'user': subscriber.username,
                }
            )

            msg.attach_alternative(html_content, "text/html")  # добавляем html

            msg.send()  # отсылаем

            print(subject)



        print(user_emails)
        print(user_names)