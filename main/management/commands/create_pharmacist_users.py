from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Pharmacist


class Command(BaseCommand):
    help = 'Create user accounts for pharmacists that don\'t have one'

    def add_arguments(self, parser):
        parser.add_argument(
            '--default-password',
            type=str,
            default='pharmacy123',
            help='Default password for new user accounts (default: pharmacy123)',
        )

    def handle(self, *args, **options):
        default_password = options['default_password']
        pharmacists_without_users = Pharmacist.objects.filter(user__isnull=True)
        
        if not pharmacists_without_users.exists():
            self.stdout.write(self.style.SUCCESS('All pharmacists already have user accounts.'))
            return
        
        self.stdout.write(f'Found {pharmacists_without_users.count()} pharmacist(s) without user accounts.')
        
        created_count = 0
        for pharmacist in pharmacists_without_users:
            # Generate username from name and surname
            username = f"{pharmacist.name.lower().replace(' ', '')}_{pharmacist.surname.lower().replace(' ', '')}"
            
            # Make sure username is unique
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create_user(
                username=username,
                password=default_password,
                email=pharmacist.email or '',
                first_name=pharmacist.name,
                last_name=pharmacist.surname
            )
            
            # Link to pharmacist
            pharmacist.user = user
            pharmacist.save()
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'[OK] Created user "{username}" for {pharmacist.name} {pharmacist.surname}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n[SUCCESS] Successfully created {created_count} user account(s).'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f'\n[WARNING] IMPORTANT: Default password is "{default_password}"'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'Please ask each pharmacist to change their password after first login!'
            )
        )

