from django.forms import ModelForm
from .models import order, customer
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class OrderForm(ModelForm):
    class Meta:
        model = order
        fields = '__all__'

class CustomerForm(ModelForm):
    class Meta:
        model = customer
        fields = '__all__'

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define the styling for the input fields
        style = 'w-full pl-3 pr-10 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:border-indigo-500 bg-white/10 text-gray-700 placeholder-gray-300'
        
        # Apply styling to all fields
        for field_name in self.fields:
            autocomplete_val = 'off'
            if 'password' in field_name:
                autocomplete_val = 'new-password'
            
            self.fields[field_name].widget.attrs.update({'class': style, 'autocomplete': autocomplete_val})