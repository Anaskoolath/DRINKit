"""
URL configuration for crm_1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views



urlpatterns = [
    path('',views.login,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('signup/',views.signup,name='signup'),
    path('home/',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('products/',views.products,name='products'),
    path('create_product/', views.create_product, name='create_product'),
    path('customer/<int:pk>/',views.customer,name='customer'),
    path('create_order/<int:pk>/',views.create_order,name='create_order'),
    path('create_order/',views.create_order,name='create_order'),
    path('create_customer/',views.create_customer,name='create_customer'),
    path('update_order/<int:pk>/',views.update_order,name='update_order'),
    path('delete_order/<int:pk>/',views.delete_order,name='delete_order'),
    path('all_customers/', views.all_customers, name='all_customers'),
    path('all_orders/', views.all_orders, name='all_orders'),
    path('all_orders/<int:pk>/', views.all_orders, name='all_orders'),
    path('create_order_bulk/<int:pk>/',views.create_order_bulk,name='create_order_bulk'),
    path('update_customer/<int:pk>/',views.update_customer,name='update_customer'),
    path('user/',views.user,name='user'),
    path('user_home/',views.user_home,name='user_home'),
]