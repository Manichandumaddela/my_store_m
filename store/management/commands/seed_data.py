from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, Order, OrderItem
from accounts.models import UserProfile
import random
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds initial grocery categories, products, admin/customer accounts, and demo orders.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Beginning grocery database seeding...'))

        # 1. Create Superuser / Admin
        admin_user, created = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@freshcart.com',
            'first_name': 'Store',
            'last_name': 'Manager',
            'is_staff': True,
            'is_superuser': True,
        })
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created Admin Account: admin / admin123'))
        else:
            self.stdout.write('Admin account already exists.')

        # 2. Create Demo Customer
        customer_user, created = User.objects.get_or_create(username='customer', defaults={
            'email': 'sarah.miller@example.com',
            'first_name': 'Sarah',
            'last_name': 'Miller',
        })
        if created:
            customer_user.set_password('customer123')
            customer_user.save()
            profile = customer_user.profile
            profile.phone = '+1 (555) 234-5678'
            profile.address = '742 Evergreen Terrace, Apt 4B'
            profile.city = 'Springfield'
            profile.postal_code = '97477'
            profile.save()
            self.stdout.write(self.style.SUCCESS('Created Customer Account: customer / customer123'))

        # 3. Categories Data
        categories_data = [
            {
                'name': 'Fresh Fruits & Vegetables',
                'description': 'Crisp farm-picked organic fruits, leafy greens, and vegetables.',
                'icon': 'fas fa-apple-whole',
            },
            {
                'name': 'Dairy, Milk & Eggs',
                'description': 'Farm-fresh milk, organic pasture eggs, artisanal butter, and cheese.',
                'icon': 'fas fa-egg',
            },
            {
                'name': 'Bakery & Fresh Bread',
                'description': 'Daily baked sourdough, artisan baguettes, buns, and gourmet croissants.',
                'icon': 'fas fa-bread-slice',
            },
            {
                'name': 'Beverages & Juices',
                'description': 'Cold-pressed natural fruit juices, organic green teas, and mineral waters.',
                'icon': 'fas fa-bottle-water',
            },
            {
                'name': 'Snacks & Packaged Food',
                'description': 'Healthy nut mixes, roasted crackers, dried fruit bites, and dips.',
                'icon': 'fas fa-cookie',
            },
            {
                'name': 'Organic Grains & Staples',
                'description': 'Premium basmati rice, organic whole wheat flour, lentils, and pulses.',
                'icon': 'fas fa-wheat-awn',
            },
        ]

        cat_objs = {}
        for cdata in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cdata['name'],
                defaults={
                    'description': cdata['description'],
                    'icon': cdata['icon']
                }
            )
            cat_objs[cdata['name']] = cat

        self.stdout.write(self.style.SUCCESS(f'Created/Loaded {len(cat_objs)} categories.'))

        # 4. Products Data
        products_data = [
            # Fruits & Veggies
            {
                'category': cat_objs['Fresh Fruits & Vegetables'],
                'name': 'Organic Gala Apples',
                'description': 'Sweet, aromatic, and crispy certified organic red Gala apples straight from Washington orchards.',
                'price': 4.99,
                'discount_price': 3.99,
                'stock': 45,
                'unit': 'kg',
                'is_featured': True,
            },
            {
                'category': cat_objs['Fresh Fruits & Vegetables'],
                'name': 'Fresh Baby Spinach',
                'description': 'Tender, washed, nutrient-dense organic baby spinach leaves, ideal for salads and smoothies.',
                'price': 2.99,
                'discount_price': 2.49,
                'stock': 28,
                'unit': 'packet',
                'is_featured': True,
            },
            {
                'category': cat_objs['Fresh Fruits & Vegetables'],
                'name': 'Ripe Hass Avocados',
                'description': 'Creamy, rich Hass avocados packed with healthy omega fats and dietary fiber.',
                'price': 5.50,
                'discount_price': 4.75,
                'stock': 35,
                'unit': 'item',
                'is_featured': True,
            },
            {
                'category': cat_objs['Fresh Fruits & Vegetables'],
                'name': 'Sweet Organic Carrots',
                'description': 'Sweet and crunchy orange carrots with fresh green tops, harvested daily.',
                'price': 1.99,
                'discount_price': None,
                'stock': 50,
                'unit': 'kg',
                'is_featured': False,
            },

            # Dairy & Eggs
            {
                'category': cat_objs['Dairy, Milk & Eggs'],
                'name': 'Pasture-Raised Organic Whole Milk',
                'description': 'Grade A pasture-raised whole milk from grass-fed cows, rich in calcium and vitamin D.',
                'price': 4.49,
                'discount_price': 3.89,
                'stock': 20,
                'unit': 'liter',
                'is_featured': True,
            },
            {
                'category': cat_objs['Dairy, Milk & Eggs'],
                'name': 'Free-Range Brown Eggs (Dozen)',
                'description': '12 Large free-range brown eggs with vibrant golden yolks from ethically raised hens.',
                'price': 5.99,
                'discount_price': 4.99,
                'stock': 30,
                'unit': 'box',
                'is_featured': True,
            },
            {
                'category': cat_objs['Dairy, Milk & Eggs'],
                'name': 'Artisanal Salted Butter',
                'description': 'Slow-churned European-style cultured butter with a rich creamy texture.',
                'price': 3.75,
                'discount_price': None,
                'stock': 18,
                'unit': 'item',
                'is_featured': False,
            },

            # Bakery
            {
                'category': cat_objs['Bakery & Fresh Bread'],
                'name': 'Artisan Sourdough Loaf',
                'description': 'Traditional naturally fermented sourdough bread with a crispy crust and chewy airy crumb.',
                'price': 4.50,
                'discount_price': 3.99,
                'stock': 15,
                'unit': 'item',
                'is_featured': True,
            },
            {
                'category': cat_objs['Bakery & Fresh Bread'],
                'name': 'French Butter Croissants (4-Pack)',
                'description': 'Flaky, buttery, golden brown croissants baked fresh every morning.',
                'price': 6.20,
                'discount_price': 5.50,
                'stock': 12,
                'unit': 'packet',
                'is_featured': False,
            },

            # Beverages
            {
                'category': cat_objs['Beverages & Juices'],
                'name': 'Cold Pressed Valencia Orange Juice',
                'description': '100% pure squeezed Valencia orange juice with natural pulp and zero added sugars.',
                'price': 3.99,
                'discount_price': 3.49,
                'stock': 25,
                'unit': 'bottle',
                'is_featured': True,
            },
            {
                'category': cat_objs['Beverages & Juices'],
                'name': 'Organic Sparkling Spring Water',
                'description': 'Crisp, naturally carbonated mineral spring water with a hint of natural lime essence.',
                'price': 1.79,
                'discount_price': None,
                'stock': 40,
                'unit': 'bottle',
                'is_featured': False,
            },

            # Snacks
            {
                'category': cat_objs['Snacks & Packaged Food'],
                'name': 'Roasted Sea Salt Almonds & Cashews',
                'description': 'Gently dry-roasted premium California almonds and cashews seasoned with sea salt.',
                'price': 7.99,
                'discount_price': 6.99,
                'stock': 22,
                'unit': 'packet',
                'is_featured': True,
            },

            # Grains
            {
                'category': cat_objs['Organic Grains & Staples'],
                'name': 'Aromatic Royal Basmati Rice',
                'description': 'Aged extra long grain Himalayan basmati rice with exquisite aroma and fluffy texture.',
                'price': 12.99,
                'discount_price': 10.99,
                'stock': 30,
                'unit': 'kg',
                'is_featured': True,
            },
            {
                'category': cat_objs['Organic Grains & Staples'],
                'name': 'Organic Red Split Lentils (Masoor Dal)',
                'description': 'High-protein organic red lentils, quick to cook and rich in dietary fiber and iron.',
                'price': 3.49,
                'discount_price': 2.99,
                'stock': 4, # Low stock trigger for admin!
                'unit': 'kg',
                'is_featured': False,
            },
        ]

        created_prod_objs = []
        for pdata in products_data:
            p, _ = Product.objects.get_or_create(
                name=pdata['name'],
                category=pdata['category'],
                defaults={
                    'description': pdata['description'],
                    'price': pdata['price'],
                    'discount_price': pdata['discount_price'],
                    'stock': pdata['stock'],
                    'unit': pdata['unit'],
                    'is_available': True,
                    'is_featured': pdata['is_featured'],
                }
            )
            created_prod_objs.append(p)

        self.stdout.write(self.style.SUCCESS(f'Created/Loaded {len(created_prod_objs)} grocery products.'))

        # 5. Create Demo Orders for Analytics
        if Order.objects.count() == 0:
            now = timezone.now()
            demo_orders_data = [
                {
                    'user': customer_user,
                    'full_name': 'Sarah Miller',
                    'email': 'sarah.miller@example.com',
                    'phone': '+1 (555) 234-5678',
                    'address': '742 Evergreen Terrace, Apt 4B',
                    'city': 'Springfield',
                    'postal_code': '97477',
                    'payment_method': 'COD',
                    'payment_status': 'Pending',
                    'order_status': 'Processing',
                    'items': [
                        (created_prod_objs[0], 2), # Apples
                        (created_prod_objs[4], 1), # Milk
                        (created_prod_objs[7], 1), # Bread
                    ],
                    'days_ago': 0,
                },
                {
                    'user': customer_user,
                    'full_name': 'Sarah Miller',
                    'email': 'sarah.miller@example.com',
                    'phone': '+1 (555) 234-5678',
                    'address': '742 Evergreen Terrace, Apt 4B',
                    'city': 'Springfield',
                    'postal_code': '97477',
                    'payment_method': 'Card',
                    'payment_status': 'Paid',
                    'order_status': 'Delivered',
                    'items': [
                        (created_prod_objs[1], 3), # Spinach
                        (created_prod_objs[2], 2), # Avocados
                        (created_prod_objs[5], 2), # Eggs
                        (created_prod_objs[9], 2), # Orange juice
                    ],
                    'days_ago': 2,
                },
                {
                    'user': None,
                    'full_name': 'David Robinson',
                    'email': 'david.r@example.com',
                    'phone': '+1 (555) 987-6543',
                    'address': '1088 Meadowview Lane',
                    'city': 'Springfield',
                    'postal_code': '97478',
                    'payment_method': 'UPI',
                    'payment_status': 'Paid',
                    'order_status': 'Delivered',
                    'items': [
                        (created_prod_objs[11], 2), # Almonds
                        (created_prod_objs[12], 1), # Basmati Rice
                    ],
                    'days_ago': 4,
                }
            ]

            for odata in demo_orders_data:
                items_subtotal = sum(p.final_price * qty for p, qty in odata['items'])
                shipping_fee = 0 if items_subtotal >= 50 else 5.00
                grand_total = float(items_subtotal) + float(shipping_fee)

                order_date = now - timedelta(days=odata['days_ago'])

                order = Order.objects.create(
                    user=odata['user'],
                    full_name=odata['full_name'],
                    email=odata['email'],
                    phone=odata['phone'],
                    address=odata['address'],
                    city=odata['city'],
                    postal_code=odata['postal_code'],
                    payment_method=odata['payment_method'],
                    payment_status=odata['payment_status'],
                    order_status=odata['order_status'],
                    total_amount=items_subtotal,
                    shipping_fee=shipping_fee,
                    grand_total=grand_total,
                )
                order.created_at = order_date
                order.save()

                for prod, qty in odata['items']:
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        product_name=prod.name,
                        product_unit=prod.get_unit_display(),
                        price=prod.final_price,
                        quantity=qty,
                        subtotal=prod.final_price * qty
                    )

            self.stdout.write(self.style.SUCCESS(f'Created sample orders with historical analytics data.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
