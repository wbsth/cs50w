from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class AuctionListening(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=6)
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, default=None, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title




