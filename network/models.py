from time import time
from django.contrib.auth.models import AbstractUser


from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True)
    like_num = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.pk}: {self.text} -like_num:{self.like_num}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='posts')
    
    def __str__(self):
        return f"{self.pk} {self.user}: {self.post.text}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings')

    def __str__(self):
        return f"{self.pk} {self.follower}: {self.following}"
        
