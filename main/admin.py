from django.contrib import admin

from main.models import Vendor, Consumer, Organization, Outlet, Campaign, Coupon, Category, Type, Interest, User


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


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    fields = ['name', 'address', 'verified', 'vendor', 'reviewed']
    list_display = ['id', 'name', 'address', 'verified', 'reviewed']
    search_fields = ['name']


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'address', 'latitude', 'longitude', 'organization']
    list_display = ['id', 'name', 'description', 'address']
    search_fields = ['name']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    fields = ['name', 'start', 'end', 'organization']
    list_distplay = ['id', 'name', 'start', 'end']
    search_fields = ['name']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    fields = ['ctype', 'category', 'campaign', 'name', 'description', 'deal', 'image', 'TC', 'amount',
              "code", "start", "end", "interests", "outlets"]
    list_distplay = ['id', 'name', 'description', 'amount', "code", "start", "end"]
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ['name', 'description']


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ['name', 'description']


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ['name', 'description']
