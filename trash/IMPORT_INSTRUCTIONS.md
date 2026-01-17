# How to Fix "openpyxl is required" Error

If you're getting the error "openpyxl is required for Excel file support", follow these steps:

## Step 1: Activate Virtual Environment

**On Windows:**
```bash
cd pharmacy_website
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
cd pharmacy_website
source venv/bin/activate
```

## Step 2: Install openpyxl

```bash
pip install openpyxl
```

## Step 3: Verify Installation

```bash
python -c "import openpyxl; print('openpyxl installed:', openpyxl.__version__)"
```

You should see: `openpyxl installed: 3.1.5` (or similar version)

## Step 4: Restart Django Server

**IMPORTANT:** You must restart the Django server after installing openpyxl!

1. Stop the current server (press Ctrl+C in the terminal where it's running)
2. Make sure virtual environment is activated
3. Start the server again:
   ```bash
   python manage.py runserver
   ```

## Step 5: Try Import Again

Now go to "Manage" → "Customers" → "Import from 1C" and upload your Excel file.

## Troubleshooting

If you still get the error:

1. **Check which Python is being used:**
   ```bash
   python --version
   which python  # On Mac/Linux
   where python  # On Windows
   ```

2. **Make sure you're in the virtual environment:**
   - Your terminal prompt should show `(venv)` at the beginning
   - If not, activate it again (see Step 1)

3. **Install openpyxl directly in the venv:**
   ```bash
   venv\Scripts\python.exe -m pip install openpyxl  # Windows
   venv/bin/python -m pip install openpyxl  # Mac/Linux
   ```

4. **Check if openpyxl is installed:**
   ```bash
   pip list | findstr openpyxl  # Windows
   pip list | grep openpyxl     # Mac/Linux
   ```

If you see `openpyxl` in the list, it's installed. The issue is likely that the Django server needs to be restarted.






