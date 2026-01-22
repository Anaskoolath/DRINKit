from django.contrib import admin

# Register your models here.
from .models import *

class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'date_created', 'status', 'quantity')

admin.site.register(customer)
admin.site.register(product)
admin.site.register(order, OrderAdmin)
admin.site.register(company)