from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import ForeignKey


class User(AbstractUser):
    pass

class UserFollow(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete = models.CASCADE, related_name='follower')

class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    edited = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id":self.id,
            "poster":self.poster.username,
            "content":self.content,
            "timestamp":self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes":self.likes,
            "edited":self.edited
        }

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='liked_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")