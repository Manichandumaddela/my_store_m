from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, F, Avg
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta, datetime
import json

from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm, ProductForm, CategoryForm, OrderStatusForm
from accounts.models import UserProfile

# Helper function to get or create cart
def _get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart

# Merge session cart into user cart on login
def merge_cart(request, user):
    session_key = request.session.session_key
    if session_key:
        try:
            session_cart = Cart.objects.get(session_key=session_key)
            user_cart, _ = Cart.objects.get_or_create(user=user)
            for item in session_cart.items.all():
                user_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=item.product,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    user_item.quantity += item.quantity
                    user_item.save()
            session_cart.delete()
        except Cart.DoesNotExist:
            pass

# Custom Admin Check
def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ==========================================
# CUSTOMER VIEWS
# ==========================================

def home(request):
    if request.GET.get('q') or request.GET.get('search') or request.GET.get('category') or request.GET.get('sort') or request.GET.get('min_price') or request.GET.get('max_price'):
        return product_list(request)

    products = Product.objects.filter(is_available=True)[:12]
    featured_products = Product.objects.filter(is_available=True, is_featured=True)[:8]
    latest_products = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    discounted_products = Product.objects.filter(is_available=True, discount_price__isnull=False, discount_price__gt=0)[:8]
    categories = Category.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)
    
    context = {
        'products': products,
        'featured_products': featured_products,
        'latest_products': latest_products,
        'discounted_products': discounted_products,
        'categories': categories,
    }
    return render(request, 'store/product_list.html', context)


def product_list(request):
    query = request.GET.get('q', request.GET.get('search', '')).strip()
    category_slug = request.GET.get('category', '').strip()
    sort_by = request.GET.get('sort', 'newest')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    products = Product.objects.filter(is_available=True)
    selected_category = None

    if category_slug:
        if category_slug.isdigit():
            selected_category = get_object_or_404(Category, id=int(category_slug))
        else:
            selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(unit__icontains=query)
        )

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if sort_by == 'price-asc':
        products = products.order_by('price')
    elif sort_by == 'price-desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()

    context = {
        'products': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'search_query': query,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'total_count': products.count(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    if str(slug).isdigit():
        product = get_object_or_404(Product, id=int(slug))
    else:
        product = get_object_or_404(Product, slug=slug)
        
    related_products = Product.objects.filter(category=product.category, is_available=True).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def cart_view(request):
    cart = _get_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('store:product_list')

    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    if not product.in_stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'This product is out of stock!'}, status=400)
        messages.error(request, 'Sorry, this product is out of stock!')
        return redirect('store:product_detail', slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        if cart_item.quantity + quantity > product.stock:
            cart_item.quantity = product.stock
            cart_item.save()
            msg = f"Only {product.stock} items available in stock."
        else:
            cart_item.quantity += quantity
            cart_item.save()
            msg = f"Updated {product.name} quantity to {cart_item.quantity} in cart!"
    else:
        cart_item.quantity = min(quantity, product.stock)
        cart_item.save()
        msg = f"Added {product.name} to your cart!"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': msg,
            'cart_count': cart.total_items,
            'subtotal': float(cart.subtotal),
            'grand_total': float(cart.grand_total),
        })

    messages.success(request, msg)
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer) if referer else redirect(reverse('store:cart'))


def update_cart(request, item_id):
    cart = _get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    action = request.POST.get('action')
    quantity = request.POST.get('quantity')

    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, f"Maximum available stock is {cart_item.product.stock}.")
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    elif action == 'remove':
        cart_item.delete()
    elif quantity:
        try:
            qty = int(quantity)
            if qty <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = min(qty, cart_item.product.stock)
                cart_item.save()
        except ValueError:
            pass

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item_subtotal = float(cart_item.subtotal) if cart_item.id else 0
        return JsonResponse({
            'status': 'success',
            'cart_count': cart.total_items,
            'item_quantity': cart_item.quantity if cart_item.id else 0,
            'item_subtotal': item_subtotal,
            'subtotal': float(cart.subtotal),
            'shipping_fee': float(cart.shipping_fee),
            'grand_total': float(cart.grand_total),
        })

    return redirect('store:cart')


def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f"Removed {product_name} from cart.",
            'cart_count': cart.total_items,
            'subtotal': float(cart.subtotal),
            'shipping_fee': float(cart.shipping_fee),
            'grand_total': float(cart.grand_total),
        })

    messages.info(request, f"Removed {product_name} from cart.")
    return redirect('store:cart')


