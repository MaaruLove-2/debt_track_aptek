import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Sum, Q
from .models import Pharmacist, Customer, Debt
from .forms import PharmacistForm, CustomerForm, DebtForm, DebtEditForm, CustomerImportForm, SimplifiedCustomerForm
from .utils import parse_csv_file, parse_excel_file, import_customers_from_data


def login_view(request):
    """Login page for pharmacists and admins"""
    if request.user.is_authenticated:
        # Redirect based on user type
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('home')
    
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
            # Check if regular user has pharmacist profile
            try:
                pharmacist = user.pharmacist_profile
                return redirect('home')
            except Pharmacist.DoesNotExist:
                messages.error(request, _('Bu istifadəçi aptekçi profili yoxdur. Zəhmət olmasa administratorla əlaqə saxlayın.'))
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
def get_current_pharmacist(request):
    """Helper function to get current pharmacist from logged-in user"""
    try:
        return request.user.pharmacist_profile
    except Pharmacist.DoesNotExist:
        return None


@login_required
def home(request):
    """Home page with overview of debts"""
    # If user is admin/staff, redirect to admin dashboard
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard')
    
    pharmacist = get_current_pharmacist(request)
    if not pharmacist:
        messages.error(request, _('Aptekçi profili tapılmadı. Zəhmət olmasa administratorla əlaqə saxlayın.'))
        auth_logout(request)
        return redirect('login')
    
    today = timezone.now().date()
    
    # Get statistics for current pharmacist only
    total_debts = Debt.objects.filter(pharmacist=pharmacist, is_paid=False).count()
    total_amount = Debt.objects.filter(pharmacist=pharmacist, is_paid=False).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    overdue_debts = Debt.objects.filter(
        pharmacist=pharmacist,
        is_paid=False,
        promise_date__lt=today
    ).count()
    
    overdue_amount = Debt.objects.filter(
        pharmacist=pharmacist,
        is_paid=False,
        promise_date__lt=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent debts for current pharmacist
    recent_debts = Debt.objects.filter(pharmacist=pharmacist, is_paid=False).order_by('-date_given')[:10]
    
    # Overdue debts for current pharmacist
    overdue_debts_list = Debt.objects.filter(
        pharmacist=pharmacist,
        is_paid=False,
        promise_date__lt=today
    ).order_by('promise_date')[:10]
    
    context = {
        'pharmacist': pharmacist,
        'total_debts': total_debts,
        'total_amount': total_amount,
        'overdue_debts': overdue_debts,
        'overdue_amount': overdue_amount,
        'recent_debts': recent_debts,
        'overdue_debts_list': overdue_debts_list,
    }
    
    return render(request, 'main/home.html', context)


@login_required
def debt_list(request):
    """List all debts with filtering options"""
    # If admin/staff, redirect to admin all debts
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_all_debts')
    
    pharmacist = get_current_pharmacist(request)
    if not pharmacist:
        messages.error(request, _('Aptekçi profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    # Only show debts for current pharmacist
    debts = Debt.objects.filter(pharmacist=pharmacist).select_related('pharmacist', 'customer')
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'unpaid':
        debts = debts.filter(is_paid=False)
    elif status == 'paid':
        debts = debts.filter(is_paid=True)
    elif status == 'overdue':
        today = timezone.now().date()
        debts = debts.filter(is_paid=False, promise_date__lt=today)
    
    # Search
    search = request.GET.get('search')
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
        'search_query': search,
    }
    
    return render(request, 'main/debt_list.html', context)


@login_required
def debt_add(request):
    """Add a new debt with simplified customer creation"""
    # Admin/staff users need to select a pharmacist, so redirect to admin dashboard
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, _('Admin istifadəçiləri borc əlavə etmək üçün aptekçi seçməlidir. Admin paneldən istifadə edin.'))
        return redirect('admin_dashboard')
    
    pharmacist = get_current_pharmacist(request)
    if not pharmacist:
        messages.error(request, _('Aptekçi profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    if request.method == 'POST':
        form = DebtForm(request.POST, pharmacist=pharmacist)
        
        # Check if creating new customer
        create_new = request.POST.get('create_new_customer') == 'true'
        customer_id = request.POST.get('customer_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        
        # If customer_id is provided, use existing customer (ignore create_new flag)
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
                debt = form.save(commit=False)
                debt.pharmacist = pharmacist
                debt.customer = customer
                if form.is_valid():
                    debt.save()
                    messages.success(request, _('Borc uğurla əlavə edildi!'))
                    return redirect('debt_list')
                else:
                    messages.error(request, _('Forma xəta var. Zəhmət olmasa yoxlayın.'))
            except Customer.DoesNotExist:
                messages.error(request, _('Müştəri tapılmadı.'))
            except Exception as e:
                messages.error(request, _('Xəta: {error}').format(error=str(e)))
        
        elif create_new and full_name:
            # Parse full_name: "Name Surname Place" or "Surname Name Place"
            parts = full_name.split()
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
            
            phone = request.POST.get('phone', '').strip()
            
            # Create or get customer
            customer, created = Customer.objects.get_or_create(
                name=name,
                surname=surname,
                place=place,
                defaults={'phone': phone if phone else None, 'patronymic': None}
            )
            
            if created:
                messages.success(request, _('Yeni müştəri yaradıldı: {customer}').format(customer=customer))
            
            # Create debt with this customer
            try:
                from datetime import datetime as dt
                date_given_str = request.POST.get('date_given')
                # Parse datetime from form (format: YYYY-MM-DDTHH:mm)
                if date_given_str:
                    date_given = dt.strptime(date_given_str, '%Y-%m-%dT%H:%M')
                else:
                    date_given = timezone.now()
                
                debt = Debt(
                    pharmacist=pharmacist,
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
            # No customer selected or created
            messages.error(request, _('Zəhmət olmasa müştəri seçin və ya yenisini yaradın.'))
    else:
        form = DebtForm(pharmacist=pharmacist)
        simplified_form = SimplifiedCustomerForm()
    
    return render(request, 'main/debt_add.html', {
        'form': form,
        'simplified_form': simplified_form
    })


@login_required
def debt_detail(request, pk):
    """View details of a specific debt"""
    # Admin/staff can view any debt
    if request.user.is_staff or request.user.is_superuser:
        debt = get_object_or_404(Debt, pk=pk)
        return render(request, 'main/debt_detail.html', {'debt': debt, 'is_admin': True})
    
    pharmacist = get_current_pharmacist(request)
    if not pharmacist:
        messages.error(request, _('Aptekçi profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    debt = get_object_or_404(Debt, pk=pk, pharmacist=pharmacist)
    return render(request, 'main/debt_detail.html', {'debt': debt, 'is_admin': False})


def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


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
        pharmacist = get_current_pharmacist(request)
        if not pharmacist:
            messages.error(request, _('Aptekçi profili tapılmadı.'))
            auth_logout(request)
            return redirect('login')
        debt = get_object_or_404(Debt, pk=pk, pharmacist=pharmacist)
    
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
def pharmacist_list(request):
    """List all pharmacists (admin only - can be removed or restricted)"""
    # Only show current pharmacist's info
    pharmacist = get_current_pharmacist(request)
    if not pharmacist:
        messages.error(request, _('Aptekçi profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    # For now, just redirect to pharmacist detail
    return redirect('pharmacist_detail', pk=pharmacist.pk)


@login_required
def pharmacist_detail(request, pk):
    """View pharmacist details and their debts"""
    current_pharmacist = get_current_pharmacist(request)
    if not current_pharmacist:
        messages.error(request, _('Aptekçi profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    # Users can only view their own profile
    if current_pharmacist.pk != pk:
        messages.error(request, _('Yalnız öz profilinizə baxa bilərsiniz.'))
        return redirect('pharmacist_detail', pk=current_pharmacist.pk)
    
    pharmacist = current_pharmacist
    debts = pharmacist.debts.all().select_related('customer')
    
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
        'pharmacist': pharmacist,
        'debts': debts,
        'selected_status': status,
    }
    
    return render(request, 'main/pharmacist_detail.html', context)


@login_required
def pharmacist_add(request):
    """Add a new pharmacist (with user account) - redirect to admin"""
    if not request.user.is_staff:
        messages.error(request, _('Yalnız administratorlar yeni aptekçi əlavə edə bilər.'))
        return redirect('home')
    return redirect('admin_pharmacist_add')


@login_required
def customer_list(request):
    """List all customers (shared across all pharmacists)"""
    # Admin/staff can access customer list without pharmacist profile
    if not (request.user.is_staff or request.user.is_superuser):
        pharmacist = get_current_pharmacist(request)
        if not pharmacist:
            messages.error(request, _('Aptekçi profili tapılmadı.'))
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
    """Add a new customer (shared across all pharmacists)"""
    # Admin/staff can add customers without pharmacist profile
    if not (request.user.is_staff or request.user.is_superuser):
        pharmacist = get_current_pharmacist(request)
        if not pharmacist:
            messages.error(request, _('Aptekçi profili tapılmadı.'))
            auth_logout(request)
            return redirect('login')
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Müştəri uğurla əlavə edildi!'))
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'main/customer_add.html', {'form': form})


@login_required
def reminders(request):
    """View all overdue debts (reminders) for current pharmacist"""
    # If admin/staff, show all overdue debts
    if request.user.is_staff or request.user.is_superuser:
        today = timezone.now().date()
        overdue_debts = Debt.objects.filter(
            is_paid=False,
            promise_date__lte=today
        ).select_related('pharmacist', 'customer').order_by('promise_date')
        
        context = {
            'pharmacist': None,
            'overdue_debts': overdue_debts,
            'is_admin': True,
        }
        return render(request, 'main/reminders.html', context)
    
    pharmacist = get_current_pharmacist(request)
    if not pharmacist:
        messages.error(request, _('Aptekçi profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    today = timezone.now().date()
    overdue_debts = Debt.objects.filter(
        pharmacist=pharmacist,
        is_paid=False,
        promise_date__lte=today
    ).select_related('pharmacist', 'customer').order_by('promise_date')
    
    context = {
        'pharmacist': pharmacist,
        'overdue_debts': overdue_debts,
        'is_admin': False,
    }
    
    return render(request, 'main/reminders.html', context)


@login_required
def customer_import(request):
    """Import customers from 1C file (CSV or Excel)"""
    pharmacist = get_current_pharmacist(request)
    if not pharmacist:
        messages.error(request, _('Aptekçi profili tapılmadı.'))
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
    if len(query) < 2:
        return JsonResponse({'customers': []})
    
    # Search in name, surname, place
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
    """Admin dashboard showing all pharmacists and their debts"""
    today = timezone.now().date()
    
    # Get all pharmacists
    pharmacists = Pharmacist.objects.all().select_related('user')
    
    # Get statistics for all pharmacists
    total_debts = Debt.objects.filter(is_paid=False).count()
    total_amount = Debt.objects.filter(is_paid=False).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    overdue_debts = Debt.objects.filter(
        is_paid=False,
        promise_date__lt=today
    ).count()
    
    overdue_amount = Debt.objects.filter(
        is_paid=False,
        promise_date__lt=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get pharmacist statistics
    pharmacist_stats = []
    for pharmacist in pharmacists:
        stats = {
            'pharmacist': pharmacist,
            'total_debt': pharmacist.total_debt,
            'debt_count': pharmacist.debts.filter(is_paid=False).count(),
            'overdue_count': pharmacist.overdue_debt_count,
            'has_user': pharmacist.user is not None,
        }
        pharmacist_stats.append(stats)
    
    # Recent debts from all pharmacists
    recent_debts = Debt.objects.filter(is_paid=False).select_related('pharmacist', 'customer').order_by('-date_given')[:20]
    
    # Overdue debts from all pharmacists
    overdue_debts_list = Debt.objects.filter(
        is_paid=False,
        promise_date__lt=today
    ).select_related('pharmacist', 'customer').order_by('promise_date')[:20]
    
    context = {
        'total_debts': total_debts,
        'total_amount': total_amount,
        'overdue_debts': overdue_debts,
        'overdue_amount': overdue_amount,
        'pharmacist_stats': pharmacist_stats,
        'recent_debts': recent_debts,
        'overdue_debts_list': overdue_debts_list,
    }
    
    return render(request, 'main/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_all_debts(request):
    """Admin view to see all debts from all pharmacists"""
    debts = Debt.objects.all().select_related('pharmacist', 'customer')
    
    # Filter by pharmacist
    pharmacist_id = request.GET.get('pharmacist')
    if pharmacist_id:
        debts = debts.filter(pharmacist_id=pharmacist_id)
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'unpaid':
        debts = debts.filter(is_paid=False)
    elif status == 'paid':
        debts = debts.filter(is_paid=True)
    elif status == 'overdue':
        today = timezone.now().date()
        debts = debts.filter(is_paid=False, promise_date__lt=today)
    
    # Search
    search = request.GET.get('search')
    if search:
        debts = debts.filter(
            Q(customer__name__icontains=search) |
            Q(customer__surname__icontains=search) |
            Q(customer__place__icontains=search) |
            Q(pharmacist__name__icontains=search) |
            Q(pharmacist__surname__icontains=search) |
            Q(description__icontains=search)
        )
    
    pharmacists = Pharmacist.objects.all()
    
    context = {
        'debts': debts,
        'pharmacists': pharmacists,
        'selected_pharmacist': pharmacist_id,
        'selected_status': status,
        'search_query': search,
    }
    
    return render(request, 'main/admin_all_debts.html', context)


@login_required
@user_passes_test(is_admin)
def admin_pharmacist_list(request):
    """Admin view to manage all pharmacists"""
    pharmacists = Pharmacist.objects.all().select_related('user')
    return render(request, 'main/admin_pharmacist_list.html', {'pharmacists': pharmacists})


@login_required
@user_passes_test(is_admin)
def admin_pharmacist_add(request):
    """Admin view to add new pharmacist with user account"""
    if request.method == 'POST':
        form = PharmacistForm(request.POST)
        if form.is_valid():
            pharmacist = form.save()
            messages.success(request, _('Aptekçi və istifadəçi hesabı uğurla yaradıldı!'))
            messages.info(request, _('İstifadəçi adı: {username}').format(username=pharmacist.user.username))
            return redirect('admin_pharmacist_list')
    else:
        form = PharmacistForm()
    
    return render(request, 'main/admin_pharmacist_add.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_pharmacist_change_password(request, pk):
    """Admin view to change pharmacist password"""
    pharmacist = get_object_or_404(Pharmacist, pk=pk)
    
    if not pharmacist.user:
        messages.error(request, _('Bu aptekçinin istifadəçi hesabı yoxdur.'))
        return redirect('admin_pharmacist_list')
    
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
            pharmacist.user.set_password(new_password)
            pharmacist.user.save()
            messages.success(request, _('Parol uğurla dəyişdirildi!'))
            return redirect('admin_pharmacist_list')
    
    return render(request, 'main/admin_pharmacist_change_password.html', {'pharmacist': pharmacist})


@login_required
def todays_operations(request):
    """View operations for a specific date (defaults to today)"""
    today = timezone.now().date()
    
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
    
    # If admin/staff, show all operations from all pharmacists for selected date
    if request.user.is_staff or request.user.is_superuser:
        # Show debts created on this date OR paid on this date
        # Use date range for SQLite compatibility
        from datetime import datetime, timedelta
        start_datetime = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
        end_datetime = start_datetime + timedelta(days=1)
        
        operations = Debt.objects.filter(
            Q(date_given__gte=start_datetime, date_given__lt=end_datetime) | 
            Q(paid_date__gte=start_datetime, paid_date__lt=end_datetime)
        ).select_related('pharmacist', 'customer').order_by('-date_given', '-id')
        
        # Statistics
        total_count = operations.count()
        total_amount = operations.aggregate(total=Sum('amount'))['total'] or 0
        paid_count = operations.filter(is_paid=True).count()
        unpaid_count = operations.filter(is_paid=False).count()
        paid_today_count = operations.filter(is_paid=True, paid_date__gte=start_datetime, paid_date__lt=end_datetime).count()
        
        context = {
            'operations': operations,
            'selected_date': selected_date,
            'today': today,
            'total_count': total_count,
            'total_amount': total_amount,
            'paid_count': paid_count,
            'unpaid_count': unpaid_count,
            'paid_today_count': paid_today_count,
            'is_admin': True,
        }
        return render(request, 'main/todays_operations.html', context)
    
    # For regular pharmacists, show only their operations for selected date
    pharmacist = get_current_pharmacist(request)
    if not pharmacist:
        messages.error(request, _('Aptekçi profili tapılmadı.'))
        auth_logout(request)
        return redirect('login')
    
    # Show debts created on this date OR paid on this date
    # Use date range for SQLite compatibility
    from datetime import datetime, timedelta
    start_datetime = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
    end_datetime = start_datetime + timedelta(days=1)
    
    operations = Debt.objects.filter(
        pharmacist=pharmacist
    ).filter(
        Q(date_given__gte=start_datetime, date_given__lt=end_datetime) | 
        Q(paid_date__gte=start_datetime, paid_date__lt=end_datetime)
    ).select_related('pharmacist', 'customer').order_by('-date_given', '-id')
    
    # Statistics
    total_count = operations.count()
    total_amount = operations.aggregate(total=Sum('amount'))['total'] or 0
    paid_count = operations.filter(is_paid=True).count()
    unpaid_count = operations.filter(is_paid=False).count()
    paid_today_count = operations.filter(is_paid=True, paid_date__gte=start_datetime, paid_date__lt=end_datetime).count()
    
    context = {
        'pharmacist': pharmacist,
        'operations': operations,
        'selected_date': selected_date,
        'today': today,
        'total_count': total_count,
        'total_amount': total_amount,
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
        'paid_today_count': paid_today_count,
        'is_admin': False,
    }
    
    return render(request, 'main/todays_operations.html', context)


@login_required
@user_passes_test(is_admin)
def admin_pharmacist_detail(request, pk):
    """Admin view to see pharmacist details and all their debts"""
    pharmacist = get_object_or_404(Pharmacist, pk=pk)
    debts = pharmacist.debts.all().select_related('customer')
    
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
        'pharmacist': pharmacist,
        'debts': debts,
        'selected_status': status,
    }
    
    return render(request, 'main/admin_pharmacist_detail.html', context)
