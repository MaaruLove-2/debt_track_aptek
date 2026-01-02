import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Sum, Q
from .models import Cashier, Customer, Debt, Payment
from .forms import CashierForm, CustomerForm, DebtForm, DebtEditForm, CustomerImportForm, SimplifiedCustomerForm, PaymentForm
from .utils import parse_csv_file, parse_excel_file, import_customers_from_data


def login_view(request):
    """Login page for cashiers and admins"""
    # Always logout user when accessing login page to ensure fresh login
    if request.user.is_authenticated:
        auth_logout(request)
        messages.info(request, _('Çıxış edildi. Zəhmət olmasa yenidən daxil olun.'))
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, _('Uğurla daxil oldunuz!'))
            # Redirect based on user type
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            # Check if regular user has cashier profile
            try:
                cashier = user.cashier_profile
                return redirect('home')
            except Cashier.DoesNotExist:
                messages.error(request, _('Bu istifadəçi kassir profili yoxdur. Zəhmət olmasa administratorla əlaqə saxlayın.'))
                auth_logout(request)
                return redirect('login')
        else:
            messages.error(request, _('İstifadəçi adı və ya parol səhvdir.'))
    
    return render(request, 'main/login.html')


def logout_view(request):
    """Logout view"""
    auth_logout(request)
    messages.success(request, _('Uğurla çıxış etdiniz.'))
    return redirect('login')


@login_required
def get_current_cashier(request):
    """Helper function to get current cashier from logged-in user"""
    try:
        return request.user.cashier_profile
    except Cashier.DoesNotExist:
        return None


