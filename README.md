# Debt Tracker

A comprehensive Django web application to track customer debts for your business. The system supports multiple pharmacists, tracks debt dates, promise dates, and automatically reminds you of overdue debts.

## Features

- **Multi-Pharmacist Support**: Track debts for up to 5 pharmacists (or more)
- **Customer Management**: Store customer information including name, surname, and place
- **Debt Tracking**: Record debt amount, date given, and promise date
- **Automatic Reminders**: System automatically identifies overdue debts
- **Filtering & Search**: Filter debts by pharmacist, status, or search by customer
- **Dashboard**: Overview of all debts, statistics, and overdue alerts
- **Admin Interface**: Full Django admin interface for data management

## Database Setup

This project uses **PostgreSQL** as the database. See [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed instructions.

### Quick Setup:

1. **Install PostgreSQL** (if not already installed)
   - Windows: Download from https://www.postgresql.org/download/windows/
   - Linux: `sudo apt-get install postgresql postgresql-contrib`
   - macOS: `brew install postgresql`

2. **Create database and user:**
   ```sql
   CREATE DATABASE pharmacy_db;
   CREATE USER pharmacy_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO pharmacy_user;
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env` (or create `.env` file)
   - Update database credentials in `.env`:
     ```
     DB_NAME=pharmacy_db
     DB_USER=pharmacy_user
     DB_PASSWORD=your_password
     DB_HOST=localhost
     DB_PORT=5432
     ```

## Setup Instructions

1. **Navigate to the project directory:**
   ```bash
   cd pharmacy_website
   ```

2. **Activate the virtual environment:**
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On Mac/Linux
   source venv/bin/activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```
   This will install:
   - Django 5.1.6
   - psycopg2-binary (PostgreSQL adapter)
   - openpyxl (for Excel import)
   - python-dotenv (for environment variables)
   - Pillow (for image handling)

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage Guide

### 1. Add cashier
- Go to "Manage" → "cashier" → "Add cashier"
- Enter pharmacist name, surname, phone, and email
- You can add up to 5 cashier (or more if needed)

### 2. Add Customers

**Option A: Manual Entry**
- Go to "Manage" → "Customers" → "Add Customer"
- Enter customer name, surname, place (where they're from), phone, and address
- Customers are automatically linked to debts

**Option B: Import from 1C File (Recommended for bulk import)**
- Go to "Manage" → "Customers" → "Import from 1C"
- Upload a CSV or Excel file exported from 1C
- The system automatically recognizes column names in multiple languages (Russian/English)
- Required columns: Name, Surname, Place
- Optional columns: Phone, Address
- Supports duplicate detection to avoid importing existing customers

### 3. Add a Debt
- Click "Add Debt" from the navigation or home page
- Select the pharmacist who gave the debt
- Select or add a customer
- Enter the amount
- Set the date given (defaults to today)
- Set the promise date (when customer promises to return money)
- Add optional description/notes
- Click "Add Debt"

### 4. View Debts
- **All Debts**: View all debts with filtering options
- **By Pharmacist**: Click on a pharmacist to see all their debts
- **Filter Options**:
  - Filter by pharmacist
  - Filter by status (Unpaid, Paid, Overdue)
  - Search by customer name, surname, or place

### 5. View Reminders
- Click "Reminders" in the navigation
- See all overdue debts grouped by pharmacist
- Overdue debts are automatically highlighted with days overdue

### 6. Mark Debt as Paid
- Open a debt detail page
- Click "Mark as Paid" button
- The debt will be marked as paid with the current date

## Management Commands

### Check Overdue Debts (Command Line)
Run this command to see overdue debts in the terminal:
```bash
python manage.py check_overdue_debts
```

This command groups overdue debts by pharmacist and displays:
- Total number of overdue debts
- Total amount overdue
- Details for each debt including days overdue

### Import Customers from 1C File (Command Line)
Import customers from a CSV or Excel file:
```bash
python manage.py import_customers path/to/file.csv
python manage.py import_customers path/to/file.xlsx --skip-duplicates
```

Options:
- `--skip-duplicates`: Skip customers that already exist (recommended)
- Supports CSV (.csv) and Excel (.xlsx, .xls) formats
- Automatically recognizes column names in Russian and English

## Models

### Pharmacist
- Name, Surname
- Phone, Email
- Automatically calculates total debt and overdue count

### Customer
- Name, Surname
- Place (where they're from)
- Phone, Address

### Debt
- Links to Pharmacist and Customer
- Amount
- Date Given (when debt was given)
- Promise Date (when customer promises to return money)
- Description/Notes
- Payment Status (Paid/Unpaid)
- Automatically calculates if overdue and days overdue

## Features Overview

### Dashboard (Home Page)
- Total unpaid debts count and amount
- Overdue debts count and amount
- Pharmacist overview with debt statistics
- Recent debts list
- Overdue debts alert section

### Debt Management
- Add new debts with all required information
- View debt details
- Mark debts as paid
- Filter and search debts
- View debts by pharmacist

### Reminders System
- Automatic detection of overdue debts
- Grouped by pharmacist for easy tracking
- Shows days overdue for each debt
- Accessible from navigation menu

## Admin Interface

Access the Django admin panel at `/admin/` to:
- Manage all pharmacists, customers, and debts
- Bulk edit records
- Advanced filtering and searching
- Export data

## Importing from 1C

### Supported File Formats
- **CSV** (.csv) - Works out of the box
- **Excel** (.xlsx, .xls) - Requires `openpyxl` package

### Column Name Recognition
The system automatically recognizes column names in multiple languages:

| Field | Supported Names |
|-------|----------------|
| Name | Имя, Name, FirstName, First Name, Имя клиента |
| Surname | Фамилия, Surname, LastName, Last Name, Фамилия клиента |
| Place | Место, Place, Город, City, Location, Адрес, Откуда |
| Phone | Телефон, Phone, Tel, Телефон клиента |
| Address | Адрес, Address, Полный адрес, Full Address |

### Example CSV Format
```csv
Name,Surname,Place,Phone,Address
Иван,Иванов,Москва,+7-999-123-4567,ул. Ленина, д. 1
Мария,Петрова,Санкт-Петербург,+7-999-765-4321,пр. Невский, д. 10
```

### Import Features
- **Duplicate Detection**: Automatically skips customers that already exist (same name, surname, and place)
- **Error Reporting**: Shows detailed errors for rows that couldn't be imported
- **Partial Updates**: Updates phone/address for existing customers if provided
- **Encoding Support**: Handles UTF-8, Windows-1251, and other common encodings

## Notes

- The system automatically tracks the current date when adding debts
- Promise dates are used to determine overdue status
- Overdue debts are calculated based on promise date vs. current date
- All dates are stored and displayed in the system timezone
- The system supports multiple debts per customer
- For Excel import, install openpyxl: `pip install openpyxl`

## Support

For issues or questions, check the Django documentation or review the code comments in the models, views, and templates.

