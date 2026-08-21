from django import forms
from .models import Product, Category, Order

class CheckoutForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Full Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'name@example.com'
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contact phone number'
    }))
    address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Apartment, street address, locality'
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'City'
    }))
    postal_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Postal Code / PIN'
    }))
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'})
    )
    order_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Delivery instructions (e.g. Ring the doorbell, leave at gate)'
        })
    )

    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'postal_code', 'payment_method', 'order_notes']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'discount_price', 'stock', 'unit', 'image', 'is_available', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Fresh Organic Apples'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe fresh ingredients, origin, quality, etc.'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00', 'placeholder': 'Optional promo price'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '10'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'productImageInput', 'accept': 'image/*'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Product name cannot be empty.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discount_price = cleaned_data.get('discount_price')
        stock = cleaned_data.get('stock')

        if price is not None and price <= 0:
            self.add_error('price', 'Price must be greater than 0.')

        if stock is not None and stock < 0:
            self.add_error('stock', 'Stock quantity cannot be negative.')

        if discount_price is not None:
            if discount_price < 0:
                self.add_error('discount_price', 'Discount price cannot be negative.')
            elif price is not None and discount_price >= price:
                self.add_error('discount_price', 'Discount price must be less than the regular price.')

        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FontAwesome class'}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_status', 'payment_status']
        widgets = {
            'order_status': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
        }