from django.db import models
import uuid

from django.contrib.auth.models import (AbstractBaseUser, AbstractUser, Group,
                                        Permission, PermissionsMixin)

class Timestamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(AbstractBaseUser, PermissionsMixin, Timestamps):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, null=False, blank=False, default="")
    phone = models.CharField(max_length=50, null=False, blank=False, unique=True, default="", db_index=True)
    email = models.EmailField(null=False, blank=False, unique=True, default="")
    username = models.CharField(null=True, blank=True, default=None, max_length=20)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['phone', 'email', 'name']
    def __str__(self):
        if self.phone:
            return self.phone
        elif self.email:
            return self.email
        return f"{self.name} - {self.phone} - {self.email}"
    
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True, related_name='custom_user_set')

class PhoneOTP(Timestamps):
    phone = models.IntegerField(null=False, blank=False, unique=True, default="", db_index=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    is_verified = models.BooleanField(default=False)



class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user}'s Wallet"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.transaction_type} - ₹{self.amount}"


class Strategy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, null=True, blank=True, default="")
    strategy_id = models.CharField(max_length=40, default=None, blank=True, null=True)
    description = models.TextField()
    user = models.ForeignKey(User, verbose_name='User-Strategy', blank=True, 
                            on_delete=models.CASCADE, related_name='algotrade_user_strategy')
    advantages = models.TextField()
    

class UserTradeDetails(models.Model):
    TRADE_CHOICES = (
    ("SELL", "SELL"),
    ("BUY", "BUY"))
    CEPE = (
    ("CALL", "CALL"),
    ("PUT", "PUT"))


    user = models.ForeignKey(User, verbose_name='User-Trades', blank=True, 
                            related_name='user_trades', on_delete=models.CASCADE)
    trade_type = models.CharField(max_length=10, default=None, null=True, choices=TRADE_CHOICES)
    cepe = models.CharField(max_length=10, default=None, null=True, choices=TRADE_CHOICES)
    trade_price = models.CharField(max_length=10, default="0", null=True)
    index = models.CharField(max_length=25, default=None, null=True)
    token = models.IntegerField(default=0)
    symbol = models.CharField(max_length=40, default=None, null=True)

    
    
    class Meta:
        verbose_name = 'UserTradeDetail'
        verbose_name_plural = 'UserTradeDetail'

class UserStrategy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, null=True, blank=True, default="")
    strategy_id = models.CharField(max_length=40, default=None, blank=True, null=True)
    description = models.TextField()
    user = models.ForeignKey(User, verbose_name='User-Strategy', blank=True, 
                            on_delete=models.CASCADE, related_name='user_strategy')
    advantages = models.TextField()

    
    class Meta:
        verbose_name = 'UserStrategy'
        verbose_name_plural = 'UserStrategys'

class UserOrders(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, verbose_name='User-Order', blank=True, 
                            on_delete=models.CASCADE, related_name='user_order')
    
    class Meta:
        verbose_name = 'UserOrder'
        verbose_name_plural = 'UserOrders'


