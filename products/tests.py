from decimal import Decimal

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.test import Client, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Product, Brand


class ProductViewSetAdminTestCase(APITestCase):
    """
    Test cases for Admin users
    """
    def setUp(self):
        self.client = Client()

        self.username = 'admin'
        self.password = 'adminpassword'
        
        self.admin_user = User.objects.create_user(
            first_name='Admin',
            last_name='LastName 1',
             username=self.username,
            email='latorregab@gmail.com',
            password=self.password
        )
        self.admin_user2 = User.objects.create_user(
            first_name='Admin 2',
            last_name='LastName 2',
            username='admin2',
            email='hola@latorregabriel.com',
            password=self.password
        )

        admin_group, created = Group.objects.get_or_create(name='admin')

        brand_content_type = ContentType.objects.get_for_model(Brand)
        brand_permissions = Permission.objects.filter(content_type=brand_content_type)
        product_content_type = ContentType.objects.get_for_model(Product)
        product_permissions = Permission.objects.filter(content_type=product_content_type)

        admin_group.permissions.set(brand_permissions | product_permissions)

        admin_group.user_set.add(self.admin_user)
        admin_group.user_set.add(self.admin_user2)

        admin_group.save()

        self.admin_user.save()

        self.brand = Brand.objects.create(name='Brand 1')
        self.product = Product.objects.create(
            name='Product 1',
            sku='P001',
            price=Decimal(20.0),
            brand=self.brand
        )

    def test_product_retrieve(self):
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=self.product.pk).visits, 1)

        self.client.login( username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=self.product.pk).visits, 1)

    @override_settings(DEBUG=True)
    def test_product_partial_update(self):
        self.client.login( username=self.username, password=self.password)
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.patch(url, {'name': 'Product 1 (Updated)'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=self.product.pk).name, 'Product 1 (Updated)')

    @override_settings(DEBUG=True)
    def test_product_update(self):
        self.client.login( username=self.username, password=self.password)
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.put(url, {
            'name': 'Product 1 (Updated)',
            'sku': self.product.sku,
            'price': 30.0,
            'brand': reverse('brand-detail', kwargs={'pk': self.brand.pk})
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_users_dont_increases_visits_when_retrieving_products(self):

        self.client.login( username=self.username, password=self.password)

        response = self.client.get(f'/products/{self.product.sku}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        visits_count = response.data['visits']

        response = self.client.get(f'/products/{self.product.sku}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['visits'], visits_count)


class ProductViewSetNonAdminUserTestCase(APITestCase):
    """
    Test cases for Non admin users that are logged in.
    """
    def setUp(self):
        # creates a user who is not an admin
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

        self.brand = Brand.objects.create(name='Brand example')

        self.product = Product.objects.create(
            sku='P0000',
            name='Test Product',
            price='10.00',
            brand=self.brand
        )

        # create a client to make API requests
        self.client = Client()

    def test_non_admin_cannot_create_product(self):
        # login as the non-admin user
        self.client.login(username=self.username, password=self.password)

        # attempt to create a new product
        response = self.client.post('/products/', {
            'sku': 'P0001',
            'name': 'Test Product',
            'price': 100.00,
            'brand': reverse('brand-detail', kwargs={'pk': self.brand.pk})
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_anonymous_users_dont_increases_visits_when_retrieving_products(self):

        self.client.login(username=self.username, password=self.password)

        response = self.client.get(f'/products/{self.product.sku}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        visits_count = response.data['visits']

        response = self.client.get(f'/products/{self.product.sku}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['visits'], visits_count)

    @override_settings(DEBUG=True)
    def test_non_admin_cannot_update_product(self):
        # create a product that we can attempt to update
        Product.objects.create(
            sku='P0001',
            name='Test Product',
            price='100.00',
            brand=self.brand
        )

        # login as the non-admin user
        self.client.login(username=self.username, password=self.password)

        # attempt to update the product
        response = self.client.put('/products/1/', {
            'sku': 'P0001',
            'name': 'Updated Test Product',
            'price': 150.00,
            'brand': reverse('brand-detail', kwargs={'pk': self.brand.pk})
        })

        # assert that the response is forbidden (status code 403)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductViewSetAnonymousUserTestCase(APITestCase):
    """
    Test cases for anonymous users
    """

    def setUp(self):

        self.brand = Brand.objects.create(name='Brand 1')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TP123',
            price=Decimal(25.5),
            brand=self.brand
        )

    def test_anonymous_user_can_list_and_get_products(self):
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(f'/products/{self.product.sku}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_anonymous_user_increases_visits_when_retrieving_products(self):

        response = self.client.get(f'/products/{self.product.sku}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        visits_count = response.data['visits']

        response = self.client.get(f'/products/{self.product.sku}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['visits'], visits_count + 1)

    def test_anonymous_user_cannot_update_or_create_products(self):
        data = {'name': 'Updated Product'}

        # Anonymous user can't update products
        response = self.client.patch(f'/products/{self.product.sku}/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Anonymous user can't create products
        response = self.client.post('/products/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
