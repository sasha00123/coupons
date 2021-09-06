from django.contrib import admin

# Register your models here.
from main.models import User, Vendor, Consumer


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ['username', 'email', 'password', 'atype', 'is_staff', 'is_superuser']
    list_display = ['id', 'username', 'email', 'atype', 'is_superuser']
    search_fields = ['username', 'email']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    fields = ['verified', 'user', 'restricted']
    list_display = ['id', 'user', 'verified', 'restricted']


@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    fields = ['full_name', 'birth_date', 'user']
    list_display = ['id', 'full_name', 'birth_date']
    search_fields = ['full_name']

