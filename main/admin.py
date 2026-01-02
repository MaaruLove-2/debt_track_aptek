from django.contrib import admin
from django.utils import timezone
from .models import Pharmacist, Customer, Debt


@admin.register(Pharmacist)
class PharmacistAdmin(admin.ModelAdmin):
    list_display = ['name', 'surname', 'user', 'phone', 'email', 'created_at']
    search_fields = ['name', 'surname', 'phone', 'email', 'user__username']
    list_filter = ['created_at']
    autocomplete_fields = ['user']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['surname', 'name', 'patronymic', 'place', 'phone', 'created_at']
    search_fields = ['name', 'surname', 'patronymic', 'place', 'phone']
    list_filter = ['place', 'created_at']


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['customer', 'pharmacist', 'amount', 'date_given_display', 'promise_date', 'is_paid', 'paid_date_display', 'is_overdue_display']
    list_filter = ['is_paid', 'date_given', 'promise_date', 'pharmacist']
    search_fields = ['customer__name', 'customer__surname', 'customer__place', 'description']
    date_hierarchy = 'date_given'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Debt Information', {
            'fields': ('pharmacist', 'customer', 'amount', 'description')
        }),
        ('Dates', {
            'fields': ('date_given', 'promise_date')
        }),
        ('Payment Status', {
            'fields': ('is_paid', 'paid_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return f"Yes ({obj.days_overdue} days)"
        return "No"
    is_overdue_display.short_description = 'Overdue'
    
    def get_queryset(self, request):
        """Override to ensure timezone-aware datetimes are displayed correctly"""
        qs = super().get_queryset(request)
        return qs
    
    def date_given_display(self, obj):
        """Display date_given in local timezone"""
        if obj.date_given:
            return timezone.localtime(obj.date_given).strftime('%d.%m.%Y %H:%M')
        return '-'
    date_given_display.short_description = 'Date Given'
    
    def paid_date_display(self, obj):
        """Display paid_date in local timezone"""
        if obj.paid_date:
            return timezone.localtime(obj.paid_date).strftime('%d.%m.%Y %H:%M')
        return '-'
    paid_date_display.short_description = 'Paid Date'
