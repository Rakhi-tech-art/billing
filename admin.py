from django.contrib import admin
from .models import Customer, Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    """Inline admin for invoice items"""
    model = InvoiceItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('total_price',)


class PaymentInline(admin.TabularInline):
    """Inline admin for payments"""
    model = Payment
    extra = 0
    fields = ('amount', 'payment_date', 'payment_method', 'reference_number')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin configuration for Customer model"""
    list_display = ('name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Invoice model"""
    list_display = ('invoice_number', 'customer', 'issue_date', 'due_date', 'status', 'total_amount')
    list_filter = ('status', 'issue_date', 'due_date', 'created_at')
    search_fields = ('invoice_number', 'customer__name', 'customer__email')
    readonly_fields = ('subtotal', 'tax_amount', 'total_amount', 'created_at', 'updated_at')
    inlines = [InvoiceItemInline, PaymentInline]

    fieldsets = (
        (None, {
            'fields': ('customer', 'invoice_number', 'issue_date', 'due_date', 'status')
        }),
        ('Tax Information', {
            'fields': ('tax_rate', 'tax_amount'),
        }),
        ('Totals', {
            'fields': ('subtotal', 'total_amount'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Override save to recalculate totals"""
        super().save_model(request, obj, form, change)
        obj.calculate_totals()


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """Admin configuration for InvoiceItem model"""
    list_display = ('description', 'invoice', 'quantity', 'unit_price', 'total_price')
    list_filter = ('invoice__status', 'invoice__issue_date')
    search_fields = ('description', 'invoice__invoice_number', 'invoice__customer__name')
    readonly_fields = ('total_price',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model"""
    list_display = ('invoice', 'amount', 'payment_date', 'payment_method', 'reference_number')
    list_filter = ('payment_method', 'payment_date', 'created_at')
    search_fields = ('invoice__invoice_number', 'invoice__customer__name', 'reference_number')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('invoice', 'amount', 'payment_date', 'payment_method')
        }),
        ('Additional Information', {
            'fields': ('reference_number', 'notes'),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
