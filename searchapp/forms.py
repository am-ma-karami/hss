from django import forms
from .models import Product

class SearchForm(forms.Form):
    query = forms.CharField(required=False, label='Search')
    min_price = forms.FloatField(required=False, label='Min Price')
    max_price = forms.FloatField(required=False, label='Max Price')
    category = forms.CharField(required=False, label='Category')
    brand = forms.CharField(required=False, label='Brand')
    in_stock = forms.BooleanField(required=False, label='In Stock')