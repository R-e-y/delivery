from django.contrib import admin

# Register your models here.

from .models import Order, Category, Item, Profile

admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Item)
