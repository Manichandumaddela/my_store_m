from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product, Cart, CartItem, Order, OrderItem

class GroceryStoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Fruits', icon='fas fa-apple-whole')
        self.product = Product.objects.create(
            category=self.category,
            name='Fresh Apples',
            price=5.00,
            discount_price=4.00,
            stock=20,
            unit='kg',
            is_available=True,
            is_featured=True
        )
        self.admin = User.objects.create_superuser(username='testadmin', password='password123', email='admin@test.com')
        self.user = User.objects.create_user(username='testuser', password='password123', email='user@test.com')

    def test_home_page(self):
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh Apples')

    def test_product_detail_page(self):
        response = self.client.get(reverse('store:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh Apples')
        self.assertContains(response, '₹4.00')

    def test_cart_workflow(self):
        # Add to cart
        add_url = reverse('store:add_to_cart', kwargs={'product_id': self.product.id})
        response = self.client.post(add_url, {'quantity': 2}, follow=True)
        self.assertEqual(response.status_code, 200)

        # Cart view
        cart_url = reverse('store:cart_view')
        response = self.client.get(cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh Apples')
        self.assertContains(response, '₹8.00')

    def test_checkout_and_order_creation(self):
        # Add to cart first
        self.client.post(reverse('store:add_to_cart', kwargs={'product_id': self.product.id}), {'quantity': 1})
        
        # Post checkout form
        checkout_url = reverse('store:checkout')
        checkout_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'city': 'New York',
            'postal_code': '10001',
            'payment_method': 'COD',
            'order_notes': 'Please ring bell',
        }
        response = self.client.post(checkout_url, checkout_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Order.objects.filter(email='john@example.com').exists())

    def test_admin_portal_protection(self):
        # Anonymous should redirect
        response = self.client.get(reverse('store:admin_dashboard'))
        self.assertEqual(response.status_code, 302)

        # Authenticated as staff/admin
        self.client.login(username='testadmin', password='password123')
        response = self.client.get(reverse('store:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Store Analytics & Dashboard')

        # Admin subpages
        self.assertEqual(self.client.get(reverse('store:manage_products')).status_code, 200)
        self.assertEqual(self.client.get(reverse('store:manage_categories')).status_code, 200)
        self.assertEqual(self.client.get(reverse('store:manage_orders')).status_code, 200)
        self.assertEqual(self.client.get(reverse('store:customer_details')).status_code, 200)
        self.assertEqual(self.client.get(reverse('store:sales_report')).status_code, 200)
