from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "image"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border px-3 py-2 rounded-lg"}),
            "description": forms.Textarea(attrs={"class": "w-full border px-3 py-2 rounded-lg", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "w-full border px-3 py-2 rounded-lg"}),
            "stock": forms.NumberInput(attrs={"class": "w-full border px-3 py-2 rounded-lg"}),
        }
