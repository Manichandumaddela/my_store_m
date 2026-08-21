from django.db.models import Sum
from .models import Category, Cart

def _get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart

def cart_processor(request):
    try:
        cart = _get_cart(request)
        item_count = sum(item.quantity for item in cart.items.all())
        subtotal = cart.subtotal
        return {
            'cart': cart,
            'cart_obj': cart,
            'cart_count': item_count,
            'cart_item_count': item_count,
            'cart_subtotal': subtotal,
        }
    except Exception:
        return {
            'cart': None,
            'cart_obj': None,
            'cart_count': 0,
            'cart_item_count': 0,
            'cart_subtotal': 0,
        }

def category_processor(request):
    try:
        categories = Category.objects.all()
        return {
            'global_categories': categories,
        }
    except Exception:
        return {
            'global_categories': [],
        }