def clear_cart(request):
    cart = _get_cart(request)
    cart.items.all().delete()
    messages.info(request, "Your shopping cart has been cleared.")
    return redirect('store:cart')


def checkout(request):
    cart = _get_cart(request)
    if cart.total_items == 0:
        messages.warning(request, "Your cart is empty. Add products before checking out.")
        return redirect('store:product_list')

    initial_data = {}
    if request.user.is_authenticated:
        user = request.user
        initial_data = {
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'email': user.email,
        }
        if hasattr(user, 'profile'):
            initial_data.update({
                'phone': user.profile.phone or '',
                'address': user.profile.address or '',
                'city': user.profile.city or '',
                'postal_code': user.profile.postal_code or '',
            })

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
                
            order.total_amount = cart.subtotal
            order.shipping_fee = cart.shipping_fee
            order.grand_total = cart.grand_total
            order.order_status = 'Pending'
            order.payment_status = 'Pending' if order.payment_method == 'COD' else 'Paid'
            order.save()

            # Create OrderItems and decrement stock
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_unit=item.product.get_unit_display(),
                    price=item.product.final_price,
                    quantity=item.quantity,
                    subtotal=item.subtotal,
                )
                # Deduct stock
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save()

            # Clear cart
            cart.items.all().delete()

            messages.success(request, f"Thank you! Your order {order.order_number} has been placed successfully.")
            return redirect('store:order_summary', order_number=order.order_number)
        else:
            messages.error(request, "Please fix the errors in the checkout form.")
    else:
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart.items.all(),
    }
    return render(request, 'store/checkout.html', context)


def order_summary(request, order_number):
    if str(order_number).isdigit():
        order = get_object_or_404(Order, id=int(order_number))
    else:
        order = get_object_or_404(Order, order_number=order_number)
    
    # Restrict viewing to order owner if authenticated
    if order.user and request.user.is_authenticated and order.user != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to view this order.")
        return redirect('store:home')

    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'store/order_summary.html', context)


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'store/my_orders.html', context)


# ==========================================
# CUSTOM ADMIN PORTAL VIEWS
# ==========================================

def admin_login_view(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('store:admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            messages.success(request, f"Welcome back to Admin Portal, {user.username}!")
            return redirect('store:admin_dashboard')
        else:
            messages.error(request, "Invalid administrator credentials or unauthorized account.")
    return render(request, 'store/admin/admin_login.html')


def admin_logout_view(request):
    logout(request)
    messages.info(request, "Administrator logged out successfully.")
    return redirect('store:admin_login')


@user_passes_test(is_admin_user, login_url='store:admin_login')
def admin_dashboard(request):
    total_revenue = Order.objects.filter(payment_status='Paid').aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status='Pending').count()
    delivered_orders = Order.objects.filter(order_status='Delivered').count()
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=5)
    total_customers = User.objects.filter(is_staff=False).count()
    recent_orders = Order.objects.all().order_by('-created_at')[:8]

    # Revenue for last 7 days chart
    today = timezone.now().date()
    daily_sales = []
    days_labels = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_sales = Order.objects.filter(
            created_at__date=day, payment_status='Paid'
        ).aggregate(Sum('grand_total'))['grand_total__sum'] or 0
        days_labels.append(day.strftime('%b %d'))
        daily_sales.append(float(day_sales))

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products[:5],
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'days_labels_json': json.dumps(days_labels),
        'daily_sales_json': json.dumps(daily_sales),
    }
    return render(request, 'store/admin/admin_dashboard.html', context)


@user_passes_test(is_admin_user, login_url='store:admin_login')
def manage_products(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock_status', '')

    products = Product.objects.all().select_related('category')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(unit__icontains=query)
        )
    if category_id:
        products = products.filter(category_id=category_id)
    if stock_status == 'low':
        products = products.filter(stock__lte=5, stock__gt=0)
    elif stock_status == 'out':
        products = products.filter(stock=0)

    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()

    context = {
        'products': page_obj,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'stock_status': stock_status,
        'total_count': products.count(),
    }
    return render(request, 'store/admin/manage_products.html', context)


@user_passes_test(is_admin_user, login_url='store:admin_login')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' was created successfully!")
            return redirect('store:manage_products')
        else:
            error_list = []
            for field, errors in form.errors.items():
                for err in errors:
                    if field == '__all__':
                        error_list.append(str(err))
                    else:
                        field_name = form.fields[field].label or field.replace('_', ' ').title() if field in form.fields else field
                        error_list.append(f"{field_name}: {err}")
            messages.error(request, "Failed to create product. " + " | ".join(error_list) if error_list else "Please correct the errors in the form.")
    else:
        form = ProductForm()

    return render(request, 'store/admin/add_product.html', {'form': form})


