from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Save phone in profile
            phone = form.cleaned_data.get('phone')
            if phone:
                user.profile.phone = phone
                user.profile.save()
                
            messages.success(request, f"Welcome to FreshCart, {user.first_name or user.username}! Your account was created successfully.")
            login(request, user)
            return redirect('store:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()
        
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
        
    next_url = request.GET.get('next', 'store:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url if next_url and next_url != 'None' else 'store:home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('store:home')

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please resolve the errors below.")
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        form = UserProfileForm(instance=profile, initial=initial_data)
        
    return render(request, 'accounts/profile.html', {'form': form, 'user': user})