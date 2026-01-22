from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from . import models
from django.db.models import Q
from .forms import *
from django.forms import inlineformset_factory, modelform_factory
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.models import Group
import random

@unauthenticated_user
def login(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user=authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if user.groups.filter(name='admin').exists() or user.is_staff:
                    return redirect('home')
                else:
                    return redirect('user_home')
            else:
                messages.info(request, 'Username OR password is incorrect')
        context={}  
        return render(request,'demo/login.html' , context)

@login_required(login_url='login')
def logoutUser(request):
    auth_logout(request)
    return redirect('login')

@unauthenticated_user   
def signup(request):
        form=CreateUserForm()
        if request.method=='POST':
            form=CreateUserForm(request.POST)
            if form.is_valid():
                user=form.save()
                group=Group.objects.get(name='customers')
                user.groups.add(group)
                models.customer.objects.create(user=user, name=user.username, email=user.email)
                messages.success(request, 'Account created successfully, login to continue')
                return redirect('login')
        context={'form':form}
        return render(request,'demo/document.html',context )

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def home(request):
    products=models.product.objects.all()
    customers=models.customer.objects.all()
    orders=models.order.objects.all()
    delivered=models.order.objects.filter(status='Delivered')
    pending=models.order.objects.filter(status='Pending')
    context={
        'products':products,
        'customers':customers,
        'orders':orders,
        'delivered':delivered,
        'pending':pending,
    }
    return render(request,'demo/home.html', context)

@login_required(login_url='login')
def about(request):
    return render(request,'demo/biodata.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    cst = get_object_or_404(models.customer, id=pk)
    orders = cst.order_set.all()
    context = {
        'cst': cst,
        'orders': orders,
    }
    return render(request, 'demo/customer.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    query = request.GET.get('q')
    category_filter = request.GET.get('category')
    company_filter = request.GET.get('company')
    
    products = models.product.objects.all()
    categories = models.product.objects.values_list('category', flat=True).distinct()
    companies = models.company.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(litre__icontains=query) |
            Q(company__name__icontains=query)
        ).distinct()
    
    if category_filter:
        products = products.filter(category=category_filter)
    
    if company_filter:
        # Support passing either a company id or a name substring
        try:
            cid = int(company_filter)
            products = products.filter(company__id=cid)
        except (ValueError, TypeError):
            products = products.filter(company__name__icontains=company_filter)
        products = products.distinct()

    context = {
        'products': products,
        'query': query,
        'categories': categories,
        'companies': companies,
        'selected_category': category_filter,
        'selected_company': company_filter
    }
    return render(request,'demo/products.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def create_product(request):
    ProductForm = modelform_factory(models.product, fields='__all__')
    form = ProductForm()
    if request.method == 'POST':
        next_url = request.POST.get('next', 'products')
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect(next_url)
    
    context = {'form': form, 'next': request.GET.get('next', 'products')}
    return render(request, 'demo/create_Product.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','customers'])
def create_order(request, pk=None):
    initial_data = {}
    product = None
    if pk:
        product = get_object_or_404(models.product, id=pk)
        initial_data['product'] = product
    if hasattr(request.user, 'customer'):
        initial_data['customer'] = request.user.customer

    form = OrderForm(initial=initial_data)
    if request.method == 'POST':
        data = request.POST.copy()
        if pk:
            data['product'] = pk
        if hasattr(request.user, 'customer'):
            data['customer'] = request.user.customer.id
        if 'status' not in data or not data['status']:
            data['status'] = 'Pending'

        form = OrderForm(data)
        if form.is_valid():
            order_instance = form.save(commit=False)
            if request.POST.get('quantity'):
                order_instance.quantity = request.POST.get('quantity')
            order_instance.save()
            messages.success(request, f'Order for {order_instance.product.name} created successfully!')
            next_url = request.POST.get('next', '/home')
            return redirect(next_url)
        else:
            print('Form errors:', form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    context={'form':form, 'product':product, 'next': request.GET.get('next', '/home')}
    return render( request,'demo/create_order.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def create_customer(request):
    form = CustomerForm()
    if request.method == 'POST':
        next_url = request.POST.get('next', '/home')
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer_instance = form.save()
            messages.success(request, f'Customer {customer_instance.name} added successfully!')
            return redirect(next_url) 
    context={'form':form, 'next': request.GET.get('next', '/home')}
    return render( request,'demo/create_Customer.html',context)

@login_required(login_url='login')
def update_order(request, pk):
    order_instance = get_object_or_404(models.order, id=pk)

    # Customers may only edit their own orders
    if not request.user.is_superuser and hasattr(request.user, 'customer'):
        if order_instance.customer != request.user.customer:
            messages.error(request, 'You do not have permission to edit this order.')
            return redirect('user_home')

    # Use the full form for superusers; restrict to product & quantity for others
    if request.user.is_superuser:
        FormClass = OrderForm
    else:
        FormClass = modelform_factory(models.order, fields=('product', 'quantity'))

    # Prioritize GET parameter for initial page load, POST for form submission
    next_url = request.GET.get('next', '/home')

    if request.method == 'POST':
        next_url = request.POST.get('next', '/home')
        form = FormClass(request.POST, instance=order_instance)

        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated successfully!')
            return redirect(next_url)
    else:
        form = FormClass(instance=order_instance)

    return render(request, 'demo/update_Order.html', {'form': form, 'order': order_instance, 'next': next_url})

@login_required(login_url='login')
def delete_order(request, pk):
    order_instance = get_object_or_404(models.order, id=pk)
    next_url = request.GET.get('next', '/home')

    if request.method == 'POST':
        next_url = request.POST.get('next', '/home')
        order_instance.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect(next_url)

    return render(request, 'demo/delete_Order.html', {'order': order_instance, 'next': next_url})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def all_customers(request):
    query = request.GET.get('q')
    if query:
        customers = models.customer.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        ).order_by('name')
    else:
        customers = models.customer.objects.all().order_by('name')
    
    context = {'customers': customers, 'query': query}
    return render(request, 'demo/all_customers.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','customers'])
def all_orders(request, pk=None):
    query = request.GET.get('q')
    if pk:
        cst = get_object_or_404(models.customer, id=pk)
        orders = cst.order_set.all()
    else:
        if request.user.is_staff or request.user.groups.filter(name='admin').exists():
            orders = models.order.objects.all()
        elif hasattr(request.user, 'customer'):
            orders = request.user.customer.order_set.all()
        else:
            orders = models.order.objects.none()

    if query:
        orders = orders.filter(
            Q(product__name__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(status__icontains=query)
        )
    
    orders = orders.order_by('-date_created')

    myFilter = OrderFilter(request.GET, queryset=orders)
    Orders = myFilter.qs

    context = {'orders': Orders, 'query': query, 'myFilter': myFilter}
    return render(request, 'demo/all_orders.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','customers'])
def create_order_bulk(request,pk):
    order_bulk=inlineformset_factory(models.customer, models.order, fields=('product', 'quantity'), extra=5)
    customer = get_object_or_404(models.customer, id=pk)
    next_url = request.GET.get('next', '/home')


    if request.method == 'POST':
        next_url = request.POST.get('next', '/home')
        formset = order_bulk(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            messages.success(request, f'Orders for {customer.name} created successfully!')
            return redirect(next_url)
    else:
        formset=order_bulk(queryset=models.order.objects.none(), instance=customer)
    
    context={'formset':formset, 'next': next_url}
    return render( request,'demo/create_order_bulk.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','customers'])
def update_customer(request, pk):
    customer_instance = get_object_or_404(models.customer,id=pk)
    # Prioritize GET parameter for initial page load, POST for form submission
    next_url = request.GET.get('next', '/user')

    if request.method == 'POST':
        next_url = request.POST.get('next', '/user')
        form = CustomerForm(request.POST, request.FILES, instance=customer_instance)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer '+customer_instance.name+' updated successfully!')
            return redirect(next_url)
    else:
        form = CustomerForm(instance=customer_instance)

    return render(request, 'demo/update_Customer.html', {'form': form, 'customer': customer_instance, 'next': next_url})

@login_required(login_url='login')
@allowed_users(allowed_roles=['customers','admin'])
def user(request):
    orders = models.order.objects.none()
    orders_delivered = 0
    orders_pending = 0
    cst = None

    if hasattr(request.user, 'customer'):
        orders= request.user.customer.order_set.all()
        cst= request.user.customer.id
        orders_delivered = orders.filter(status='Delivered').count()
        orders_pending = orders.filter(status='Pending').count()

    # Fetch products for the user home page
    query = request.GET.get('q')
    products = models.product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    context={
        'cst' : cst,
        'orders':orders,
        'orders_delivered':orders_delivered,
        'orders_pending':orders_pending,
        'products': products,
        'query': query,
    }
    return render(request,'demo/user.html',context)

def user_home(request):
    orders = models.order.objects.none()
    orders_delivered = 0
    orders_pending = 0
    cst = None

    if hasattr(request.user, 'customer'):
        orders= request.user.customer.order_set.all()
        cst= request.user.customer.id
        orders_delivered = orders.filter(status='Delivered').count()
        orders_pending = orders.filter(status='Pending').count()

    # Fetch products for the user home page
    query = request.GET.get('q')
    # support either ?company= or ?brand=
    company = request.GET.get('company')
    ids = models.product.objects.values_list('id', flat=True)
    random_ids = random.sample(list(ids), min(18, len(ids)))
    random_products = models.product.objects.filter(id__in=random_ids)
    products = random_products
    ids1 = models.product.objects.values_list('id', flat=True)
    random_ids1 = random.sample(list(ids1), min(4, len(ids1)))
    random_products1 = models.product.objects.filter(id__in=random_ids1)
    featured = random_products1

    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(category__icontains=query) |
            Q(litre__icontains=query) |
            Q(company__name__icontains=query)
        ).distinct()

    # Filter by company/brand if provided (support id or name)
    if company:
        try:
            cid = int(company)
            products = products.filter(company__id=cid)
        except (ValueError, TypeError):
            products = products.filter(company__name__icontains=company)
        products = products.distinct()

    companies = models.company.objects.all()

    context={
        'cst' : cst,
        'orders':orders,
        'orders_delivered':orders_delivered,
        'orders_pending':orders_pending,
        'products': products,
        'query': query,
        'company': company,
        'companies': companies,
        'featured': featured,
    }
    return render(request,'demo/user_home.html',context)