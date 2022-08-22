from django import forms
from django.forms import ModelForm
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Order, Item, Profile

# creates form fields for all fields from Order model
# fields = '__all__' # or ['name', 'body'] 
# exclude = ['customer', 'code'] # if exluded the field won't be filled
class UserForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput({'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput({'placeholder': 'Confirm Password'}))
    
    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'password1', 
            'password2'
            ]
        widgets = {
            'username': forms.TextInput({ "placeholder": "Username"}),
            'email': forms.EmailInput({ "placeholder": "Email"}),

        }


class UpdateUserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 
            'first_name',
            'last_name',
            'email', 
        ]
        widgets = {
            # 'username': forms.TextInput({ "placeholder": "Username"}),
            # 'email': forms.EmailInput({ "placeholder": "Email"}),
        }


class ReportForm(forms.Form):
    all_orders = forms.BooleanField(required=False)
    orders = forms.MultipleChoiceField(
        choices=(
            ('new', 'new'), 
            ('ready', 'ready'), 
            ('paid', 'paid'), 
            ('shipped', 'shipped'), 
            ('arrived', 'arrived'), 
            ('delivering', 'delivering'), 
            ('recieved', 'recieved')
            ), 
            required=False,
            widget=forms.SelectMultiple
        )
    all_couriers = forms.BooleanField(required=False)
    couriers = forms.ModelMultipleChoiceField(queryset = User.objects.filter(groups__name ='courier'), required=False, widget=forms.SelectMultiple)
    all_customers = forms.BooleanField(required=False)
    customers = forms.ModelMultipleChoiceField(queryset = User.objects.filter(groups__name ='customer'), required=False, widget=forms.SelectMultiple)
    period = forms.ChoiceField(choices = (('custom', 'custom'), ('week', 'week'), ('month', 'month'), ('year', 'year')), required=False)
    start_date = forms.DateField(required=False, widget=forms.DateInput(format='%d-%m-%y'))
    end_date = forms.DateField(required=False)
    order_by_date = forms.BooleanField(required=False)
    order_by_margin = forms.BooleanField(required=False)
    salary = forms.BooleanField(required=False, label = 'Calculate salary for couriers')
    

    def clean(self):
        cleaned_data = super().clean()
        all_orders = cleaned_data.get("all_orders")
        orders = cleaned_data.get("orders")
        all_couriers = cleaned_data.get("all_couriers")
        couriers = cleaned_data.get("couriers")
        all_customers = cleaned_data.get("all_customers")
        customers = cleaned_data.get("customers")
        period = cleaned_data.get('period')
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not all_orders and not orders:
            raise ValidationError("At least 'all orders' must be chosen")
        if not all_couriers and not couriers:
            raise ValidationError("At least 'all couriers' option must be chosen")
        if not all_customers and not customers:
            raise ValidationError("At least 'all customers' option must be chosen")
        
        if not period == 'custom' and start_date and end_date:
            raise ValidationError("Start and End date are availble only if 'custom' option is selected")
        elif period == 'custom' and not start_date and not end_date:
            raise ValidationError("Period must be chosen")


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            'phone',
            'whatsapp',
            'photo', 
          
        ]
        widgets = {
            'phone': forms.TextInput({ "placeholder": "Phone number (Don't forget the country code)"}),
            'whatsapp': forms.TextInput({ "placeholder": "WhatsApp number"}),
            # 'photo': forms.ImageField(),
        }


class OrderForm(ModelForm):
    class Meta:
        model = Order

        fields = '__all__'

        widgets = {
            'customer': forms.HiddenInput(),
            'courier': forms.HiddenInput(),
            # code
            # 'track_code': forms.TextInput({ "placeholder": "Tracking code"}),
            'status': forms.HiddenInput(),
            'comment': forms.TextInput({ "placeholder": "comment to the order"}),
            'address': forms.TextInput({ "placeholder": "destination address"}),
            'delivery_day': forms.DateInput({ "placeholder": "approximate date of delivery"}),
            'cost': forms.NumberInput({ "placeholder": "cost of all items"}),
            'delivery_cost': forms.NumberInput({ "placeholder": "cost of delivery service"}),
            'margin': forms.NumberInput({ "placeholder": "cost of buyer service"}),
            # payment_method
            # currency
        }


class ItemForm(ModelForm):
    class Meta:
        model = Item

        fields = '__all__' 

        widgets = {
            'order': forms.HiddenInput(),
            # 'description': forms.Textarea({'rows':3}),
            'link': forms.URLInput({"placeholder": "link of an item store or photo"})

        }


# class OrderCustomerForm(ModelForm):
#     class Meta:
#         model = Order

#         fields = [
#             'customer',
#             'code',
#             # 'status',
#             'address',
#             'comment',
#             'payment_method'
#         ]

#         widgets = {
#             'customer': forms.HiddenInput(),
#             'code': forms.HiddenInput(),
#             # 'track_code': forms.TextInput({ "placeholder": "Tracking code"}),
#             'status': forms.HiddenInput(),
#             # 'comment': forms.TextInput({ "placeholder": "Comment"}),
#             # 'address': forms.TextInput({ "placeholder": "Destination address"}),
#             # 'delivery_day': forms.DateInput({ "placeholder": "Approximate date of delivery"}),
#             # 'cost': forms.NumberInput({ "placeholder": "Cost of all items"}),
#             # 'delivery_cost': forms.NumberInput({ "placeholder": "Cost of delivery service"}),
#             # payment_method
#             # currency
#         }


# class OrderBuyerForm(ModelForm):
#     class Meta:
#         model = Order

#         fields = [
#             'customer',
#             'code',
#             'track_code',
#             # 'status',
#             'comment',
#             'delivery_day',
#             'cost',
#             'delivery_cost',
#             'currency'
#         ]

#         widgets = {
#             'customer': forms.HiddenInput(),
#             # code
#             # 'track_code': forms.TextInput({ "placeholder": "Tracking code"}),
#             'status': forms.HiddenInput(),
#             # 'comment': forms.TextInput({ "placeholder": "Comment"}),
#             'address': forms.TextInput({ "placeholder": "Destination address"}),
#             'delivery_day': forms.DateInput({ "placeholder": "Approximate date of delivery"}),
#             'cost': forms.NumberInput({ "placeholder": "Cost of all items"}),
#             # 'delivery_cost': forms.NumberInput({ "placeholder": "Cost of delivery service"}),
#             # payment_method
#             # currency
#         }


