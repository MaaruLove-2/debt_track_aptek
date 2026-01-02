from django.core.management.base import BaseCommand
import sys


class Command(BaseCommand):
    help = 'Check Python environment and installed packages'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("Django Python Environment Check")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Python executable: {sys.executable}")
        self.stdout.write(f"Python version: {sys.version}")
        self.stdout.write("")
        
        # Check openpyxl
        try:
            import openpyxl
            self.stdout.write(self.style.SUCCESS("[OK] openpyxl is installed!"))
            self.stdout.write(f"  Version: {openpyxl.__version__}")
            self.stdout.write(f"  Location: {openpyxl.__file__}")
        except ImportError as e:
            self.stdout.write(self.style.ERROR("[ERROR] openpyxl is NOT installed!"))
            self.stdout.write(f"  Error: {e}")
            self.stdout.write("")
            self.stdout.write("To install, run:")
            self.stdout.write(f"  {sys.executable} -m pip install openpyxl")
        
        self.stdout.write("")
        self.stdout.write("=" * 60)






