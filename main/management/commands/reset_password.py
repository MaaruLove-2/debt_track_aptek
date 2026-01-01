from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Pharmacist


class Command(BaseCommand):
    help = 'Reset password for a user or list all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to reset password for',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='New password (if not provided, will be generated)',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all users and their pharmacist associations',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_users()
        elif options['username']:
            self.reset_password(options['username'], options.get('password'))
        else:
            self.stdout.write(self.style.ERROR('Please provide --username or use --list to see all users'))
            self.stdout.write(self.style.WARNING('Usage: python manage.py reset_password --username USERNAME [--password PASSWORD]'))
            self.stdout.write(self.style.WARNING('Or: python manage.py reset_password --list'))

    def list_users(self):
        """List all users"""
        users = User.objects.all().select_related('pharmacist_profile')
        self.stdout.write(self.style.SUCCESS(f'\nFound {users.count()} user(s):\n'))
        self.stdout.write(f"{'Username':<20} {'Email':<30} {'Staff':<8} {'Superuser':<12} {'Pharmacist':<30}")
        self.stdout.write('-' * 100)
        
        for user in users:
            pharmacist_name = '-'
            try:
                pharmacist = user.pharmacist_profile
                pharmacist_name = f"{pharmacist.name} {pharmacist.surname}"
            except Pharmacist.DoesNotExist:
                pass
            
            self.stdout.write(
                f"{user.username:<20} {user.email or '-':<30} "
                f"{'Yes' if user.is_staff else 'No':<8} "
                f"{'Yes' if user.is_superuser else 'No':<12} "
                f"{pharmacist_name:<30}"
            )
        
        self.stdout.write('')

    def reset_password(self, username, password=None):
        """Reset password for a user"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found!'))
            return
        
        if not password:
            # Generate a random password
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        user.set_password(password)
        user.save()
        
        self.stdout.write(self.style.SUCCESS(f'\nPassword reset successfully for user: {username}'))
        self.stdout.write(self.style.WARNING(f'New password: {password}'))
        self.stdout.write(self.style.WARNING('Please save this password securely!\n'))

