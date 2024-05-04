from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class all_listings(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    startingbid = models.IntegerField()
    currentprice = models.IntegerField()
    category = models.CharField(max_length=64)
    imageurl = models.CharField(max_length=255)
    image = models.ImageField(upload_to='commerce/auctions/static/auctions/',default='default_image.png')
    creation_time = models.DateTimeField(default=timezone.now, verbose_name='creation time')
    bid_counter = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    winner = models.CharField(max_length=100, blank=True, null=True)     

    def __str__(self):
        return f"{self.title} {self.description} by {self.user.username}"

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watchlist_counter = models.IntegerField(default=0, blank=True)
    watchlist_items = models.ManyToManyField(all_listings, related_name='watchlist_items', blank=True)
    
    def __str__(self):
        return f"Watchlist for {self.user.username} "

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creation_time = models.DateTimeField(auto_now=True)
    auction = models.ForeignKey(all_listings, on_delete=models.CASCADE)
  
    def __str__(self):
        return f'{self.amount} on {self.auction} by {self.user.username}'
    
class Price(models.Model):
    item = models.ForeignKey(all_listings, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'Amount: {self.amount}'
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(all_listings, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}: {self.text}'