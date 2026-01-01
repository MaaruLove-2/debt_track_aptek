from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Pharmacist, Customer, Debt


class PharmacistForm(forms.ModelForm):
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
        model = Pharmacist
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
        username = cleaned_data.get('username')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(_('Parollar uyğun gəlmir.'))
        
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Bu istifadəçi adı artıq mövcuddur.'))
        
        return cleaned_data
    
    def save(self, commit=True):
        pharmacist = super().save(commit=False)
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        
        # Create User account
        user = User.objects.create_user(
            username=username,
            password=password,
            email=self.cleaned_data.get('email', ''),
            first_name=self.cleaned_data.get('name', ''),
            last_name=self.cleaned_data.get('surname', '')
        )
        pharmacist.user = user
        
        if commit:
            pharmacist.save()
        return pharmacist


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
        label=_('Ad, Soyad, Yer'),
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Məs: Əli Məmmədov Bakı və ya Məmmədov Əli Bakı')
        }),
        help_text=_('Ad, Soyad və Yer bir sətirdə (məs: Əli Məmmədov Bakı)')
    )
    phone = forms.CharField(
        label=_('Telefon'),
        max_length=20,
        required=False,
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
    
    def __init__(self, *args, pharmacist=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove pharmacist field - it will be set automatically
        if 'pharmacist' in self.fields:
            del self.fields['pharmacist']
        
        # Make customer field not required initially (will be set via customer_id)
        if 'customer' in self.fields:
            self.fields['customer'].required = False
            self.fields['customer'].widget = forms.HiddenInput()
        
        # Set default datetime for date_given if not provided
        if 'date_given' in self.fields and not self.initial.get('date_given'):
            from django.utils import timezone
            now = timezone.now()
            # Format as datetime-local input expects: YYYY-MM-DDTHH:mm
            self.initial['date_given'] = now.strftime('%Y-%m-%dT%H:%M')
    
    class Meta:
        model = Debt
        fields = ['customer', 'amount', 'date_given', 'promise_date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_given': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
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
            from django.utils import timezone
            paid_date = self.instance.paid_date
            if timezone.is_aware(paid_date):
                paid_date = timezone.localtime(paid_date)
            self.initial['paid_date'] = paid_date.strftime('%Y-%m-%dT%H:%M')
        
        # Set widget attributes
        if 'amount' in self.fields:
            self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        if 'paid_date' in self.fields:
            self.fields['paid_date'].widget.attrs.update({'class': 'form-control', 'type': 'datetime-local'})
    
    class Meta:
        model = Debt
        fields = ['customer', 'amount', 'date_given', 'promise_date', 'description', 'paid_date', 'payment_method']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_given': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'promise_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'paid_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }


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
