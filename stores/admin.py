from django.contrib import admin

from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'address')
