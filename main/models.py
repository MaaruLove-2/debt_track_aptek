from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Pharmacist(models.Model):
    """Model representing a pharmacist"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacist_profile', verbose_name=_('İstifadəçi'), null=True, blank=True)
    name = models.CharField(_('Ad'), max_length=100)
    surname = models.CharField(_('Soyad'), max_length=100)
    phone = models.CharField(_('Telefon'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('E-poçt'), blank=True, null=True)
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)

    class Meta:
        ordering = ['name', 'surname']
        verbose_name = _('Aptekçi')
        verbose_name_plural = _('Aptekçilər')

    def __str__(self):
        return f"{self.name} {self.surname}"

    @property
    def total_debt(self):
        """Calculate total remaining debt for this pharmacist"""
        unpaid_debts = self.debts.filter(is_paid=False).prefetch_related('payments')
        return sum(debt.remaining_amount for debt in unpaid_debts)

    @property
    def overdue_debt_count(self):
        """Count overdue debts for this pharmacist"""
        today = timezone.now().date()
        return self.debts.filter(is_paid=False, promise_date__lt=today).count()
    
    @property
    def unpaid_debt_count(self):
        """Count unpaid debts for this pharmacist"""
        return self.debts.filter(is_paid=False).count()


class Customer(models.Model):
    """Model representing a customer"""
    name = models.CharField(_('Ad'), max_length=100, blank=True, default='')
    surname = models.CharField(_('Soyad'), max_length=100)
    patronymic = models.CharField(_('Ata adı'), max_length=100, blank=True, null=True, help_text=_("Ata adı (отчество)"))
    place = models.CharField(_('Yer'), max_length=200, help_text=_("Müştərinin haradan olduğu"), default='Unknown')
    phone = models.CharField(_('Telefon'), max_length=20, blank=True, null=True)
    address = models.TextField(_('Ünvan'), blank=True, null=True)
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)

    class Meta:
        ordering = ['surname', 'name']
        unique_together = [['name', 'surname', 'patronymic', 'place']]
        verbose_name = _('Müştəri')
        verbose_name_plural = _('Müştərilər')

    def __str__(self):
        full_name = f"{self.surname} {self.name}"
        if self.patronymic:
            full_name += f" {self.patronymic}"
        return f"{full_name} ({self.place})"


class DebtManager(models.Manager):
    """Custom manager that excludes deleted debts by default"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Debt(models.Model):
    """Model representing a debt record"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Nağd')),
        ('card', _('Kart')),
        ('posterminal', _('Posterminal')),
    ]
    
    pharmacist = models.ForeignKey(Pharmacist, on_delete=models.CASCADE, related_name='debts', verbose_name=_('Aptekçi'))
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='debts', verbose_name=_('Müştəri'))
    amount = models.DecimalField(_('Məbləğ'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    date_given = models.DateTimeField(_('Verilmə tarixi'), default=timezone.now, help_text=_("Borcun verildiyi tarix və vaxt"))
    promise_date = models.DateField(_('Vəd tarixi'), help_text=_("Müştərinin pulu qaytarmaq üçün vəd etdiyi tarix"))
    description = models.TextField(_('Təsvir'), blank=True, null=True, help_text=_("Borcla bağlı əlavə qeydlər"))
    is_paid = models.BooleanField(_('Ödənilib'), default=False)
    paid_date = models.DateTimeField(_('Ödəniş tarixi'), blank=True, null=True, help_text=_("Ödəniş tarixi və vaxtı"))
    payment_method = models.CharField(_('Ödəniş üsulu'), max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True, help_text=_("Ödəniş üsulu"))
    is_deleted = models.BooleanField(_('Silinib'), default=False, help_text=_("Borcun silinib-silinməməsi"))
    deleted_at = models.DateTimeField(_('Silinmə tarixi'), blank=True, null=True, help_text=_("Borcun silindiyi tarix və vaxt"))
    deleted_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_debts', verbose_name=_('Silən'))
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yenilənmə tarixi'), auto_now=True)

    # Custom manager to exclude deleted debts by default
    objects = DebtManager()
    all_objects = models.Manager()  # Manager that includes deleted items
    
    class Meta:
        ordering = ['-date_given', '-created_at']
        verbose_name = _('Borc')
        verbose_name_plural = _('Borclar')

    def __str__(self):
        status = _("Ödənilib") if self.is_paid else _("Ödənilməyib")
        return f"{self.customer} - {self.amount} ({status})"

    @property
    def is_overdue(self):
        """Check if the debt is overdue"""
        if self.is_paid:
            return False
        today = timezone.now().date()
        return self.promise_date < today

    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_paid or not self.is_overdue:
            return 0
        today = timezone.now().date()
        return (today - self.promise_date).days

    def mark_as_paid(self, payment_method=None):
        """Mark debt as paid"""
        self.is_paid = True
        self.paid_date = timezone.now()
        if payment_method:
            self.payment_method = payment_method
        self.save()
    
    def get_payment_method_display_az(self):
        """Get payment method display name in Azerbaijani"""
        if not self.payment_method:
            return '-'
        method_map = {
            'cash': 'Nağd',
            'card': 'Kart',
            'posterminal': 'Posterminal',
        }
        return method_map.get(self.payment_method, self.payment_method)
    
    @property
    def paid_amount(self):
        """Calculate total paid amount from partial payments"""
        return self.payments.aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.amount - self.paid_amount
    
    def soft_delete(self, user):
        """Soft delete the debt"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()


