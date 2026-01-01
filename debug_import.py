import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from main.models import Customer
from collections import Counter

# Check what values customers have
customers = Customer.objects.all()
print(f"Total customers: {customers.count()}\n")

if customers.count() > 0:
    print("Customer details:")
    for c in customers:
        print(f"  Name: '{c.name}'")
        print(f"  Surname: '{c.surname}'")
        print(f"  Patronymic: '{c.patronymic}'")
        print(f"  Place: '{c.place}'")
        print()
    
    # Check for duplicates
    unique_combos = Counter()
    for c in customers:
        combo = (c.name or '', c.surname, c.patronymic or '', c.place)
        unique_combos[combo] += 1
    
    print(f"Unique combinations: {len(unique_combos)}")
    if len(unique_combos) < customers.count():
        print("WARNING: There are duplicate combinations!")
        for combo, count in unique_combos.items():
            if count > 1:
                print(f"  {combo} appears {count} times")




