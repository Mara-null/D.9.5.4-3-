from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        author_posts_rating = Post.objects.filter(author_id=self.pk).aggregate(
            post_rating_sum=Coalesce(Sum('rating_post') * 3, 0))
        author_comments_rating = Comment.objects.filter(user_id=self.user).aggregate(
            comments_rating_sum=Coalesce(Sum('rating_comment'), 0))
        author_posts_comments_rating = Comment.objects.filter(post__author__name=self.user).aggregate(
            comments_rating_sum=Coalesce(Sum('rating_comment'), 0))

        self.rating = author_posts_rating['post_rating_sum'] * 3 + author_comments_rating['comments_rating_sum'] + author_posts_comments_rating['comments_rating_sum']
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=55, unique=True)
    subscribers = models.ManyToManyField(User, blank=True, null=True, related_name='categories')

    def __str__(self):
        return self.name


class Post(models.Model):
    article = 'AT'
    news = 'NW'

    POST_TYPE = [
        (article, 'Статья'),
        (news, 'Новости'),
    ]

    post_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    post_type = models.CharField(max_length=2, choices=POST_TYPE, default=news)
    rating = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, through='PostCategory')


    def like(self):
        self.rating += 1
        self.save()
        self.author.update.rating()

    def dislike(self):
        self.rating += 1
        self.save()
        self.author.update.rating()

    def preview(self):
        if len(self.text) > 124:
            prev = self.text[124] + '...'
        else:
            prev = self.text

        print(prev)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/news/{self.id}'

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rating += 1
        self.save()
        self.author.update.rating()

    def dislike(self):
        self.rating += 1
        self.save()
        self.author.update.rating()

