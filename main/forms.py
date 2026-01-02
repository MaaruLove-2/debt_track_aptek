from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Cashier, Customer, Debt, Payment


class CashierForm(forms.ModelForm):
    username = forms.CharField(
        label=_('İstifadəçi adı'),
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_('Daxil olmaq üçün istifadə ediləcək istifadəçi adı')
    )
    password = forms.CharField(
        label=_('Parol'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_('Minimum 8 simvol')
    )
    password_confirm = forms.CharField(
        label=_('Parolu təsdiqlə'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Cashier
        fields = ['name', 'surname', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError(_('Parollar uyğun deyil.'))
            if len(password) < 8:
                raise forms.ValidationError(_('Parol minimum 8 simvol olmalıdır.'))
        
        return cleaned_data
    
    def save(self, commit=True):
        cashier = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            user = User.objects.create_user(
                username=username,
                password=password
            )
            cashier.user = user
        
        if commit:
            cashier.save()
        return cashier


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'surname', 'patronymic', 'place', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'place': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SimplifiedCustomerForm(forms.Form):
    """Simplified form for quick customer creation"""
    full_name = forms.CharField(
        label='',
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ad, Soyad və Yer bir sətirdə')}),
    )
    phone = forms.CharField(
        label=_('Telefon'),
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+994501234567'})
    )


class DebtForm(forms.ModelForm):
    customer_search = forms.CharField(
        label=_('Müştəri axtar'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Müştəri adı, soyadı və ya yerə görə axtar...'),
            'autocomplete': 'off'
        })
    )
    customer_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
    create_new_customer = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput()
    )
    
    def __init__(self, *args, cashier=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove cashier field - it will be set automatically
        if 'cashier' in self.fields:
            del self.fields['cashier']
        
        # Make customer field not required initially (will be set via customer_id)
        if 'customer' in self.fields:
            self.fields['customer'].required = False
            self.fields['customer'].widget = forms.HiddenInput()
        
        # Hide date_given field - it will be set automatically to current time
        if 'date_given' in self.fields:
            self.fields['date_given'].widget = forms.HiddenInput()
            # Set to current time
            from django.utils import timezone
            now = timezone.now()
            self.initial['date_given'] = now
        
        # Set promise_date default to end of current month
        if 'promise_date' in self.fields and not self.initial.get('promise_date'):
            from datetime import datetime
            from calendar import monthrange
            now = timezone.now()
            # Get last day of current month
            last_day = monthrange(now.year, now.month)[1]
            # Create date for last day of current month
            end_of_month = datetime(now.year, now.month, last_day).date()
            self.initial['promise_date'] = end_of_month
    
    def clean_date_given(self):
        """Convert naive datetime from datetime-local input to timezone-aware datetime"""
        date_given = self.cleaned_data.get('date_given')
        if date_given and timezone.is_naive(date_given):
            # datetime-local sends naive datetime, assume it's in local timezone (Asia/Baku)
            from django.conf import settings
            import pytz
            local_tz = pytz.timezone(settings.TIME_ZONE)
            date_given = local_tz.localize(date_given)
        return date_given
    
    class Meta:
        model = Debt
        fields = ['customer', 'amount', 'date_given', 'promise_date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_given': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'promise_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DebtEditForm(forms.ModelForm):
    """Form for editing debts - only admins can use this"""
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Always allow editing customer - use Select widget
        if 'customer' in self.fields:
            from .models import Customer
            self.fields['customer'].queryset = Customer.objects.all().order_by('surname', 'name')
            self.fields['customer'].widget.attrs.update({'class': 'form-control'})
        
        # Format paid_date for datetime-local input if it exists
        if 'paid_date' in self.fields and self.instance and self.instance.paid_date:
            paid_date = self.instance.paid_date
            if timezone.is_aware(paid_date):
                paid_date = timezone.localtime(paid_date)
            self.initial['paid_date'] = paid_date.strftime('%Y-%m-%dT%H:%M')
        
        # Format date_given for datetime-local input if it exists
        if 'date_given' in self.fields and self.instance and self.instance.date_given:
            date_given = self.instance.date_given
            if timezone.is_aware(date_given):
                date_given = timezone.localtime(date_given)
            self.initial['date_given'] = date_given.strftime('%Y-%m-%dT%H:%M')
        
        # Set widget attributes
        if 'amount' in self.fields:
            self.fields['amount'].widget.attrs.update({'class': 'form-control'})
            # Add warning if there are payments
            if self.instance and self.instance.pk:
                paid_amount = self.instance.paid_amount
                if paid_amount > 0:
                    self.fields['amount'].help_text = _('XƏBƏRDARLIQ: Bu borcda artıq {paid}₼ ödəniş var. Məbləği dəyişdikdə qalan məbləğ yenidən hesablanacaq. Hazırkı məbləğ: {current}₼, Ödənilmiş: {paid}₼, Qalan: {remaining}₼').format(
                        paid=paid_amount,
                        current=self.instance.amount,
                        remaining=self.instance.remaining_amount
                    )
        if 'paid_date' in self.fields:
            self.fields['paid_date'].widget.attrs.update({'class': 'form-control', 'type': 'datetime-local'})
        if 'date_given' in self.fields:
            self.fields['date_given'].widget.attrs.update({'class': 'form-control', 'type': 'datetime-local'})
    
    def clean_amount(self):
        """Validate amount - ensure it's not less than paid amount"""
        amount = self.cleaned_data.get('amount')
        if self.instance and self.instance.pk:
            paid_amount = self.instance.paid_amount
            if amount and paid_amount > 0 and amount < paid_amount:
                raise forms.ValidationError(
                    _('Məbləğ ödənilmiş məbləğdən ({paid}₼) az ola bilməz.').format(paid=paid_amount)
                )
        return amount
    
    def clean_date_given(self):
        """Convert naive datetime from datetime-local input to timezone-aware datetime"""
        date_given = self.cleaned_data.get('date_given')
        if date_given and timezone.is_naive(date_given):
            # datetime-local sends naive datetime, assume it's in local timezone
            date_given = timezone.make_aware(date_given)
        return date_given
    
    def clean_paid_date(self):
        """Convert naive datetime from datetime-local input to timezone-aware datetime"""
        paid_date = self.cleaned_data.get('paid_date')
        if paid_date and timezone.is_naive(paid_date):
            # datetime-local sends naive datetime, assume it's in local timezone (Asia/Baku)
            from django.conf import settings
            import pytz
            local_tz = pytz.timezone(settings.TIME_ZONE)
            paid_date = local_tz.localize(paid_date)
        return paid_date
    
    class Meta:
        model = Debt
        fields = ['customer', 'amount', 'date_given', 'promise_date', 'description', 'paid_date', 'payment_method']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_given': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'promise_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'paid_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.ModelForm):
    """Form for adding partial payments"""
    
    def __init__(self, *args, debt=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.debt = debt
        if debt:
            # Set max amount to remaining amount
            if 'amount' in self.fields:
                self.fields['amount'].widget.attrs.update({
                    'class': 'form-control',
                    'step': '0.01',
                    'max': str(debt.remaining_amount)
                })
                self.fields['amount'].help_text = _('Qalan məbləğ: {amount}₼').format(amount=debt.remaining_amount)
        
        # Set default payment_date to current time if not already set
        if 'payment_date' in self.fields:
            if not self.initial.get('payment_date') and not self.data:
                now = timezone.now()
                # Convert to local timezone for display in datetime-local input
                if timezone.is_aware(now):
                    now = timezone.localtime(now)
                self.initial['payment_date'] = now.strftime('%Y-%m-%dT%H:%M')
        
        # Set default payment_date to current time if not already set
        if 'payment_date' in self.fields:
            if not self.initial.get('payment_date'):
                now = timezone.now()
                # Convert to local timezone for display in datetime-local input
                if timezone.is_aware(now):
                    now = timezone.localtime(now)
                self.initial['payment_date'] = now.strftime('%Y-%m-%dT%H:%M')
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.debt and amount:
            if amount > self.debt.remaining_amount:
                raise forms.ValidationError(
                    _('Ödəniş məbləği qalan məbləğdən ({remaining}₼) çox ola bilməz.').format(
                        remaining=self.debt.remaining_amount
                    )
                )
        return amount
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'payment_method', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_payment_date(self):
        """Convert naive datetime from datetime-local input to timezone-aware datetime"""
        payment_date = self.cleaned_data.get('payment_date')
        if payment_date and timezone.is_naive(payment_date):
            payment_date = timezone.make_aware(payment_date)
        return payment_date


class CustomerImportForm(forms.Form):
    file = forms.FileField(
        label=_('Fayl seçin (CSV və ya Excel)'),
        help_text=_('1C-dən ixrac edilmiş CSV və ya Excel faylını yükləyin. Dəstəklənən formatlar: .csv, .xlsx, .xls'),
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    skip_duplicates = forms.BooleanField(
        required=False,
        initial=False,  # Unchecked by default
        label=_('Təkrarlananları atla'),
        help_text=_('İşarələnərsə, artıq mövcud olan müştəriləri atlayın. İşarələnməzsə, bütün sətirləri idxal edin (təkrarlananlar mövcud qeydləri yeniləyəcək).'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    skip_empty = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Boş sətirləri atla'),
        help_text=_('Konтрагент (Müqavilə tərəfi) boş olan sətirləri xəta göstərmək əvəzinə atla'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
