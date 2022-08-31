import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from dateutil.relativedelta import relativedelta
from datetime import date
from django import forms
from django.shortcuts import render, redirect 
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import UserForm, OrderForm, ItemForm, ProfileForm, UpdateUserForm, ReportForm
from .models import Order, Item, Category, Profile

# create your viwes here

# orders = [
#     {'id': 1, 'name': 'Jacket'},
#     {'id': 2, 'name': 'Skirt'},
#     {'id': 3, 'name': 'Dyson'},
# ]

# def track(request):
#     data = { 'input class': 'form-control', 'value': 'RO256117306RU' }
#     r = requests.post('https://parcelsapp.com/en/tracking/', data)
#     print (r)
#     return redirect ('home')


def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # try:
        #     user = User.objects.get(username=username)
        # except:
        #     messages.error(request, 'User does not exist')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user) # creates token in db and browser sessions
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request) # deletes token
    messages.info(request, 'You are logged out.')
    return redirect('home')


def registerPage(request):
    form = UserForm()
    if request.user.groups.all():
        user_type = 'buyer'
        group = Group.objects.get(name = 'courier')
    else:
        user_type = 'customer'
        group = Group.objects.get(name = 'customer')

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # freezing to access newly created user object
            user.username = user.username.lower()
            user.save()
            user.groups.add(group)
            Profile.objects.create(
                user = user
            )
             
            if user_type == 'buyer':
                # just output success message
                return redirect('members')
            else:
                login(request, user)
                return redirect('home')
            
        else:
            # return JsonResponse({"message": "Form is invalid"}, status=400)
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


# quick guide
def home(request):
    context = {}
    return render(request, 'base/home.html', context)


# # exchange
# def exchange(request):
#     context = {}
#     return render(request, 'base/exchange.html', context)


# about us
def aboutUs(request):
    context = {}
    return render(request, 'base/about-us.html', context)


# members
@login_required(login_url='login')
def members(request):

    user_type = request.user.groups.all()[0].name
    couriers = User.objects.filter(groups__name ='courier')
    customers = User.objects.filter(groups__name='customer')
    # print(Order.objects.filter(courier__username='arif', status='recieved'))
    # print(Order.objects.filter(courier__username='richard', status='recieved'))
    # print(Order.objects.filter(courier__username='sanji', status='recieved'))
    context={'user_type': user_type, 'couriers': couriers, 'customers': customers}
    return render(request, 'base/members.html', context)


@login_required(login_url='login')
def deleteCourier(request, pk):
    courier = User.objects.get(id=pk)

    if request.method == 'POST':
        courier.delete()
        return redirect('members')

    return render(request, 'base/delete.html', {'obj': courier})


@login_required(login_url='login')
def changeStatus(request, pk):
    order = Order.objects.get(id=pk)
    user_type = request.user.groups.all()[0].name
    status = order.status
    method = order.payment_method
    new_status = ''
    if user_type == 'customer':
        if method == 'cash' and status == 'paid' or method == 'card' and status == 'delivering':
            new_status = 'recieved'
            messages.info(request, 'Order has been recieved!')

    elif user_type == 'courier':
        if status == 'arrived':
            order.courier = request.user
            new_status = 'delivering' 
            messages.info(request, 'Order has been picked up by courier!')
        else:
            new_status = 'paid'
            messages.info(request, 'Order has been paid!')

    elif user_type == 'buyer':
        if status == 'ready':
            if method == 'cash':
                new_status = 'shipped' 
                messages.info(request, 'Order has been shipped!')
            else: 
                new_status = 'paid'
                messages.info(request, 'Order has been paid!')

        elif status == 'paid':
            new_status = 'shipped'
            messages.info(request, 'Order has been shipped!')
        elif status == 'shipped':
            new_status = 'arrived'
            messages.info(request, 'Order has been arrived!')

    order.status = new_status
    order.save()
    
    return redirect('my-orders')


