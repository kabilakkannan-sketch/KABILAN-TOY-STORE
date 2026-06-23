from django.db import models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Admin(models.Model):
    admin_name=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
class KYC(models.Model):
    user_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)
class Items(models.Model):
    toy_name = models.CharField(max_length=100)
    photo = models.FileField(upload_to='images/', null=True, blank=True)
    order_qty = models.CharField(max_length=100)
    old_price = models.CharField(max_length=10)
    new_price = models.CharField(max_length=10)
    offer = models.CharField(max_length=100)
    discription = models.CharField(max_length=1200)
    CATEGORY_CHOICES = [
        ('sports', 'Sports Toys'),
        ('ai', 'AI Toys'),
        ('sleeping', 'Sleeping Toys'),
        ('anime', 'Anime Toys'),
        ('robotic', 'Robotic Toys'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='sports')
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class Orders(models.Model):
    product_name = models.CharField(max_length=100)
    product_photo = models.FileField(upload_to='photo/', null=True, blank=True)
    order_quantity = models.CharField(max_length=100)
    user_quantity = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    user_id = models.IntegerField()
    status = models.CharField(max_length=50, default="Confirmed")
    action_status = models.CharField(
        max_length=20,
        choices=[('delivered','Delivered'),('cancelled','Cancelled'),('returned','Returned')],
        blank=True,
        default="")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)     
    combo_id = models.CharField(max_length=100, blank=True, null=True)
    @property
    def is_return_valid(self):
        if self.action_status == 'delivered' and self.delivered_at:
            return timezone.now() <= self.delivered_at + timedelta(days=10)
        return False
class ItemImages(models.Model):
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    image = models.FileField(upload_to='images/', null=True, blank=True)
class Cart(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    qty = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
class Wallet(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    user = models.OneToOneField(KYC, on_delete=models.CASCADE)
class ChatMessage(models.Model):
    user = models.ForeignKey(KYC, on_delete=models.CASCADE)
    product = models.ForeignKey(Items, on_delete=models.CASCADE)
    sender = models.CharField(
        max_length=10,
        choices=[
            ('user', 'User'),
            ('admin', 'Admin')
        ])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
class ProductReview(models.Model):
    order = models.OneToOneField(Orders, on_delete=models.CASCADE, related_name='review')    
    user = models.ForeignKey(KYC, on_delete=models.CASCADE)    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])    
    review_text = models.TextField(blank=True, null=True)    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order.id} - {self.rating} Stars"
