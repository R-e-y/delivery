from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(null=True, blank=True, max_length=30, default=' ')
    whatsapp = models.CharField(null=True, blank=True, max_length=30, default=' ')
    address = models.CharField(null=True, blank=True, max_length=100, default=' ')
    photo = models.ImageField(null=True, blank=True, upload_to='avatars/', default='avatars/default.jpg')

    # delivery_days = 

    def __str__(self):
        return self.user.username

    @property
    def recieved(self):
        return Order.objects.filter(status='recieved', customer=self.user).count()

    @property
    def in_progress(self):
        return Order.objects.filter(~Q(status='recieved'), customer=self.user).count()

    @property
    def delivered(self):
        return Order.objects.filter(status='recieved', courier=self.user).count()

    @property
    def delivering(self):
        return Order.objects.filter(status='delivering', courier=self.user).count()


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Coupon(models.Model):
    count = models.IntegerField(default=0)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.customer.username
    
    def increase(self, num=1):
        if self.count == 10:
            self.count = 0
        else:
            self.count += num
        self.save()

    def discount(self):
        if self.count == 10:
            return 0,5
        else:
            return 1


class Order(models.Model):
    
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    courier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='couriers')
    code = models.CharField(max_length=100, unique=True)
    track_code = models.CharField(null=True, blank=True, max_length=100)
    status = models.CharField(
        max_length=20, 
        choices=[
            ('new', 'new'), 
            ('ready', 'ready'), 
            ('paid', 'paid'), 
            ('shipped', 'shipped'), 
            ('arrived', 'arrived'), 
            ('delivering', 'delivering'), 
            ('recieved', 'recieved')
            ], 
            default='new',
        )
    # tracker = 
    
    address = models.CharField(max_length=100) # delivery address (home) 
    comment = models.TextField(null=True, blank=True)
    delivery_day = models.DateField(null=True) 
    cost = models.DecimalField(null=True, max_digits=8, decimal_places=2) # autocalculated field 
    delivery_cost = models.DecimalField(null=True, max_digits=8, decimal_places=2)
    margin = models.DecimalField(null=True, max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=[('cash', 'cash'),('card', 'card')], default ='cash')
    currency = models.CharField(max_length=5, choices=[('$', '$'), ('₺', '₺'), ('som', 'som')], default='$') # autocalculated field items currency 
    consult = models.BooleanField(default=True)

    updated = models.DateTimeField(auto_now=True) #every time saved
    created = models.DateTimeField(auto_now_add=True) #first time saved or created

    class Meta:
        ordering = ['-updated', '-created'] # '-' means descending order (the newest/updated will be first)
    
    @property
    def total_cost(self):
        return self.cost + self.delivery_cost + self.margin

    # True if these fields are filled
    @property
    def filled(self):
       return True if (self.track_code != None and self.delivery_day != None and self.cost != 0 and self.delivery_cost != 0 and self.margin != 0) else False


    def __str__(self):
        return self.code


class Item(models.Model):

    # Order -- parent name, on_delete -- CASCADE/SET_NULL, one-to-many relationship
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, max_length=200)
    link = models.URLField(null=True, max_length=200)
    weight = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    metric_unit = models.CharField(max_length=2, choices=[('kg', 'kg'), ('g', 'g'), ('lb', 'lb')], default='g')
    quantity = models.PositiveIntegerField(default=1)
    cost = models.DecimalField(null=True, max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=5, choices=[('$', '$'), ('₺', '₺'), ('som', 'som')], default='$') 

    updated = models.DateTimeField(auto_now=True) 
    created = models.DateTimeField(auto_now_add=True) 

    class Meta:
            ordering = ['-updated', '-created']

    @property
    def filled(self):
        return True if self.weight != 0 and self.cost != 0 else False

    def __str__(self):
        return self.name # returns fist 50 characters





