from django.urls import path, re_path
from . import views

app_name = 'store'

urlpatterns = [
    # Customer Store URLs
    path('', views.home, name='home'),
    path('index/', views.home, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('product/<str:slug>/', views.product_detail, name='product_detail'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart-view/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('order/summary/<str:order_number>/', views.order_summary, name='order_summary'),
    path('my-orders/', views.my_orders, name='my_orders'),
    
    # Custom Admin Portal URLs
    path('admin-panel/login/', views.admin_login_view, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout_view, name='admin_logout'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Admin Product Management
    path('admin-panel/products/', views.manage_products, name='manage_products'),
    path('admin-panel/products/add/', views.add_product, name='add_product'),
    path('admin-panel/products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('admin-panel/products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    
    # Admin Category Management
    path('admin-panel/categories/', views.manage_categories, name='manage_categories'),
    path('admin-panel/categories/add/', views.add_category, name='add_category'),
    path('admin-panel/categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('admin-panel/categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    
    # Admin Orders, Customers, Reports
    path('admin-panel/orders/', views.manage_orders, name='manage_orders'),
    path('admin-panel/orders/update/<int:order_id>/', views.manage_orders, name='update_order_status'),
    path('admin-panel/customers/', views.customer_details, name='customer_details'),
    path('admin-panel/sales-report/', views.sales_report, name='sales_report'),
]
