from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import ManyToManyField


class User(AbstractUser):
    followers = ManyToManyField('self', symmetrical=False, blank=True, related_name='following')


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=280)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = ManyToManyField(User, blank=True, related_name='liked')

    def __str__(self):
        return f'{self.id}: {self.poster}'

    def serialize(self):
        return {
            "id": self.id,
            "poster": self.poster.username,
            "poster_id": self.poster.id,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes_count": self.likes.count()
        }
