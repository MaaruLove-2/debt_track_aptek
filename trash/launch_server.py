#!/usr/bin/env python
"""Launcher script to find and start the Django server."""
import os
import sys
import subprocess

# Try to find the project directory
possible_paths = [
    os.path.dirname(os.path.abspath(__file__)),
    os.getcwd(),
    r"\\desktop-1\новая папка\code\debt-track",
]

project_path = None
for path in possible_paths:
    manage_py = os.path.join(path, "manage.py")
    if os.path.exists(manage_py):
        project_path = path
        break

if not project_path:
    # Try to search for manage.py
    for root, dirs, files in os.walk(os.path.expanduser("~")):
        if "manage.py" in files:
            project_path = root
            break
        # Limit search depth
        if root.count(os.sep) > 5:
            dirs[:] = []

if project_path:
    print(f"Found project at: {project_path}")
    os.chdir(project_path)
    
    # Check for virtual environment
    venv_python = os.path.join(project_path, "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        python_cmd = venv_python
        print("Using virtual environment Python")
    else:
        python_cmd = sys.executable
        print("Using system Python")
    
    # Start the server
    print("Starting Django development server...")
    print("=" * 50)
    subprocess.run([python_cmd, "manage.py", "runserver"])
else:
    print("ERROR: Could not find project directory!")
    print("Please navigate to the project directory and run: python manage.py runserver")
    sys.exit(1)





