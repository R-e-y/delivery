from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),

    path('', views.home , name='home'),
    # path('exchange/', views.exchange , name='exchange'), 
    path('about-us/', views.aboutUs , name='about-us'), 
    path('members/', views.members , name='members'), #different members depending on roles
    path('delete-courier/<str:pk>/', views.deleteCourier , name='delete-courier'),
    path('change-status/<str:pk>/', views.changeStatus , name='change-status'),
    path('reports/', views.reports, name='reports'),
    
    path('profile/<str:pk>/', views.profile, name='profile'), #different profiles depending on roles
    path('update-profile/', views.updateProfile , name='update-profile'),
    path('delete-profile/<str:pk>/', views.deleteProfile , name='delete-profile'),



# Order urls -------------------------------------------------------------------------------------------------------
    
    path('my-orders/', views.myOrders, name="my-orders"),
    path('order/<str:pk>/', views.order, name="order"),
    path('create-order/', views.createOrder, name="create-order"),
    path('update-order/<str:pk>/', views.updateOrder, name="update-order"),
    path('delete-order/<str:pk>/', views.deleteOrder, name="delete-order"),

# Item urls -------------------------------------------------------------------------------------------------------

    # path('item/<str:pk>/', views.item, name="item"),
    path('add-items/<str:pk>/', views.addItems, name="add-items"),
    path('update-item/<str:pk>/', views.updateItem, name="update-item"),
    path('delete-item/<str:pk>/', views.deleteItem, name="delete-item"),
    
]


urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)