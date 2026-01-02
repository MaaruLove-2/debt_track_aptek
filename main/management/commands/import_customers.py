from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from main.models import Customer
from main.utils import parse_csv_file, parse_excel_file, import_customers_from_data
import os


class Command(BaseCommand):
    help = 'Import customers from a CSV or Excel file exported from 1C'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV or Excel file to import'
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip customers that already exist (same name, surname, and place)',
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        skip_duplicates = options.get('skip_duplicates', True)

        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')

        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension not in ['.csv', '.xlsx', '.xls']:
            raise CommandError('Unsupported file format. Please use CSV or Excel (.xlsx, .xls)')

        self.stdout.write(f'Reading file: {file_path}')

        try:
            with open(file_path, 'rb') as f:
                if file_extension == '.csv':
                    data_rows = parse_csv_file(f)
                elif file_extension in ['.xlsx', '.xls']:
                    data_rows = parse_excel_file(f)

            self.stdout.write(f'Found {len(data_rows)} rows to process')

            # Import customers
            result = import_customers_from_data(data_rows, skip_duplicates=skip_duplicates)

            # Display results
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ Successfully imported {result["imported"]} customer(s)'
            ))

            if result['skipped'] > 0:
                self.stdout.write(self.style.WARNING(
                    f'⚠ Skipped {result["skipped"]} duplicate customer(s)'
                ))

            if result['errors']:
                self.stdout.write(self.style.ERROR(
                    f'\n✗ Encountered {len(result["errors"])} error(s):'
                ))
                for error in result['errors'][:10]:  # Show first 10 errors
                    self.stdout.write(self.style.ERROR(f'  - {error}'))
                if len(result['errors']) > 10:
                    self.stdout.write(self.style.ERROR(
                        f'  ... and {len(result["errors"]) - 10} more errors'
                    ))

        except ImportError as e:
            raise CommandError(str(e))
        except ValueError as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(f'An error occurred: {str(e)}')






