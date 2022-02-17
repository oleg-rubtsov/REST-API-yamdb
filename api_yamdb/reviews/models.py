from random import choice

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from api_yamdb.settings import ROLES
from .validators import (validate_username_me,
                         validate_year)
from .utils import Util

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'
CHOICES = (
    (USER, 'user'),
    (ADMIN, 'admin'),
    (MODERATOR, 'moderator')
)


class User(AbstractUser):
    username = models.CharField(validators=(validate_username_me,),
                                max_length=50, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(max_length=16, choices=CHOICES,
                            default=USER, blank=True)
    confirmation_code = models.IntegerField(default=0)

    @property
    def is_user(self):
        return self.role == ROLES['USER_ROLE']

    @property
    def is_admin(self):
        return self.role == ROLES['ADMIN_ROLE']

    @property
    def is_moderator(self):
        return self.role == ROLES['MODERATOR_ROLE']

    class Meta:
        ordering = ['-username', ]


@receiver(post_save, sender=User)
def post_save(sender, instance, created, **kwargs):
    if created:
        confirmation_code = choice(range(1000, 10000))
        instance.confirmation_code = confirmation_code
        instance.save()

        email_body = (f'Hi, {instance.username}. '
                      f'We have delivered confirmation code'
                      f' to you!\nYour code is: {confirmation_code}')
        data = {'email_body': email_body,
                'to_email': instance.email,
                'email_subject': 'That`s your code!'}

        Util.send_email(data)


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='category name')
    slug = models.SlugField(unique=True, verbose_name='category slug')

    class Meta:
        ordering = ['-name']
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200, verbose_name='genre name')
    slug = models.SlugField(unique=True, verbose_name='genre slug')

    class Meta:
        ordering = ['-name']
        verbose_name = 'genre'
        verbose_name_plural = 'genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='title name',
        db_index=True
    )
    year = models.IntegerField(
        validators=[validate_year],
        default=0,
        verbose_name='year of creation',
        db_index=True
    )
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='category'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,
        verbose_name='genre'
    )

    class Meta:
        ordering = ['-name']
        verbose_name = 'title'
        verbose_name_plural = 'titles'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.CharField(max_length=200)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        error_messages={'validators': 'Оценка по 10-бальной шкале!'})
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='author title')]
        ordering = ['-score', 'pub_date']

    def __str__(self):
        return self.text


class Comments(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.CharField(max_length=200)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date', ]
