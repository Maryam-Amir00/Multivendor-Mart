from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "price", "stock", "created_at")
    list_filter = ("vendor", "created_at")
    search_fields = ("name", "vendor__username")
