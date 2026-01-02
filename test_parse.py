"""
Test script to see what's being parsed from the Excel file
Run this to debug the import issue
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from main.utils import parse_excel_file, parse_counterparty_name

# You'll need to provide the path to your Excel file
file_path = input("Enter the full path to your Excel file: ").strip().strip('"')

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)

print(f"\nReading file: {file_path}\n")

try:
    with open(file_path, 'rb') as f:
        data_rows = parse_excel_file(f)
    
    print(f"Total rows parsed: {len(data_rows)}\n")
    print("First 10 rows:")
    print("=" * 80)
    
    for i, row in enumerate(data_rows[:10], 1):
        print(f"\nRow {i}:")
        print(f"  Контрагент (raw): {row.get('counterparty', 'NOT FOUND')}")
        print(f"  Name: {row.get('name', 'NOT FOUND')}")
        print(f"  Surname: {row.get('surname', 'NOT FOUND')}")
        print(f"  Patronymic: {row.get('patronymic', 'NOT FOUND')}")
        print(f"  Place: {row.get('place', 'NOT FOUND')}")
        print(f"  All keys: {list(row.keys())}")
    
    # Check for duplicates in parsed data
    print("\n" + "=" * 80)
    print("Checking for duplicate combinations in parsed data...")
    from collections import Counter
    combos = Counter()
    for row in data_rows:
        name = row.get('name', '') or ''
        surname = row.get('surname', '') or ''
        patronymic = row.get('patronymic', '') or ''
        place = row.get('place', '') or 'Unknown'
        combo = (name, surname, patronymic, place)
        combos[combo] += 1
    
    unique_count = len(combos)
    print(f"Unique combinations: {unique_count}")
    print(f"Total rows: {len(data_rows)}")
    
    if unique_count < len(data_rows):
        print(f"\nWARNING: {len(data_rows) - unique_count} rows have duplicate combinations!")
        print("\nMost common combinations:")
        for combo, count in combos.most_common(5):
            if count > 1:
                print(f"  {combo} appears {count} times")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()