@login_required(login_url='login')
def reports(request):
    form = ReportForm(initial={'period': 'custom'})
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            q1 = q2 = q3 = q4 = Q()
            period = form.cleaned_data.get('period')
            if not form.cleaned_data.get('all_orders'):
                q1 = Q(code = form.cleaned_data.get('orders'))

            if not form.cleaned_data.get('all_couriers'):
                q2 = Q(courier__in = form.cleaned_data.get('couriers'))

            if not form.cleaned_data.get('all_customers'):
                q3 = Q(customer__in = form.cleaned_data.get('customers'))

            if period == 'custom':
                start_date = form.cleaned_data.get('start_date')
                end_date = form.cleaned_data.get('end_date')
            elif period == 'week':
                start_date = date.today() - relativedelta(days=7)
                end_date = date.today()
            elif period == 'month':
                start_date = date.today() - relativedelta(months=1)
                end_date = date.today()
            elif period == 'year':
                start_date = date.today() - relativedelta(years=1)
                end_date = date.today()
            q4 = Q(created__range = [start_date, end_date])
           

            if form.cleaned_data.get('order_by_date') and form.cleaned_data.get('order_by_margin'):
                orders = Order.objects.filter(q1 & q2 & q3 & q4).order_by('-created', '-margin')
            elif form.cleaned_data.get('order_by_date'):
                orders = Order.objects.filter(q1 & q2 & q3 & q4).order_by('-created')
            elif form.cleaned_data.get('order_by_margin'):
                orders = Order.objects.filter(q1 & q2 & q3 & q4).order_by('-margin')
            else:
                orders = Order.objects.filter(q1 & q2 & q3 & q4)


           # PDF creation ----------------------------------------------

            # Create a file-like buffer to receive PDF data.
            buffer = io.BytesIO()
            # Create the PDF object, using the buffer as its "file."
            c = canvas.Canvas(buffer, pagesize = letter, bottomup = 0)
     
            c.drawString(50, 50, 'Report of ' + date.today().strftime('%d.%m.%y'))
            data = []
            data.append(['No.','Date', 'Code', 'Status', 'Customer', 'Cost', 'Delivery cost', 'Total cost', 'Income', 'Currency'])

            i = tc = td = tt = tm = cur = 0 # total(cost, delivery_cost, total_cost, margin) respectively
            # for i in range(orders.count()):
            for order in orders:
                cur = order.currency
                i += 1
                tc += order.cost
                td += order.delivery_cost
                tt += order.total_cost
                tm += order.margin
                row_vals = []
                row_vals.append(i)
                row_vals.append(order.created.strftime('%d.%m.%y'))
                row_vals.append(order.code)
                row_vals.append(order.status)
                row_vals.append(order.customer)
                row_vals.append(order.cost)
                row_vals.append(order.delivery_cost)
                row_vals.append(order.total_cost)
                row_vals.append(order.margin)
                row_vals.append(order.currency)

                data.append(row_vals)
            data.append(['','', '', '', '', '---------', '-----------------', '-------------', '----------', '------------'])
            data.append(['','', '', '', '', tc, td, tt, tm, cur])
            data.append('')
            data.append('')
            

            # if salary is selected
            if form.cleaned_data.get('salary'):
                couriers = User.objects.filter(groups__name = 'courier')
                data.append(['','', '', '', '', 'No.','Courier', 'Delivered', 'Salary', 'Currency'])
                i = ts = 0 # total salary
                for courier in couriers:
                    count = Order.objects.filter(courier = courier).count()
                    print(courier.order_set.first())
                    print(courier.username, count)
                    i += 1
                    ts += 200 * count
                    row_vals = []
                    row_vals.append('')
                    row_vals.append('')
                    row_vals.append('')
                    row_vals.append('')
                    row_vals.append('')
                    row_vals.append(i)
                    row_vals.append(courier.username)
                    row_vals.append(count)
                    row_vals.append(200 * count)
                    row_vals.append('som')
                    # print(courier.order_set.count())

                    data.append(row_vals)
                data.append(['','', '', '', '', '', '', '', '-----------', '------------'])
                data.append(['','', '', '', '', '', '', '', ts, 'som'])
                

            data.reverse()
            tbl = Table(data)
            
            tbl.wrap(0, 0)
            tbl.drawOn(c, 50, 80)

            # Close the PDF object cleanly, and we're done.
            c.showPage()
            c.save()

            # FileResponse sets the Content-Disposition header so that browsers
            # present the option to save the file.
            buffer.seek(0)
            return FileResponse(buffer, filename='delivery-report.pdf')
            

    context = {'form':form}
    return render(request, 'base/report_form.html', context)


