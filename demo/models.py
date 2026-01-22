from django.db import models
from django.contrib.auth.models import User
# Create your models here.




class customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    profile_pic = models.ImageField(default="profile.jpg", null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class company(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

class product(models.Model):
    CATEGORY = (
    ('carbonated', 'Carbonated Drinks'),
    ('juice', 'Natural Juices'),
    ('water', 'Bottled Water'),
    ('energy', 'Energy Drinks'),
)

    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    company = models.ManyToManyField(company, blank=True)
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(null=True)
    litre = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, default='defualt.jpeg') 
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    

    def __str__(self):
        return self.name

class order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    )

    customer = models.ForeignKey(customer, null=True, blank=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(product, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.CharField(max_length=200, null=True,default="1")
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200, null=True, blank=True, choices=STATUS)

    def __str__(self):
        return self.product.name if self.product else f"Order #{self.id}"