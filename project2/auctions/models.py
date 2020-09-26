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
    starting_bid = models.DecimalField(decimal_places=2, max_digits=8)
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, default=None, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_price = models.DecimalField(decimal_places=2, max_digits=8)
    active = models.BooleanField(default=True)
    favoured = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_favoured", blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.current_price = self.starting_bid
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Bid(models.Model):
    auction = models.ForeignKey(AuctionListening, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount = models.DecimalField(decimal_places=2, max_digits=8)

    def __str__(self):
        return f"{self.amount} bid on {self.auction} by {self.user}"


class Comment(models.Model):
    auction = models.ForeignKey(AuctionListening, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"{self.user} comment on {self.auction}"