# Profile viwes -------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def profile(request, pk):

    user_type = request.user.groups.all()[0].name
    user = User.objects.get(id=pk)
    context={'user_type': user_type, 'user': user}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def updateProfile(request):
    # user_type = request.user.groups.all()[0].name 
    user_form = UpdateUserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    # user_form.fields['password1'].widget = forms.HiddenInput()
    # user_form.fields['password2'] = user_form.fields['password2'].hidden_widget()

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
        

    context={'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'base/profile_form.html', context)


@login_required(login_url='login')
def deleteProfile(request, pk):
    user = User.objects.get(id=pk)

    if request.method == 'POST':
        user.delete()
        return redirect('register', user_type='customer')

    return render(request, 'base/delete.html', {'obj': user})


# Order viwes -------------------------------------------------------------------------------------------------------

@login_required(login_url='login') 
def myOrders(request):
    user_type = request.user.groups.all()[0].name
    Order.objects.exclude(pk__in=[x.order.pk for x in Item.objects.all()]).delete()
    q1 = q2 = Q()
    if user_type == 'customer':
        q1 = ~Q(status='recieved') & Q(customer = request.user)
    elif user_type == 'courier':
        q1 = Q(status='arrived') | Q(status='delivering') & Q(courier = request.user)
    elif user_type == 'buyer':
        q1 = ~Q(status='recieved')

    orders_count = Order.objects.filter(q1).count()

    if request.GET.get('q') != None:
        q = request.GET.get('q')  
        q2 = (
            Q(status__icontains=q) |
            Q(code__icontains=q) |
            Q(created__icontains=q) |
            Q(customer__username__icontains=q) 
        )
    orders = Order.objects.filter(q1 & q2)
    order_items = Item.objects.all()
    categories = Category.objects.all()
    context = {
        'user_type': user_type,
        'orders': orders, 
        'categories': categories, 
        'orders_count': orders_count, 
        'order_items': order_items
        }
    return render(request, 'base/my-orders.html', context) # using template


@login_required(login_url='login') 
def myOrdersCompleted(request):
    user_type = request.user.groups.all()[0].name

    q1 = q2 = Q()
    if user_type == 'customer':
        q1 = Q(status='recieved') & Q(customer = request.user)
    elif user_type == 'courier':
        q1 = Q(status='recieved') & Q(courier = request.user)
    elif user_type == 'buyer':
        q1 = Q(status='recieved')

    orders_count = Order.objects.filter(q1).count()

    # searchbar
    order_items = Item.objects.all()
    if request.GET.get('q') != None:
        q = request.GET.get('q')  
        q2 = (
            Q(status__icontains=q) |
            Q(code__icontains=q) |
            # Q(__itemcontains=q) |
            Q(created__icontains=q) |
            Q(customer__username__icontains=q) 
        )
 
    orders = Order.objects.filter(q1 & q2)
    context = {
        'user_type': user_type,
        'orders': orders, 
        'orders_count': orders_count, 
        'order_items': order_items
        }
    return render(request, 'base/my-orders.html', context) # using template



@login_required(login_url='login')
def order(request, pk):

    user_type = request.user.groups.all()[0].name
    order = Order.objects.get(id=pk)
    order_items = order.item_set.all() # .order_by(-created)
    items_count = order_items.count()

    context = {
        'user_type':user_type, 
        'order':order, 
        'order_items': order_items, 
        'items_count': items_count
        }
    return render(request, 'base/order.html', context) 


@login_required(login_url='login')
def createOrder(request):
    generated_code = request.user.username.upper() + '_' + str(Order.objects.latest('id').id + 1)
    order = Order.objects.create(customer=request.user, code=generated_code)
    return redirect('add-items', pk=order.id)


@login_required(login_url='login')
def updateOrder(request, pk):

    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order) # gets fields prefilled
    user_type = request.user.groups.all()[0].name

    if user_type == 'customer':
        form.fields['code'].widget = forms.HiddenInput()
        form.fields['track_code'].widget = forms.HiddenInput()
        form.fields['delivery_day'].widget = forms.HiddenInput()
        form.fields['cost'].widget = forms.HiddenInput()
        form.fields['delivery_cost'].widget = forms.HiddenInput()
        form.fields['margin'].widget = forms.HiddenInput()
        form.fields['currency'].widget = forms.HiddenInput()
    else:
        form.fields['address'].widget = forms.HiddenInput()
        form.fields['payment_method'].widget = forms.HiddenInput()

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order) # specifying which order to update, otherwise new order will be created
        if form.is_valid():
            order = form.save()
            
            items_filled = 1
            for item in order.item_set.all():
                if not item.filled:
                    items_filled = 0

            if order.filled and items_filled:
                order.status = 'ready'
                order.save()
                messages.success(request, 'Order updated successfully!')
            else:
                messages.success(request, 'Order created successfully!')

            return redirect('order', pk=order.id)

    context = {'form': form }
    return render(request, 'base/order_form.html', context)


