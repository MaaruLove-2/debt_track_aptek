import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from main.models import Customer

total = Customer.objects.count()
print(f"Total customers in database: {total}")

if total > 0:
    print("\nFirst 10 customers:")
    for i, customer in enumerate(Customer.objects.all()[:10], 1):
        print(f"{i}. {customer.surname} {customer.name or ''} {customer.patronymic or ''} - {customer.place}")
    
    if total > 10:
        print(f"\n... and {total - 10} more customers")
else:
    print("No customers found in database!")