@login_required
def home(request):
    """Home page with overview of debts"""
    # If user is admin/staff, redirect to admin dashboard
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard')
    
    cashier = get_current_cashier(request)
    if not cashier:
        messages.error(request, _('Kassir profili tapılmadı. Zəhmət olmasa administratorla əlaqə saxlayın.'))
        auth_logout(request)
        return redirect('login')
    
    today = timezone.now().date()
    from datetime import datetime
    from calendar import monthrange
    
    # Get current month start and end dates
    current_month_start = today.replace(day=1)
    last_day = monthrange(today.year, today.month)[1]
    current_month_end = today.replace(day=last_day)
    
    # Convert to datetime for filtering
    month_start_datetime = timezone.make_aware(datetime.combine(current_month_start, datetime.min.time()))
    month_end_datetime = timezone.make_aware(datetime.combine(current_month_end, datetime.max.time()))
    
    # Monthly statistics - debts given this month
    monthly_given = Debt.objects.filter(
        cashier=cashier,
        date_given__gte=month_start_datetime,
        date_given__lte=month_end_datetime
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Monthly statistics - payments/returns this month (partial + full)
    monthly_partial_payments = Payment.objects.filter(
        debt__cashier=cashier,
        payment_date__gte=month_start_datetime,
        payment_date__lte=month_end_datetime
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Full payments (debts fully paid this month, excluding those with partial payments)
    monthly_full_payments = Debt.objects.filter(
        cashier=cashier,
        is_paid=True,
        paid_date__gte=month_start_datetime,
        paid_date__lte=month_end_datetime
    ).exclude(
        id__in=Payment.objects.filter(
            payment_date__gte=month_start_datetime,
            payment_date__lte=month_end_datetime
        ).values_list('debt_id', flat=True).distinct()
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_returned = monthly_partial_payments + monthly_full_payments
    monthly_balance = monthly_given - monthly_returned
    
    # Get statistics for current cashier only
    # Prefetch payments to calculate remaining_amount correctly
    unpaid_debts = Debt.objects.filter(cashier=cashier, is_paid=False).select_related('customer').prefetch_related('payments')
    unpaid_debts_list = list(unpaid_debts)  # Evaluate queryset once
    total_debts = len(unpaid_debts_list)
    
    # Calculate total remaining amount (not total amount)
    total_amount = sum(debt.remaining_amount for debt in unpaid_debts_list)
    
    overdue_debts_qs = Debt.objects.filter(
        cashier=cashier,
        is_paid=False,
        promise_date__lt=today
    ).select_related('customer').prefetch_related('payments')
    overdue_debts_list = list(overdue_debts_qs)  # Evaluate queryset once
    overdue_count = len(overdue_debts_list)
    
    # Calculate overdue remaining amount (not total amount)
    overdue_amount = sum(debt.remaining_amount for debt in overdue_debts_list)
    
    # Recent debts for current cashier
    recent_debts = Debt.objects.filter(cashier=cashier, is_paid=False).order_by('-date_given')[:10]
    
    # Overdue debts for current cashier
    overdue_debts_list = Debt.objects.filter(
        cashier=cashier,
        is_paid=False,
        promise_date__lt=today
    ).order_by('promise_date')[:10]
    
    context = {
        'cashier': cashier,
        'total_debts': total_debts,
        'total_amount': total_amount,
        'overdue_debts': overdue_count,
        'overdue_amount': overdue_amount,
        'recent_debts': recent_debts,
        'overdue_debts_list': overdue_debts_list,
        'monthly_given': monthly_given,
        'monthly_returned': monthly_returned,
        'monthly_balance': monthly_balance,
    }
    
    return render(request, 'main/home.html', context)


@login_required
def debt_list(request):
    """List all debts with filtering options"""
    # If admin/staff, redirect to admin all debts
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_all_debts')
    
    cashier = get_current_cashier(request)
    if not cashier:
        messages.error(request, _('Kassir profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    # Only show open (unpaid) debts for current cashier by default
    debts = Debt.objects.filter(cashier=cashier, is_paid=False).select_related('cashier', 'customer')
    
    # Filter by status (only if explicitly requested)
    status = request.GET.get('status')
    if status == 'paid':
        # Show paid debts only if explicitly requested
        debts = Debt.objects.filter(cashier=cashier, is_paid=True).select_related('cashier', 'customer')
    elif status == 'overdue':
        today = timezone.now().date()
        debts = debts.filter(is_paid=False, promise_date__lt=today)
    elif status == 'all':
        # Show all debts (paid and unpaid) if explicitly requested
        debts = Debt.objects.filter(cashier=cashier).select_related('cashier', 'customer')
    # Default: show only unpaid (open) debts
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        debts = debts.filter(
            Q(customer__name__icontains=search) |
            Q(customer__surname__icontains=search) |
            Q(customer__place__icontains=search) |
            Q(description__icontains=search)
        )
    
    context = {
        'debts': debts,
        'selected_status': status,
        'search_query': search if search else '',
    }
    
    return render(request, 'main/debt_list.html', context)


@login_required
def debt_add(request):
    """Add a new debt with simplified customer creation"""
    # Admin/staff users need to select a cashier, so redirect to admin dashboard
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, _('Admin istifadəçiləri borc əlavə etmək üçün kassir seçməlidir. Admin paneldən istifadə edin.'))
        return redirect('admin_dashboard')
    
    cashier = get_current_cashier(request)
    if not cashier:
        messages.error(request, _('Kassir profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    if request.method == 'POST':
        form = DebtForm(request.POST, cashier=cashier)
        
        customer_id = request.POST.get('customer_id', '').strip()
        customer_input = request.POST.get('customer_input', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        customer = None
        
        # If customer_id is provided, use existing customer
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                messages.error(request, _('Müştəri tapılmadı.'))
                form = DebtForm(cashier=cashier)
                return render(request, 'main/debt_add.html', {
                    'form': form
                })
        elif customer_input:
            # Validate phone is provided for new customers
            if not phone:
                messages.error(request, _('Yeni müştəri üçün telefon nömrəsi mütləqdir.'))
                form = DebtForm(cashier=cashier)
                return render(request, 'main/debt_add.html', {
                    'form': form
                })
            
            # Parse customer_input: "Name Surname Place" or "Surname Name Place"
            parts = customer_input.split()
            if len(parts) >= 3:
                # Last part is place
                place = parts[-1]
                # First two parts are name and surname
                name = parts[0]
                surname = parts[1] if len(parts) > 1 else ''
            elif len(parts) == 2:
                name = parts[0]
                surname = parts[1]
                place = 'Unknown'
            else:
                name = parts[0] if parts else ''
                surname = ''
                place = 'Unknown'
            
            # Try to find existing customer first
            customer = Customer.objects.filter(
                name=name,
                surname=surname,
                place=place
            ).first()
            
            # If not found, create new customer
            if not customer:
                customer = Customer.objects.create(
                    name=name,
                    surname=surname,
                    patronymic=None,
                    place=place,
                    phone=phone
                )
                messages.success(request, _('Yeni müştəri avtomatik yaradıldı: {customer}').format(customer=customer))
            else:
                # Update phone if provided and customer doesn't have one
                if phone and not customer.phone:
                    customer.phone = phone
                    customer.save()
        
        if not customer:
            messages.error(request, _('Zəhmət olmasa müştəri adını daxil edin.'))
            form = DebtForm(cashier=cashier)
            return render(request, 'main/debt_add.html', {
                'form': form
            })
        
        # Create debt with this customer
        try:
            # Use form's cleaned_data if available, otherwise parse from POST or use current time
            date_given = None
            if form.is_valid() and 'date_given' in form.cleaned_data:
                date_given = form.cleaned_data['date_given']
            else:
                # Try to get from POST data
                date_given_str = request.POST.get('date_given')
                if date_given_str:
                    from datetime import datetime as dt
                    # Try to parse different date formats
                    try:
                        # Format: YYYY-MM-DDTHH:MM (datetime-local input)
                        naive_dt = dt.strptime(date_given_str, '%Y-%m-%dT%H:%M')
                        date_given = timezone.make_aware(naive_dt)
                    except ValueError:
                        try:
                            # Format: YYYY-MM-DD HH:MM:SS.microseconds (already parsed datetime)
                            naive_dt = dt.strptime(date_given_str, '%Y-%m-%d %H:%M:%S.%f')
                            date_given = timezone.make_aware(naive_dt)
                        except ValueError:
                            try:
                                # Format: YYYY-MM-DD HH:MM:SS (without microseconds)
                                naive_dt = dt.strptime(date_given_str, '%Y-%m-%d %H:%M:%S')
                                date_given = timezone.make_aware(naive_dt)
                            except ValueError:
                                # If all parsing fails, use current time
                                date_given = timezone.now()
                else:
                    date_given = timezone.now()
            
            # Ensure date_given is timezone-aware
            if date_given and timezone.is_naive(date_given):
                date_given = timezone.make_aware(date_given)
            
            debt = Debt(
                cashier=cashier,
                customer=customer,
                amount=request.POST.get('amount'),
                date_given=date_given,
                promise_date=request.POST.get('promise_date'),
                description=request.POST.get('description', '')
            )
            debt.full_clean()
            debt.save()
            messages.success(request, _('Borc uğurla əlavə edildi!'))
            return redirect('debt_list')
        except Exception as e:
            messages.error(request, _('Xəta: {error}').format(error=str(e)))
    else:
        form = DebtForm(cashier=cashier)
    
    return render(request, 'main/debt_add.html', {
        'form': form
    })


@login_required
def debt_detail(request, pk):
    """View details of a specific debt"""
    # Admin/staff can view any debt
    if request.user.is_staff or request.user.is_superuser:
        debt = get_object_or_404(Debt.all_objects, pk=pk)
        is_admin = True
    else:
        cashier = get_current_cashier(request)
        if not cashier:
            messages.error(request, _('Kassir profili tapılmadı.'))
            auth_logout(request)
            return redirect('login')
        debt = get_object_or_404(Debt.all_objects, pk=pk, cashier=cashier)
        is_admin = False
    
    # Get all payments for this debt
    payments = debt.payments.all().order_by('-payment_date')
    
    # Get all debts for this customer (same cashier if not admin)
    if is_admin:
        customer_debts = Debt.objects.filter(
            customer=debt.customer,
            is_paid=False,
            is_deleted=False
        ).select_related('cashier', 'customer').order_by('-date_given')
    else:
        customer_debts = Debt.objects.filter(
            customer=debt.customer,
            cashier=cashier,
            is_paid=False,
            is_deleted=False
        ).select_related('cashier', 'customer').order_by('-date_given')
    
    # Calculate totals
    total_remaining = sum(d.remaining_amount for d in customer_debts)
    total_amount = sum(d.amount for d in customer_debts)
    total_paid = sum(d.paid_amount for d in customer_debts)
    
    return render(request, 'main/debt_detail.html', {
        'debt': debt, 
        'is_admin': is_admin,
        'payments': payments,
        'customer_debts': customer_debts,
        'total_remaining': total_remaining,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'has_multiple_debts': customer_debts.count() > 1
    })


def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_admin)
def debt_delete(request, pk):
    """Delete a debt - only admins can delete, requires password confirmation"""
    debt = get_object_or_404(Debt, pk=pk)
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        
        if not password:
            messages.error(request, _('Zəhmət olmasa parol daxil edin.'))
            return render(request, 'main/debt_delete.html', {'debt': debt})
        
        # Verify password
        if not check_password(password, request.user.password):
            messages.error(request, _('Yanlış parol. Borc silinmədi.'))
            return render(request, 'main/debt_delete.html', {'debt': debt})
        
        # Password is correct, soft delete the debt
        customer_name = str(debt.customer)
        amount = debt.amount
        debt.soft_delete(request.user)
        messages.success(request, _('Borc uğurla silindi: {customer} - {amount}₼').format(
            customer=customer_name, amount=amount
        ))
        return redirect('debt_list')
    
    return render(request, 'main/debt_delete.html', {'debt': debt})


@login_required
@user_passes_test(is_admin)
def debt_edit(request, pk):
    """Edit a debt - only admins can edit"""
    debt = get_object_or_404(Debt, pk=pk)
    
    if request.method == 'POST':
        form = DebtEditForm(request.POST, instance=debt, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Borc uğurla yeniləndi!'))
            return redirect('debt_detail', pk=pk)
    else:
        form = DebtEditForm(instance=debt, user=request.user)
    
    return render(request, 'main/debt_edit.html', {'form': form, 'debt': debt})


@login_required
def debt_mark_paid(request, pk):
    """Mark a debt as paid with payment method"""
    # Admin/staff can mark any debt as paid
    if request.user.is_staff or request.user.is_superuser:
        debt = get_object_or_404(Debt, pk=pk)
    else:
        cashier = get_current_cashier(request)
        if not cashier:
            messages.error(request, _('Kassir profili tapılmadı.'))
            auth_logout(request)
            return redirect('login')
        debt = get_object_or_404(Debt, pk=pk, cashier=cashier)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if not payment_method:
            messages.error(request, _('Zəhmət olmasa ödəniş üsulunu seçin.'))
            return redirect('debt_detail', pk=pk)
        
        debt.mark_as_paid(payment_method=payment_method)
        payment_method_display = debt.get_payment_method_display_az()
        messages.success(request, _('Borc ödənildi kimi işarələndi! Ödəniş üsulu: {method}').format(method=payment_method_display))
        return redirect('debt_detail', pk=pk)
    
    # If GET request, show payment method selection form
    return render(request, 'main/debt_mark_paid.html', {'debt': debt})


@login_required
def debt_add_payment(request, pk):
    """Add a partial payment to a debt"""
    # Admin/staff can add payment to any debt
    if request.user.is_staff or request.user.is_superuser:
        debt = get_object_or_404(Debt, pk=pk)
    else:
        cashier = get_current_cashier(request)
        if not cashier:
            messages.error(request, _('Kassir profili tapılmadı.'))
            auth_logout(request)
            return redirect('login')
        debt = get_object_or_404(Debt, pk=pk, cashier=cashier)
    
    if debt.is_paid:
        messages.info(request, _('Bu borc artıq tam ödənilib.'))
        return redirect('debt_detail', pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, debt=debt)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.debt = debt
            payment.created_by = request.user
            # payment_date is already set from the form, but ensure it's timezone-aware
            if payment.payment_date and timezone.is_naive(payment.payment_date):
                payment.payment_date = timezone.make_aware(payment.payment_date)
            payment.save()
            messages.success(request, _('Ödəniş uğurla əlavə edildi: {amount}₼').format(amount=payment.amount))
            return redirect('debt_detail', pk=pk)
    else:
        form = PaymentForm(debt=debt)
    
    return render(request, 'main/debt_add_payment.html', {'form': form, 'debt': debt})


@login_required
def debt_pay_all_customer(request, pk):
    """Pay all debts for a customer"""
    # Admin/staff can pay all debts for any customer
    if request.user.is_staff or request.user.is_superuser:
        debt = get_object_or_404(Debt.all_objects, pk=pk)
        is_admin = True
    else:
        cashier = get_current_cashier(request)
        if not cashier:
            messages.error(request, _('Kassir profili tapılmadı.'))
            auth_logout(request)
            return redirect('login')
        debt = get_object_or_404(Debt.all_objects, pk=pk, cashier=cashier)
        is_admin = False
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if not payment_method:
            messages.error(request, _('Zəhmət olmasa ödəniş üsulunu seçin.'))
            return redirect('debt_detail', pk=pk)
        
        # Get all unpaid debts for this customer
        if is_admin:
            customer_debts = Debt.objects.filter(
                customer=debt.customer,
                is_paid=False,
                is_deleted=False
            )
        else:
            customer_debts = Debt.objects.filter(
                customer=debt.customer,
                cashier=cashier,
                is_paid=False,
                is_deleted=False
            )
        
        if not customer_debts.exists():
            messages.info(request, _('Bu müştərinin ödənilməmiş borcu yoxdur.'))
            return redirect('debt_detail', pk=pk)
        
        # Mark all debts as paid
        count = 0
        total_amount = 0
        for d in customer_debts:
            d.mark_as_paid(payment_method=payment_method)
            count += 1
            total_amount += d.remaining_amount
        
        # Get payment method display name
        payment_methods = {
            'cash': _('Nağd'),
            'card': _('Kart'),
            'posterminal': _('Posterminal')
        }
        payment_method_display = payment_methods.get(payment_method, payment_method)
        
        messages.success(request, _('{count} borc uğurla ödənildi! Ümumi məbləğ: {amount}₼. Ödəniş üsulu: {method}').format(
            count=count,
            amount=total_amount,
            method=payment_method_display
        ))
        return redirect('debt_detail', pk=pk)
    
    # If GET request, show payment method selection form
    # Get all unpaid debts for this customer to show total
    if is_admin:
        customer_debts = Debt.objects.filter(
            customer=debt.customer,
            is_paid=False,
            is_deleted=False
        )
    else:
        customer_debts = Debt.objects.filter(
            customer=debt.customer,
            cashier=cashier,
            is_paid=False,
            is_deleted=False
        )
    
    total_remaining = sum(d.remaining_amount for d in customer_debts)
    
    return render(request, 'main/debt_pay_all.html', {
        'debt': debt,
        'customer_debts': customer_debts,
        'total_remaining': total_remaining,
        'count': customer_debts.count()
    })


@login_required
def cashier_list(request):
    """List all cashiers (admin only - can be removed or restricted)"""
    # Only show current cashier's info
    cashier = get_current_cashier(request)
    if not cashier:
        messages.error(request, _('Kassir profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    # For now, just redirect to cashier detail
    return redirect('cashier_detail', pk=cashier.pk)


@login_required
def cashier_detail(request, pk):
    """View cashier details and their debts"""
    current_cashier = get_current_cashier(request)
    if not current_cashier:
        messages.error(request, _('Kassir profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    # Users can only view their own profile
    if current_cashier.pk != pk:
        messages.error(request, _('Yalnız öz profilinizə baxa bilərsiniz.'))
        return redirect('cashier_detail', pk=current_cashier.pk)
    
    cashier = current_cashier
    debts = cashier.debts.all().select_related('customer')
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'unpaid':
        debts = debts.filter(is_paid=False)
    elif status == 'paid':
        debts = debts.filter(is_paid=True)
    elif status == 'overdue':
        today = timezone.now().date()
        debts = debts.filter(is_paid=False, promise_date__lt=today)
    
    context = {
        'cashier': cashier,
        'debts': debts,
        'selected_status': status,
    }
    
    return render(request, 'main/cashier_detail.html', context)


@login_required
def cashier_change_password(request, pk):
    """Allow cashier to change their own password"""
    current_cashier = get_current_cashier(request)
    if not current_cashier:
        messages.error(request, _('Kassir profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    # Users can only change their own password
    if current_cashier.pk != pk:
        messages.error(request, _('Yalnız öz parolunuzu dəyişə bilərsiniz.'))
        return redirect('cashier_detail', pk=current_cashier.pk)
    
    cashier = current_cashier
    
    if not cashier.user:
        messages.error(request, _('Bu kassirin istifadəçi hesabı yoxdur.'))
        return redirect('cashier_detail', pk=pk)
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not current_password:
            messages.error(request, _('Zəhmət olmasa cari parolu daxil edin.'))
        elif not new_password:
            messages.error(request, _('Zəhmət olmasa yeni parolu daxil edin.'))
        elif new_password != confirm_password:
            messages.error(request, _('Yeni parol və təsdiq parolu uyğun deyil.'))
        elif len(new_password) < 8:
            messages.error(request, _('Parol minimum 8 simvol olmalıdır.'))
        elif not cashier.user.check_password(current_password):
            messages.error(request, _('Cari parol səhvdir.'))
        else:
            cashier.user.set_password(new_password)
            cashier.user.save()
            update_session_auth_hash(request, cashier.user)  # Keep user logged in
            messages.success(request, _('Parol uğurla dəyişdirildi!'))
            return redirect('cashier_detail', pk=pk)
    
    return render(request, 'main/cashier_change_password.html', {'cashier': cashier})


@login_required
def cashier_add(request):
    """Add a new cashier (with user account) - redirect to admin"""
    if not request.user.is_staff:
        messages.error(request, _('Yalnız administratorlar yeni kassir əlavə edə bilər.'))
        return redirect('home')
    return redirect('admin_cashier_add')


@login_required
def customer_list(request):
    """List all customers (shared across all cashiers)"""
    # Admin/staff can access customer list without cashier profile
    if not (request.user.is_staff or request.user.is_superuser):
        cashier = get_current_cashier(request)
        if not cashier:
            messages.error(request, _('Kassir profili tapılmadı.'))
            auth_logout(request)
            return redirect('login')
    
    customers = Customer.objects.all()
    
    # Search
    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            Q(name__icontains=search) |
            Q(surname__icontains=search) |
            Q(patronymic__icontains=search) |
            Q(place__icontains=search)
        )
    
    context = {
        'customers': customers,
        'search_query': search,
    }
    
    return render(request, 'main/customer_list.html', context)


@login_required
def customer_add(request):
    """Add a new customer (shared across all cashiers)"""
    # Admin/staff can add customers without cashier profile
    if not (request.user.is_staff or request.user.is_superuser):
        cashier = get_current_cashier(request)
        if not cashier:
            messages.error(request, _('Kassir profili tapılmadı.'))
            auth_logout(request)
            return redirect('login')
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # Check if customer already exists (unique constraint)
            try:
                customer, created = Customer.objects.get_or_create(
                    name=form.cleaned_data['name'],
                    surname=form.cleaned_data['surname'],
                    patronymic=form.cleaned_data.get('patronymic') or None,
                    place=form.cleaned_data['place'],
                    defaults={
                        'phone': form.cleaned_data.get('phone'),
                        'address': form.cleaned_data.get('address')
                    }
                )
                if created:
                    messages.success(request, _('Müştəri uğurla əlavə edildi!'))
                else:
                    messages.info(request, _('Bu müştəri artıq mövcuddur: {customer}').format(customer=customer))
                return redirect('customer_list')
            except Exception as e:
                messages.error(request, _('Xəta: {error}').format(error=str(e)))
    else:
        form = CustomerForm()
    
    return render(request, 'main/customer_add.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def customer_edit(request, pk):
    """Edit an existing customer (admin only)"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            try:
                # Check if the updated customer would conflict with another customer
                # (unique constraint on name, surname, patronymic, place)
                updated_name = form.cleaned_data['name']
                updated_surname = form.cleaned_data['surname']
                updated_patronymic = form.cleaned_data.get('patronymic') or None
                updated_place = form.cleaned_data['place']
                
                # Check if another customer with same combination exists (excluding current)
                existing = Customer.objects.filter(
                    name=updated_name,
                    surname=updated_surname,
                    patronymic=updated_patronymic,
                    place=updated_place
                ).exclude(pk=customer.pk).first()
                
                if existing:
                    messages.error(request, _('Bu kombinasiya ilə başqa müştəri artıq mövcuddur: {customer}').format(customer=existing))
                else:
                    form.save()
                    messages.success(request, _('Müştəri məlumatları uğurla yeniləndi!'))
                    return redirect('customer_list')
            except Exception as e:
                messages.error(request, _('Xəta: {error}').format(error=str(e)))
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'main/customer_edit.html', {'form': form, 'customer': customer})


@login_required
def reminders(request):
    """View all overdue debts (reminders) for current cashier"""
    # If admin/staff, show all overdue debts
    if request.user.is_staff or request.user.is_superuser:
        today = timezone.now().date()
        overdue_debts = Debt.objects.filter(
            is_paid=False,
            promise_date__lte=today
        ).select_related('cashier', 'customer').order_by('promise_date')
        
        context = {
            'cashier': None,
            'overdue_debts': overdue_debts,
            'is_admin': True,
        }
        return render(request, 'main/reminders.html', context)
    
    cashier = get_current_cashier(request)
    if not cashier:
        messages.error(request, _('Kassir profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    today = timezone.now().date()
    overdue_debts = Debt.objects.filter(
        cashier=cashier,
        is_paid=False,
        promise_date__lte=today
    ).select_related('cashier', 'customer').order_by('promise_date')
    
    context = {
        'cashier': cashier,
        'overdue_debts': overdue_debts,
        'is_admin': False,
    }
    
    return render(request, 'main/reminders.html', context)


@login_required
def customer_import(request):
    """Import customers from 1C file (CSV or Excel)"""
    cashier = get_current_cashier(request)
    if not cashier:
        messages.error(request, _('Kassir profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    if request.method == 'POST':
        form = CustomerImportForm(request.POST, request.FILES)
        if form.is_valid():
            
            
            file = request.FILES['file']
            # Get checkbox values - Django BooleanField returns False when unchecked, True when checked
            # Use explicit get() to ensure we get the actual value
            skip_duplicates = form.cleaned_data.get('skip_duplicates', False)
            skip_empty = form.cleaned_data.get('skip_empty', False)
            
            # Debug: Add a message to show what values we're using
            messages.info(request, _('İdxal parametrləri: Təkrarlananları atla = {skip_duplicates}, Boş sətirləri atla = {skip_empty}').format(
                skip_duplicates=skip_duplicates, skip_empty=skip_empty))
            
            # Determine file type
            file_extension = os.path.splitext(file.name)[1].lower()
            
            try:
                # Parse file based on extension
                if file_extension == '.csv':
                    data_rows = parse_csv_file(file)
                elif file_extension in ['.xlsx', '.xls']:
                    # Check if openpyxl is available before trying to parse
                    try:
                        import openpyxl
                    except ImportError:
                        import sys
                        python_path = sys.executable
                        messages.error(
                            request,
                            _('openpyxl cari Python mühitində mövcud deyil.\n'
                              'Cari Python: {python_path}\n'
                              'Zəhmət olmasa quraşdırın: pip install openpyxl\n'
                              'Sonra Django serverini yenidən başladın.').format(python_path=python_path)
                        )
                        return render(request, 'main/customer_import.html', {'form': form})
                    data_rows = parse_excel_file(file)
                else:
                    messages.error(request, _('Dəstəklənməyən fayl formatı. Zəhmət olmasa CSV və ya Excel faylı yükləyin.'))
                    return render(request, 'main/customer_import.html', {'form': form})
                
                # Import customers (skip_duplicates and skip_empty already set above at line 249-250)
                result = import_customers_from_data(data_rows, skip_duplicates=skip_duplicates, skip_empty=skip_empty)
                
                # Show results
                if result['imported'] > 0:
                    if skip_duplicates:
                        messages.success(
                            request,
                            _('{count} yeni müştəri uğurla idxal edildi!').format(count=result["imported"])
                        )
                    else:
                        # Show detailed breakdown when skip_duplicates is False
                        msg_parts = []
                        if result.get('created_new', 0) > 0:
                            msg_parts.append(_('{count} yeni müştəri yaradıldı').format(count=result["created_new"]))
                        if result.get('updated_existing', 0) > 0:
                            msg_parts.append(_('{count} mövcud müştəri yeniləndi').format(count=result["updated_existing"]))
                        if not msg_parts:
                            msg_parts.append(_('{count} müştəri işlənildi').format(count=result["imported"]))
                        
                        messages.success(
                            request,
                            _('{count} müştəri uğurla işlənildi! ({details})').format(
                                count=result["imported"],
                                details=", ".join(msg_parts)
                            )
                        )
                
                # Only show skipped message if skip_duplicates was True
                if result['skipped'] > 0 and skip_duplicates:
                    messages.info(
                        request,
                        _('{count} təkrarlanan müştəri atlandı.').format(count=result["skipped"])
                    )
                
                if result['errors']:
                    error_msg = _('{count} xəta ilə qarşılaşıldı. ').format(count=len(result["errors"]))
                    # Show first 3 errors with details
                    if len(result['errors']) <= 3:
                        error_msg += '<br>'.join(result['errors'])
                    else:
                        error_msg += '<br>'.join(result['errors'][:3]) + _('<br>... və {count} əlavə xəta.').format(count=len(result["errors"]) - 3)
                        # Show a sample of errors from different parts of the file
                        if len(result['errors']) > 10:
                            mid_point = len(result['errors']) // 2
                            error_msg += _('<br><br>Faylın ortasından nümunə:<br>{error}').format(error=result["errors"][mid_point])
                    messages.warning(request, error_msg)
                
                if result['imported'] == 0 and result['skipped'] == 0:
                    messages.warning(request, _('Heç bir müştəri idxal edilmədi. Zəhmət olmasa fayl formatını yoxlayın.'))
                
                return redirect('customer_list')
            
            except ImportError as e:
                messages.error(request, str(e))
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = CustomerImportForm()
    
    return render(request, 'main/customer_import.html', {'form': form})


@login_required
def customer_search_api(request):
    """API endpoint for customer search (AJAX)"""
    from django.http import JsonResponse
    
    query = request.GET.get('q', '').strip()
    
    # If query is empty or very short, return recent customers as preview
    if len(query) < 2:
        # Return recent customers (last 20) as preview
        customers = Customer.objects.all().order_by('-id')[:20]
    else:
        # Search in name, surname, place, phone
        customers = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(surname__icontains=query) |
            Q(place__icontains=query) |
            Q(phone__icontains=query)
        )[:20]
    
    results = []
    for customer in customers:
        results.append({
            'id': customer.pk,
            'name': customer.name,
            'surname': customer.surname,
            'place': customer.place,
            'phone': customer.phone or '',
            'display': str(customer)
        })
    
    return JsonResponse({'customers': results})


# Admin Views
def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard showing all cashiers and their debts"""
    today = timezone.now().date()
    from datetime import datetime, timedelta
    from calendar import monthrange
    
    # Get current month start and end dates
    current_month_start = today.replace(day=1)
    last_day = monthrange(today.year, today.month)[1]
    current_month_end = today.replace(day=last_day)
    
    # Convert to datetime for filtering
    month_start_datetime = timezone.make_aware(datetime.combine(current_month_start, datetime.min.time()))
    month_end_datetime = timezone.make_aware(datetime.combine(current_month_end, datetime.max.time()))
    
    # Monthly statistics - debts given this month
    monthly_given = Debt.objects.filter(
        date_given__gte=month_start_datetime,
        date_given__lte=month_end_datetime
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Monthly statistics - payments/returns this month (partial + full)
    monthly_partial_payments = Payment.objects.filter(
        payment_date__gte=month_start_datetime,
        payment_date__lte=month_end_datetime
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Full payments (debts fully paid this month, excluding those with partial payments)
    monthly_full_payments = Debt.objects.filter(
        is_paid=True,
        paid_date__gte=month_start_datetime,
        paid_date__lte=month_end_datetime
    ).exclude(
        id__in=Payment.objects.filter(
            payment_date__gte=month_start_datetime,
            payment_date__lte=month_end_datetime
        ).values_list('debt_id', flat=True).distinct()
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_returned = monthly_partial_payments + monthly_full_payments
    monthly_balance = monthly_given - monthly_returned
    
    # Get all cashiers
    cashiers = Cashier.objects.all().select_related('user')
    
    # Get statistics for all cashiers
    # Prefetch payments to calculate remaining_amount correctly
    unpaid_debts = Debt.objects.filter(is_paid=False).select_related('customer', 'cashier').prefetch_related('payments')
    unpaid_debts_list = list(unpaid_debts)  # Evaluate queryset once
    total_debts = len(unpaid_debts_list)
    
    # Calculate total remaining amount (not total amount)
    total_amount = sum(debt.remaining_amount for debt in unpaid_debts_list)
    
    overdue_debts_qs = Debt.objects.filter(
        is_paid=False,
        promise_date__lt=today
    ).select_related('customer', 'cashier').prefetch_related('payments')
    overdue_debts_list = list(overdue_debts_qs)  # Evaluate queryset once
    overdue_debts_count = len(overdue_debts_list)
    
    # Calculate overdue remaining amount (not total amount)
    overdue_amount = sum(debt.remaining_amount for debt in overdue_debts_list)
    
    # Get cashier statistics
    cashier_stats = []
    for cashier in cashiers:
        # Prefetch debts and payments for accurate remaining_amount calculation
        unpaid_debts = cashier.debts.filter(is_paid=False).prefetch_related('payments')
        total_remaining = sum(debt.remaining_amount for debt in unpaid_debts)
        
        stats = {
            'cashier': cashier,
            'total_debt': total_remaining,  # Use calculated remaining amount
            'debt_count': unpaid_debts.count(),
            'overdue_count': cashier.overdue_debt_count,
            'has_user': cashier.user is not None,
        }
        cashier_stats.append(stats)
    
    # Recent debts from all cashiers
    recent_debts = Debt.objects.filter(is_paid=False).select_related('cashier', 'customer').order_by('-date_given')[:20]
    
    # Overdue debts from all cashiers
    overdue_debts_list = Debt.objects.filter(
        is_paid=False,
        promise_date__lt=today
    ).select_related('cashier', 'customer').order_by('promise_date')[:20]
    
    context = {
        'total_debts': total_debts,
        'total_amount': total_amount,
        'overdue_debts': overdue_debts_count,
        'overdue_amount': overdue_amount,
        'cashier_stats': cashier_stats,
        'recent_debts': recent_debts,
        'overdue_debts_list': overdue_debts_list,
        'monthly_given': monthly_given,
        'monthly_returned': monthly_returned,
        'monthly_balance': monthly_balance,
    }
    
    return render(request, 'main/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_all_debts(request):
    """Admin view to see all debts from all cashiers"""
    # Only show open (unpaid) debts by default
    debts = Debt.objects.filter(is_paid=False).select_related('cashier', 'customer')
    
    # Filter by cashier
    cashier_id = request.GET.get('cashier')
    if cashier_id:
        debts = debts.filter(cashier_id=cashier_id)
    
    # Filter by status (only if explicitly requested)
    status = request.GET.get('status')
    if status == 'paid':
        # Show paid debts only if explicitly requested
        debts = Debt.objects.filter(is_paid=True).select_related('cashier', 'customer')
        if cashier_id:
            debts = debts.filter(cashier_id=cashier_id)
    elif status == 'overdue':
        today = timezone.now().date()
        debts = debts.filter(is_paid=False, promise_date__lt=today)
    elif status == 'all':
        # Show all debts (paid and unpaid) if explicitly requested
        debts = Debt.objects.all().select_related('cashier', 'customer')
        if cashier_id:
            debts = debts.filter(cashier_id=cashier_id)
    # Default: show only unpaid (open) debts
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        debts = debts.filter(
            Q(customer__name__icontains=search) |
            Q(customer__surname__icontains=search) |
            Q(customer__place__icontains=search) |
            Q(cashier__name__icontains=search) |
            Q(cashier__surname__icontains=search) |
            Q(description__icontains=search)
        )
    
    cashiers = Cashier.objects.all()
    
    context = {
        'debts': debts,
        'cashiers': cashiers,
        'selected_cashier': cashier_id,
        'selected_status': status,
        'search_query': search if search else '',
    }
    
    return render(request, 'main/admin_all_debts.html', context)


@login_required
@user_passes_test(is_admin)
def admin_cashier_list(request):
    """Admin view to manage all cashiers"""
    cashiers = Cashier.objects.all().select_related('user')
    return render(request, 'main/admin_cashier_list.html', {'cashiers': cashiers})


@login_required
@user_passes_test(is_admin)
def admin_cashier_add(request):
    """Admin view to add new cashier with user account"""
    if request.method == 'POST':
        form = CashierForm(request.POST)
        if form.is_valid():
            cashier = form.save()
            messages.success(request, _('Kassir və istifadəçi hesabı uğurla yaradıldı!'))
            messages.info(request, _('İstifadəçi adı: {username}').format(username=cashier.user.username))
            return redirect('admin_cashier_list')
    else:
        form = CashierForm()
    
    return render(request, 'main/admin_cashier_add.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_cashier_change_password(request, pk):
    """Admin view to change cashier password"""
    cashier = get_object_or_404(Cashier, pk=pk)
    
    if not cashier.user:
        messages.error(request, _('Bu kassirin istifadəçi hesabı yoxdur.'))
        return redirect('admin_cashier_list')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not new_password:
            messages.error(request, _('Parol boş ola bilməz.'))
        elif new_password != confirm_password:
            messages.error(request, _('Parollar uyğun gəlmir.'))
        elif len(new_password) < 8:
            messages.error(request, _('Parol ən azı 8 simvol olmalıdır.'))
        else:
            cashier.user.set_password(new_password)
            cashier.user.save()
            messages.success(request, _('Parol uğurla dəyişdirildi!'))
            return redirect('admin_cashier_list')
    
    return render(request, 'main/admin_cashier_change_password.html', {'cashier': cashier})


@login_required
def todays_operations(request):
    """View operations for a specific date (defaults to today)"""
    # Get current date in local timezone
    now = timezone.now()
    if timezone.is_aware(now):
        now = timezone.localtime(now)
    today = now.date()
    
    # Get selected date from GET parameter, default to today
    selected_date_str = request.GET.get('date', '')
    if selected_date_str:
        try:
            # Parse date from YYYY-MM-DD format
            from datetime import datetime as dt
            selected_date = dt.strptime(selected_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            selected_date = today
    else:
        selected_date = today
    
    # If admin/staff, show all operations from all cashiers for selected date
    if request.user.is_staff or request.user.is_superuser:
        # Show debts created on this date OR paid on this date
        # Use date range for SQLite compatibility
        from datetime import datetime, timedelta
        # Ensure we use the correct timezone when combining date and time
        # Use timezone.make_aware with the default timezone (Asia/Baku from settings)
        naive_start = datetime.combine(selected_date, datetime.min.time())
        start_datetime = timezone.make_aware(naive_start)
        end_datetime = start_datetime + timedelta(days=1)
        
        # Separate debts given today from debts returned/paid today
        debts_given_today = Debt.all_objects.filter(
            date_given__gte=start_datetime, 
            date_given__lt=end_datetime
        ).select_related('cashier', 'customer', 'deleted_by').prefetch_related('payments').order_by('-date_given', '-id')
        
        debts_returned_today = Debt.all_objects.filter(
            paid_date__gte=start_datetime, 
            paid_date__lt=end_datetime
        ).select_related('cashier', 'customer', 'deleted_by').prefetch_related('payments').order_by('-paid_date', '-id')
        
        debts_deleted_today = Debt.all_objects.filter(
            deleted_at__gte=start_datetime, 
            deleted_at__lt=end_datetime
        ).select_related('cashier', 'customer', 'deleted_by').prefetch_related('payments').order_by('-deleted_at', '-id')
        
        # Get partial payments made today
        partial_payments_today = Payment.objects.filter(
            payment_date__gte=start_datetime, 
            payment_date__lt=end_datetime
        ).select_related('debt__customer', 'debt__cashier', 'created_by').order_by('-payment_date', '-id')
        
        # Get full payments (debts fully paid today) - exclude those with partial payments
        full_payments_today = debts_returned_today.filter(is_paid=True).exclude(
            id__in=partial_payments_today.values_list('debt_id', flat=True).distinct()
        )
        
        # Combine all payments (partial + full) for display
        all_payments_today = list(partial_payments_today)
        for debt in full_payments_today:
            # Create a payment-like object for full payments
            all_payments_today.append({
                'debt': debt,
                'amount': debt.amount,
                'payment_date': debt.paid_date,
                'payment_method': debt.payment_method,
                'notes': '',
                'created_by': None,
                'is_full_payment': True
            })
        
        # Sort combined payments by date
        all_payments_today.sort(key=lambda x: x.payment_date if hasattr(x, 'payment_date') else x['payment_date'], reverse=True)
        
        # Statistics
        total_amount = debts_given_today.aggregate(total=Sum('amount'))['total'] or 0
        deleted_count = debts_deleted_today.count()
        payments_today_total = partial_payments_today.aggregate(total=Sum('amount'))['total'] or 0
        payments_today_total += sum(debt.amount for debt in full_payments_today)
        
        context = {
            'debts_given_today': debts_given_today,
            'debts_returned_today': debts_returned_today,
            'debts_deleted_today': debts_deleted_today,
            'all_payments_today': all_payments_today,
            'selected_date': selected_date,
            'today': today,
            'total_amount': total_amount,
            'deleted_count': deleted_count,
            'payments_today_total': payments_today_total,
            'is_admin': True,
        }
        return render(request, 'main/todays_operations.html', context)
    
    # For regular cashiers, show only their operations for selected date
    cashier = get_current_cashier(request)
    if not cashier:
        messages.error(request, _('Kassir profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    # Show debts created on this date OR paid on this date
    # Use date range for SQLite compatibility
    from datetime import datetime, timedelta
    # Ensure we use the correct timezone when combining date and time
    # Use timezone.make_aware with the default timezone (Asia/Baku from settings)
    naive_start = datetime.combine(selected_date, datetime.min.time())
    start_datetime = timezone.make_aware(naive_start)
    end_datetime = start_datetime + timedelta(days=1)
    
    # Separate debts given today from debts returned/paid today
    debts_given_today = Debt.all_objects.filter(
        cashier=cashier,
        date_given__gte=start_datetime, 
        date_given__lt=end_datetime
    ).select_related('cashier', 'customer', 'deleted_by').prefetch_related('payments').order_by('-date_given', '-id')
    
    debts_returned_today = Debt.all_objects.filter(
        cashier=cashier,
        paid_date__gte=start_datetime, 
        paid_date__lt=end_datetime
    ).select_related('cashier', 'customer', 'deleted_by').prefetch_related('payments').order_by('-paid_date', '-id')
    
    debts_deleted_today = Debt.all_objects.filter(
        cashier=cashier,
        deleted_at__gte=start_datetime, 
        deleted_at__lt=end_datetime
    ).select_related('cashier', 'customer', 'deleted_by').prefetch_related('payments').order_by('-deleted_at', '-id')
    
    # Get partial payments made today
    partial_payments_today = Payment.objects.filter(
        payment_date__gte=start_datetime, 
        payment_date__lt=end_datetime,
        debt__cashier=cashier
        ).select_related('debt__customer', 'debt__cashier', 'created_by').order_by('-payment_date', '-id')
    
    # Get full payments (debts fully paid today) - exclude those with partial payments
    full_payments_today = debts_returned_today.filter(is_paid=True).exclude(
        id__in=partial_payments_today.values_list('debt_id', flat=True).distinct()
    )
    
    # Combine all payments (partial + full) for display
    all_payments_today = list(partial_payments_today)
    for debt in full_payments_today:
        # Create a payment-like object for full payments
        all_payments_today.append({
            'debt': debt,
            'amount': debt.amount,
            'payment_date': debt.paid_date,
            'payment_method': debt.payment_method,
            'notes': '',
            'created_by': None,
            'is_full_payment': True
        })
    
    # Sort combined payments by date
    all_payments_today.sort(key=lambda x: x.payment_date if hasattr(x, 'payment_date') else x['payment_date'], reverse=True)
    
    # Statistics
    total_amount = debts_given_today.aggregate(total=Sum('amount'))['total'] or 0
    deleted_count = debts_deleted_today.count()
    payments_today_total = partial_payments_today.aggregate(total=Sum('amount'))['total'] or 0
    payments_today_total += sum(debt.amount for debt in full_payments_today)
    
    context = {
        'cashier': cashier,
        'debts_given_today': debts_given_today,
        'debts_returned_today': debts_returned_today,
        'debts_deleted_today': debts_deleted_today,
        'all_payments_today': all_payments_today,
        'selected_date': selected_date,
        'today': today,
        'total_amount': total_amount,
        'deleted_count': deleted_count,
        'payments_today_total': payments_today_total,
        'is_admin': False,
    }
    
    return render(request, 'main/todays_operations.html', context)


@login_required
@user_passes_test(is_admin)
def admin_cashier_detail(request, pk):
    """Admin view to see cashier details and all their debts"""
    cashier = get_object_or_404(Cashier, pk=pk)
    debts = cashier.debts.all().select_related('customer')
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'unpaid':
        debts = debts.filter(is_paid=False)
    elif status == 'paid':
        debts = debts.filter(is_paid=True)
    elif status == 'overdue':
        today = timezone.now().date()
        debts = debts.filter(is_paid=False, promise_date__lt=today)
    
    context = {
        'cashier': cashier,
        'debts': debts,
        'selected_status': status,
    }
    
    return render(request, 'main/admin_cashier_detail.html', context)
