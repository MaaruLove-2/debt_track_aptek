# Admin Panel Guide

## Overview
The admin panel allows staff/superuser accounts to manage all pharmacists, view all debts across all pharmacists, and perform administrative tasks.

## Accessing the Admin Panel

1. **Create a Superuser Account** (if you don't have one):
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

2. **Login** with your superuser credentials at `/login/`

3. **Access Admin Dashboard**:
   - After login, staff/superuser accounts are automatically redirected to the admin dashboard
   - Or click on the "Admin" menu in the navigation bar
   - Or go directly to `/admin/dashboard/`

## Admin Features

### 1. Admin Dashboard (`/admin/dashboard/`)
- **Overview Statistics**: 
  - Total unpaid debts across all pharmacists
  - Total overdue debts
  - Total amounts
- **Pharmacist Overview Table**: 
  - See all pharmacists
  - View their debt counts and amounts
  - See which pharmacists have user accounts
  - Quick access to change passwords
- **Recent Debts**: Latest debts from all pharmacists
- **Overdue Debts**: All overdue debts across the system

### 2. All Debts View (`/admin/debts/`)
- View all debts from all pharmacists
- **Filter Options**:
  - By pharmacist
  - By status (unpaid, paid, overdue)
  - Search by customer name, pharmacist name, or description
- See which pharmacist owns each debt

### 3. Pharmacist Management (`/admin/pharmacists/`)
- **List All Pharmacists**:
  - See all pharmacists in the system
  - View their user accounts
  - See debt statistics per pharmacist
  - Quick access to change passwords

### 4. Add New Pharmacist (`/admin/pharmacists/add/`)
- Create a new pharmacist account
- Automatically creates a user account with username and password
- Fill in:
  - Username (for login)
  - Password (minimum 8 characters)
  - Confirm password
  - Name, Surname
  - Phone, Email (optional)

### 5. Pharmacist Detail (`/admin/pharmacists/<id>/`)
- View detailed information about a pharmacist
- See all their debts
- Filter debts by status
- Access password change option

### 6. Change Password (`/admin/pharmacists/<id>/change-password/`)
- Reset a pharmacist's password if they forget it
- Enter new password (minimum 8 characters)
- Confirm password
- Password is immediately updated

## Navigation

The admin menu appears in the navigation bar for staff/superuser accounts:
- **Admin Panel**: Dashboard overview
- **All Debts**: View all debts
- **Manage Pharmacists**: List and manage pharmacists
- **Django Admin**: Link to Django's built-in admin (for advanced management)

## Important Notes

1. **Staff vs Superuser**:
   - Both `is_staff=True` and `is_superuser=True` users can access the admin panel
   - Regular pharmacists (without staff status) cannot access admin features

2. **Pharmacist Accounts**:
   - Each pharmacist can have a linked user account
   - If a pharmacist doesn't have a user account, they cannot log in
   - Use the "Add Pharmacist" form to create both pharmacist and user account together

3. **Password Management**:
   - Admins can change any pharmacist's password
   - New passwords must be at least 8 characters
   - Passwords are stored securely (hashed)

4. **Debt Visibility**:
   - Regular pharmacists: Only see their own debts
   - Admins: See all debts from all pharmacists
   - Customers: Shared globally (all pharmacists can see all customers)

## Making a User an Admin

To make an existing user an admin:

1. **Via Django Admin** (`/admin/`):
   - Go to Users section
   - Find the user
   - Check "Staff status" and/or "Superuser status"
   - Save

2. **Via Python Shell**:
   ```python
   python manage.py shell
   ```
   ```python
   from django.contrib.auth.models import User
   user = User.objects.get(username='username')
   user.is_staff = True
   user.is_superuser = True
   user.save()
   ```

## Security

- All admin views require authentication and staff/superuser status
- Regular pharmacists cannot access admin URLs even if they know them
- Password changes are logged in Django's user system
- All admin actions are protected by `@login_required` and `@user_passes_test(is_admin)` decorators




