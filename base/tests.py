from django.test import TestCase, SimpleTestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
import datetime, json
from base.models import Profile, Order, Item, Category
from base import views

# Create your tests here.
class TestAuth(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='test', password='12test12', email='test@example.com')

    def test_correct(self):
        user1 = authenticate(username='test', password='12test12')
        self.assertTrue((user1 is not None) and user1.is_authenticated)
        # self.assertTemplateUsed(response, 'base/home.html')

    def test_wrong_username(self):
        user1 = authenticate(username='wrong', password='12test12')
        self.assertFalse(user1 is not None and user1.is_authenticated)
        # для скринов на интегр тестирование
        # self.assertEqual(messages, 'Username or password does not exist')

    def test_wrong_password(self):
        user1 = authenticate(username='test', password='wrong')
        self.assertFalse(user1 is not None and user1.is_authenticated)
        # self.assertEqual(messages, 'Username or password does not exist')


# testin Order, Item Models
class TestModels(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='test', password='12test12', email='test@example.com')
        self.user1.save()
        user1 = authenticate(username='test', password='12test12')

        self.order1 = Order.objects.create(
            customer=user1,
            code='user1_1',
            cost=100,
            delivery_cost=200,
            margin=50
        )
    
    def test_total_cost(self):
        self.assertEquals(self.order1.total_cost, 350)
    
    def test_filled(self):
        self.order1.track_code = 'TR8990786RU'
        self.order1.delivery_day = datetime.date.today()
        self.order1.save()
        self.assertEquals(self.order1.filled, True)

    def test_not_filled(self):
        self.assertEquals(self.order1.filled, False)

    def test_item_filled(self):
        self.item1 = Item.objects.create(
            order=self.order1,
            weight = 10,
            cost = 4
        )
        self.assertEquals(self.item1.filled, True)

    def test_item_not_filled(self):
        self.item1 = Item.objects.create(
            order=self.order1,
            weight = 10,
        )
        self.assertEquals(self.item1.filled, False)


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='test', password='12test12', email='test@example.com')
        self.user1.groups.add(Group.objects.create(name = 'customer'))
        self.client.login(username='test', password='12test12')

    def test_profile_customer(self):
        # self.user1.groups.add(Group.objects.create(name = 'customer'))
        response = self.client.get(reverse('profile'))
        self.assertEquals(response.status_code, 200)
    
    def test_profile_buyer(self):
        # self.user1.groups.add(Group.objects.create(name = 'buyer'))
        response = self.client.get(reverse('profile'))
        self.assertEquals(response.status_code, 200)

    def test_profile_courier(self):
        # self.user1.groups.add(Group.objects.create(name = 'courier'))
        response = self.client.get(reverse('profile'))
        self.assertEquals(response.status_code, 200)

    # only buyer can change status on shipped
    def test_change_status_on_shipped_buyer(self):
        # self.user1.groups.add(Group.objects.create(name = 'buyer'))
        self.client.login(username='test', password='12test12')
        self.order1 = Order.objects.create(
            customer = self.user1,
            code = 'user1_1',
            status='ready',
            payment_method='cash'
        )
        response = self.client.get(reverse('change-status', args=[self.order1.id]))
        self.assertEquals(response.status_code, 302)

    #интегр
    def test_change_status_on_shipped_customer(self):
        # self.user1.groups.add(Group.objects.create(name = 'customer'))
        self.client.login(username='test', password='12test12')
        self.order1 = Order.objects.create(
            customer = self.user1,
            code = 'user1_1',
            status='ready',
            payment_method='cash'
        )
        response = self.client.get(reverse('change-status', args=[self.order1.id]))
        self.assertEquals(response.status_code, 302)

    # интегр
    def test_change_status_on_shipped_courier(self):
        # self.user1.groups.add(Group.objects.create(name = 'courier'))
        self.client.login(username='test', password='12test12')
        self.order1 = Order.objects.create(
            customer = self.user1,
            code = 'user1_1',
            status='ready',
            payment_method='cash'
        )
        response = self.client.get(reverse('change-status', args=[self.order1.id]))
        self.assertEquals(response.status_code, 302)


    def test_delete_order_new(self):
        self.client.login(username='test', password='12test12')
        self.order1 = Order.objects.create(
            customer = self.user1,
            code = 'user1_1',
            status='new'
        )
        response = self.client.get(reverse('delete-order', args=[self.order1.id]))
        self.assertEquals(response.status_code, 200)
    def test_delete_order_ready(self):
        self.client.login(username='test', password='12test12')
        self.order1 = Order.objects.create(
            customer = self.user1,
            code = 'user1_1',
            status='ready'
        )
        response = self.client.get(reverse('delete-order', args=[self.order1.id]))
        self.assertEquals(response.status_code, 200)
    def test_delete_order_shipped(self):
        self.client.login(username='test', password='12test12')
        self.order1 = Order.objects.create(
            customer = self.user1,
            code = 'user1_1',
            status='shipped'
        )
        response = self.client.get(reverse('delete-order', args=[self.order1.id]))
        self.assertEquals(response.status_code, 200)


    def test_update_item_owner(self):
        self.client.login(username='test', password='12test12')
        self.order1 = Order.objects.create(customer= self.user1,code = 'user1_1')
        self.item1 = Item.objects.create(order= self.order1,name = 'item1')
        response = self.client.post(reverse('update-item', args=[self.item1.id]), {'name': 'item1'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.item1.name, 'item1')
        # self.assertEquals(self.item1.order.customer, user1)

    def test_update_item_stranger(self):  
        # self.user2 = User.objects.create_user(username='test2', password='12test12', email='test@example.com')
        self.client.login(username='test2', password='12test12')
        self.order1 = Order.objects.create( customer= self.user1, code = 'user1_1')
        self.item1 = Item.objects.create(order= self.order1, name = 'item1')
        response = self.client.post(reverse('update-item', args=[self.item1.id]), {'name': 'item1'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.item1.name, 'item1')
        # self.assertEquals(self.item1.order.customer, user2)

