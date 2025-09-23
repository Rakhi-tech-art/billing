from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Customer, Invoice, InvoiceItem, Payment


def dashboard(request):
    """Dashboard view showing key metrics"""
    total_customers = Customer.objects.count()
    total_invoices = Invoice.objects.count()
    pending_invoices = Invoice.objects.filter(status__in=['draft', 'sent']).count()
    total_revenue = Invoice.objects.filter(status='paid').aggregate(
        total=Sum('total_amount'))['total'] or 0

    recent_invoices = Invoice.objects.select_related('customer').order_by('-created_at')[:5]

    context = {
        'total_customers': total_customers,
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'total_revenue': total_revenue,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'billing/dashboard.html', context)


def customer_list(request):
    """List all customers"""
    customers = Customer.objects.all().order_by('name')
    return render(request, 'billing/customer_list.html', {'customers': customers})


def customer_detail(request, customer_id):
    """Show customer details and their invoices"""
    customer = get_object_or_404(Customer, id=customer_id)
    invoices = customer.invoices.all().order_by('-created_at')
    return render(request, 'billing/customer_detail.html', {
        'customer': customer,
        'invoices': invoices
    })


def invoice_list(request):
    """List all invoices"""
    invoices = Invoice.objects.select_related('customer').order_by('-created_at')
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})


def invoice_detail(request, invoice_id):
    """Show invoice details"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()
    payments = invoice.payments.all().order_by('-payment_date')
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    balance_due = invoice.total_amount - total_paid

    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
        'total_paid': total_paid,
        'balance_due': balance_due,
    }
    return render(request, 'billing/invoice_detail.html', context)


def create_invoice(request):
    """Create a new invoice"""
    if request.method == 'POST':
        # Get form data
        customer_id = request.POST.get('customer')
        invoice_number = request.POST.get('invoice_number')
        issue_date = request.POST.get('issue_date')
        due_date = request.POST.get('due_date')
        tax_rate = request.POST.get('tax_rate', 0)
        notes = request.POST.get('notes', '')

        # Create invoice
        customer = get_object_or_404(Customer, id=customer_id)
        invoice = Invoice.objects.create(
            customer=customer,
            invoice_number=invoice_number,
            issue_date=issue_date,
            due_date=due_date,
            tax_rate=tax_rate,
            notes=notes
        )

        # Add invoice items
        descriptions = request.POST.getlist('description')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')

        for desc, qty, price in zip(descriptions, quantities, unit_prices):
            if desc and qty and price:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=desc,
                    quantity=qty,
                    unit_price=price
                )

        invoice.calculate_totals()
        messages.success(request, f'Invoice {invoice_number} created successfully!')
        return redirect('invoice_detail', invoice_id=invoice.id)

    customers = Customer.objects.all().order_by('name')
    return render(request, 'billing/create_invoice.html', {'customers': customers})