@login_required(login_url='login')
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order successfully deleted.')
        return redirect('my-orders')

    return render(request, 'base/delete.html', {'obj': order})



# Item viwes -------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def addItems(request, pk):
    
    order = Order.objects.get(id=pk)
    order_items = order.item_set.all() # .order_by(-created)
    form = ItemForm(initial={'order': order})

    form.fields['weight'].widget = forms.HiddenInput()
    form.fields['metric_unit'].widget = forms.HiddenInput()
    form.fields['cost'].widget = forms.HiddenInput()
    form.fields['currency'].widget = forms.HiddenInput()

    if request.method == 'POST':
        form = ItemForm(request.POST) 
        if form.is_valid():
            form.save() 
            if order_items.count() == 1:
                return redirect('update-order', pk=order.id) 
            else:
                return redirect('order', pk=order.id)

    context={'form': form, 'order': order, 'order_items': order_items}
    return render(request, 'base/items_form.html', context)


@login_required(login_url='login')
def updateItem(request, pk):
    item_btn = 'edit'

    item = Item.objects.get(id=pk)
    order = item.order
    order_items = item.order.item_set.all() # .order_by(-created)
    form = ItemForm(instance=item) # gets fields prefilled
    user_type = request.user.groups.all()[0].name

    if user_type == 'customer':
        form.fields['weight'].widget = forms.HiddenInput()
        form.fields['metric_unit'].widget = forms.HiddenInput()
        form.fields['cost'].widget = forms.HiddenInput()
        form.fields['currency'].widget = forms.HiddenInput()
    else:
        form.fields['category'].widget = forms.HiddenInput()
        form.fields['name'].widget = forms.HiddenInput()
        form.fields['description'].widget = forms.HiddenInput()
        form.fields['link'].widget = forms.HiddenInput()
        form.fields['quantity'].widget = forms.HiddenInput()

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item) # specifying which order to update, otherwise new order will be created
        if form.is_valid():
            form.save()

            if user_type == 'buyer':
                items_filled = 1
                for item in order_items:
                    if not item.filled:
                        items_filled = 0
                if items_filled:
                    order.cost = sum([item.cost for item in order_items])
                    order.status = 'ready' if order.filled else order.status
                    order.save()
            
            return redirect('order', pk=item.order.id)

    context = {
        'form': form, 
        'item': item,
        'order':order, 
        'order_items': order_items, 
        'item_btn': item_btn
        }
    return render(request, 'base/items_form.html', context)


@login_required(login_url='login')
def deleteItem(request, pk):
    item = Item.objects.get(id=pk)

    if request.user != item.order.customer:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        item.delete()
        return redirect('order', pk=item.order.id)

    return render(request, 'base/delete.html', {'obj': item})