@user_passes_test(is_admin_user, login_url='store:admin_login')
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('store:manage_products')
        else:
            error_list = []
            for field, errors in form.errors.items():
                for err in errors:
                    if field == '__all__':
                        error_list.append(str(err))
                    else:
                        field_name = form.fields[field].label or field.replace('_', ' ').title() if field in form.fields else field
                        error_list.append(f"{field_name}: {err}")
            messages.error(request, "Failed to update product. " + " | ".join(error_list) if error_list else "Please correct the errors in the form.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'store/admin/edit_product.html', {'form': form, 'product': product})


@user_passes_test(is_admin_user, login_url='store:admin_login')
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' deleted successfully.")
        return redirect('store:manage_products')
    return render(request, 'store/admin/delete_product.html', {'product': product})


@user_passes_test(is_admin_user, login_url='store:admin_login')
def manage_categories(request):
    categories = Category.objects.annotate(
        prod_count=Count('products'),
        total_stock=Sum('products__stock')
    ).all()
    return render(request, 'store/admin/manage_categories.html', {'categories': categories})


@user_passes_test(is_admin_user, login_url='store:admin_login')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Category '{cat.name}' added successfully!")
            return redirect('store:manage_categories')
    else:
        form = CategoryForm()
    return render(request, 'store/admin/add_category.html', {'form': form})


@user_passes_test(is_admin_user, login_url='store:admin_login')
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Category '{cat.name}' updated successfully!")
            return redirect('store:manage_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'store/admin/edit_category.html', {'form': form, 'category': category})


@user_passes_test(is_admin_user, login_url='store:admin_login')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' and associated products deleted.")
        return redirect('store:manage_categories')
    return render(request, 'store/admin/delete_category.html', {'category': category})


@user_passes_test(is_admin_user, login_url='store:admin_login')
def manage_orders(request, order_id=None):
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '').strip()

    # Handle status update inline POST
    if request.method == 'POST':
        oid = order_id or request.POST.get('order_id')
        new_status = request.POST.get('order_status') or request.POST.get('status')
        new_payment = request.POST.get('payment_status')
        if oid:
            target_order = get_object_or_404(Order, id=oid)
            if new_status:
                target_order.order_status = new_status
            if new_payment:
                target_order.payment_status = new_payment
            target_order.save()
            messages.success(request, f"Order #{target_order.order_number} status updated to {target_order.order_status}.")
            return redirect(request.META.get('HTTP_REFERER', 'store:manage_orders'))

    orders = Order.objects.all().prefetch_related('items')

    if status_filter:
        orders = orders.filter(order_status=status_filter)
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    paginator = Paginator(orders, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'status_filter': status_filter,
        'query': query,
        'status_choices': Order.STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'store/admin/manage_orders.html', context)


@user_passes_test(is_admin_user, login_url='store:admin_login')
def customer_details(request):
    customers = User.objects.filter(is_staff=False).annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__grand_total')
    ).select_related('profile').order_by('-date_joined')

    context = {
        'customers': customers,
        'total_customers': customers.count(),
    }
    return render(request, 'store/admin/customer_details.html', context)


@user_passes_test(is_admin_user, login_url='store:admin_login')
def sales_report(request):
    period = request.GET.get('period', 'monthly')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    orders = Order.objects.filter(order_status__in=['Processing', 'Shipped', 'Delivered'])

    today = timezone.now().date()
    if period == 'daily':
        orders = orders.filter(created_at__date=today)
    elif period == 'weekly':
        orders = orders.filter(created_at__date__gte=today - timedelta(days=7))
    elif period == 'monthly':
        orders = orders.filter(created_at__date__gte=today - timedelta(days=30))
    elif period == 'yearly':
        orders = orders.filter(created_at__date__gte=today - timedelta(days=365))
    elif period == 'custom' and start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__range=[start_date, end_date])
        except ValueError:
            pass

    total_revenue = orders.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_orders = orders.count()
    avg_order_value = (total_revenue / total_orders) if total_orders > 0 else 0

    top_products = OrderItem.objects.filter(order__in=orders).values(
        'product_name'
    ).annotate(
        units_sold=Sum('quantity'),
        revenue=Sum('subtotal')
    ).order_by('-units_sold')[:10]

    context = {
        'period': period,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'orders': orders.order_by('-created_at')[:25],
        'top_products': top_products,
    }
    return render(request, 'store/admin/sales_report.html', context)