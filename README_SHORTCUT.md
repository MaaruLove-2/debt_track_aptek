# Desktop Shortcut Setup

This guide will help you create a desktop shortcut to start the Django development server and open the website.

## Quick Setup

1. **Double-click `create_shortcut.bat`** in the `pharmacy_website` folder
2. A shortcut named "Aptek Borc İzləyicisi" will be created on your desktop
3. Double-click the desktop shortcut to start the server and open the website

## Manual Setup (Alternative)

If the automatic setup doesn't work, you can create the shortcut manually:

1. Right-click on your desktop
2. Select "New" → "Shortcut"
3. Browse to the `pharmacy_website` folder and select `start_server.vbs`
4. Name it "Aptek Borc İzləyicisi"
5. Click "Finish"

## How It Works

- **`start_server.bat`**: Main script that starts the Django server and opens the browser
- **`start_server.vbs`**: Runs the batch file without showing a command window
- **`create_shortcut.bat`**: Creates the desktop shortcut automatically
- **`create_desktop_shortcut.ps1`**: PowerShell script that creates the shortcut

## Requirements

- Python must be installed and in your system PATH
- Django must be installed (`pip install django`)
- All project dependencies must be installed

## Troubleshooting

If the shortcut doesn't work:

1. Make sure Python is installed: Open Command Prompt and type `python --version`
2. Make sure you're in the correct directory (should contain `manage.py`)
3. Try running `start_server.bat` directly to see any error messages
4. Check that the Django server can start manually: `python manage.py runserver`

