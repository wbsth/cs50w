from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, blank=True)

    def count_followers(self):
        return self.followers.count()

    def count_following(self):
        return User.objects.filter(followers=self).count()


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    addedOn = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=3000)

    class Meta:
        ordering = ['-addedOn']
