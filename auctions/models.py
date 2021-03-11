from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    size = models.CharField(max_length=10, blank=True)
    price = models.PositiveSmallIntegerField()
    highestbid = models.PositiveSmallIntegerField(blank=True)
    photo_url = models.URLField(max_length=500, blank=True, default="https://images.unsplash.com/photo-1517502166878-35c93a0072f0?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=934&q=80")
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=False)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    NEUTRAL = 'NRL'
    WOMEN = 'WMN'
    MEN = 'MEN'
    GENDER_CHOICES = [
        (NEUTRAL, 'Neutral'),
        (WOMEN, 'Women'),
        (MEN, 'Men')
    ]
    gender = models.CharField(max_length=3, choices=GENDER_CHOICES, blank=True)
    UNKNOWN = 'UNK'
    ACCESSORIES = 'AC'
    TOPS = 'TPS'
    JACKETS = 'JKT'
    SWEATERS = 'SWT'
    SHIRTS = 'SRT'
    SUITS = 'ST'
    DRESSES = 'DRS'
    PANTS = 'PN'
    JEANS = 'JN'
    SHORTS = 'SHR'
    SWIM = 'SWM'
    SHOES = 'SHO'
    CATEGORY_CHOICES = [
        (UNKNOWN, 'Unknown'),
        (ACCESSORIES, 'Accessories'),
        (TOPS, 'Tops'),
        (JACKETS, 'Jackets'),
        (SWEATERS, 'Sweaters'),
        (SHIRTS, 'Shirts'),
        (SUITS, 'Suits'),
        (DRESSES, 'Dresses'),
        (PANTS, 'Pants'),
        (JEANS, 'Jeans'),
        (SHORTS, 'Shorts'),
        (SWIM, 'Swim'),
        (SHOES, 'Shoes'),
    ]
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES, blank=True)

    def __str__(self):
        return f"{self.user.username} created listing for '{self.title}' at ${self.price}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.PositiveSmallIntegerField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")

    def __str__(self):
        return f"{self.user.username} placed bid for ${self.offer} for '{self.listing.title}'"

class Comments(models.Model):
    comment = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")

    def __str__(self):
        return f"{self.user.username} wrote '{self.comment}'' on {self.listing.title}"