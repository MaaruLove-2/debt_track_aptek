from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import Debt, Pharmacist


class Command(BaseCommand):
    help = 'Check for overdue debts and display reminders for each pharmacist'

    def handle(self, *args, **options):
        today = timezone.now().date()
        overdue_debts = Debt.objects.filter(
            is_paid=False,
            promise_date__lt=today
        ).select_related('pharmacist', 'customer').order_by('pharmacist', 'promise_date')
        
        if not overdue_debts.exists():
            self.stdout.write(
                self.style.SUCCESS('✓ No overdue debts found!')
            )
            return
        
        # Group by pharmacist
        pharmacist_groups = {}
        for debt in overdue_debts:
            pharmacist = debt.pharmacist
            if pharmacist not in pharmacist_groups:
                pharmacist_groups[pharmacist] = []
            pharmacist_groups[pharmacist].append(debt)
        
        # Display reminders
        self.stdout.write(
            self.style.WARNING(f'\n⚠ OVERDUE DEBT REMINDERS ({len(overdue_debts)} total)\n')
        )
        self.stdout.write('=' * 80)
        
        for pharmacist, debts in pharmacist_groups.items():
            total_amount = sum(debt.amount for debt in debts)
            self.stdout.write(
                self.style.ERROR(f'\n📋 Pharmacist: {pharmacist}')
            )
            self.stdout.write(f'   Total Overdue Debts: {len(debts)}')
            self.stdout.write(f'   Total Amount: ${total_amount:.2f}')
            self.stdout.write('-' * 80)
            
            for debt in debts:
                days_overdue = debt.days_overdue
                self.stdout.write(
                    f'   • {debt.customer.name} {debt.customer.surname} ({debt.customer.place})'
                )
                self.stdout.write(
                    f'     Amount: ${debt.amount:.2f} | '
                    f'Promise Date: {debt.promise_date} | '
                    f'Days Overdue: {days_overdue}'
                )
                if debt.description:
                    self.stdout.write(f'     Notes: {debt.description[:50]}...')
                self.stdout.write('')
        
        self.stdout.write('=' * 80)
        self.stdout.write(
            self.style.WARNING(f'\n⚠ Please follow up with customers to collect overdue payments.\n')
        )

