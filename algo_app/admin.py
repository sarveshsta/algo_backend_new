from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(PhoneOTP)
admin.site.register(Wallet)
admin.site.register(Strategy)
admin.site.register(UserTradeDetails)
admin.site.register(UserOrders)
admin.site.register(UserStrategy)