class Payment(models.Model):
    """Model for tracking partial payments on debts"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Nağd')),
        ('card', _('Kart')),
        ('posterminal', _('Posterminal')),
    ]
    
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments', verbose_name=_('Borc'))
    amount = models.DecimalField(_('Məbləğ'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_date = models.DateTimeField(_('Ödəniş tarixi'), default=timezone.now, help_text=_("Ödəniş tarixi və vaxtı"))
    payment_method = models.CharField(_('Ödəniş üsulu'), max_length=20, choices=PAYMENT_METHOD_CHOICES, help_text=_("Ödəniş üsulu"))
    notes = models.TextField(_('Qeydlər'), blank=True, null=True, help_text=_("Ödənişlə bağlı əlavə qeydlər"))
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_payments', verbose_name=_('Yaradan'))
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = _('Ödəniş')
        verbose_name_plural = _('Ödənişlər')
    
    def __str__(self):
        return f"{self.debt.customer} - {self.amount}₼ ({self.payment_date.strftime('%d.%m.%Y %H:%M')})"
    
    def get_payment_method_display_az(self):
        """Get payment method display name in Azerbaijani"""
        method_map = {
            'cash': 'Nağd',
            'card': 'Kart',
            'posterminal': 'Posterminal',
        }
        return method_map.get(self.payment_method, self.payment_method)


class Payment(models.Model):
    """Model for tracking partial payments on debts"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Nağd')),
        ('card', _('Kart')),
        ('posterminal', _('Posterminal')),
    ]
    
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments', verbose_name=_('Borc'))
    amount = models.DecimalField(_('Məbləğ'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_date = models.DateTimeField(_('Ödəniş tarixi'), default=timezone.now, help_text=_("Ödəniş tarixi və vaxtı"))
    payment_method = models.CharField(_('Ödəniş üsulu'), max_length=20, choices=PAYMENT_METHOD_CHOICES, help_text=_("Ödəniş üsulu"))
    notes = models.TextField(_('Qeydlər'), blank=True, null=True, help_text=_("Ödənişlə bağlı əlavə qeydlər"))
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_payments', verbose_name=_('Yaradan'))
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = _('Ödəniş')
        verbose_name_plural = _('Ödənişlər')
    
    def __str__(self):
        return f"{self.debt.customer} - {self.amount}₼ ({self.payment_date.strftime('%d.%m.%Y %H:%M')})"
    
    def get_payment_method_display_az(self):
        """Get payment method display name in Azerbaijani"""
        method_map = {
            'cash': 'Nağd',
            'card': 'Kart',
            'posterminal': 'Posterminal',
        }
        return method_map.get(self.payment_method, self.payment_method)
    
    def save(self, *args, **kwargs):
        """Override save to check if debt is fully paid"""
        super().save(*args, **kwargs)
        # Check if debt is fully paid after this payment
        if self.debt.remaining_amount <= 0:
            self.debt.is_paid = True
            self.debt.paid_date = self.payment_date
            self.debt.payment_method = self.payment_method
            self.debt.save()


class DebtEditRequest(models.Model):
    """Model for storing debt edit approval requests"""
    STATUS_CHOICES = [
        ('pending', _('Gözləyir')),
        ('approved', _('Təsdiqlənib')),
        ('rejected', _('Rədd edilib')),
    ]
    
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='edit_requests', verbose_name=_('Borc'))
    requested_by = models.ForeignKey(Pharmacist, on_delete=models.CASCADE, related_name='edit_requests', verbose_name=_('Tələb edən'))
    requested_amount = models.DecimalField(_('Tələb olunan məbləğ'), max_digits=10, decimal_places=2, null=True, blank=True)
    requested_paid_date = models.DateTimeField(_('Tələb olunan ödəniş tarixi'), null=True, blank=True)
    reason = models.TextField(_('Səbəb'), help_text=_("Dəyişiklik səbəbi"))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_edit_requests', verbose_name=_('Baxılan'))
    review_notes = models.TextField(_('Baxış qeydləri'), blank=True, null=True)
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    reviewed_at = models.DateTimeField(_('Baxılma tarixi'), null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Borc redaktə tələbi')
        verbose_name_plural = _('Borc redaktə tələbləri')
    
    def __str__(self):
        return f"{self.debt} - {self.get_status_display()} ({self.requested_by})"
