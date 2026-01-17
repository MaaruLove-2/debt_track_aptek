#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple launcher for Django development server."""
import os
import sys
import subprocess

# Change to project directory
project_dir = r'D:\shared\code\debt-track'
os.chdir(project_dir)
print(f"Project directory: {os.getcwd()}")

# Check for virtual environment
venv_python = os.path.join(project_dir, 'venv2', 'Scripts', 'python.exe')
if os.path.exists(venv_python):
    python_cmd = venv_python
    print("Using virtual environment Python")
else:
    python_cmd = sys.executable
    print("Using system Python")
    # Check if Django is installed
    try:
        import django
        print(f"Django {django.get_version()} is available")
    except ImportError:
        print("Django not found. Installing dependencies...")
        subprocess.run([python_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)

# Check if migrations are needed
print("\nChecking database...")
subprocess.run([python_cmd, 'manage.py', 'check'], check=False)

# Start the server
print("\n" + "="*50)
print("Starting Django development server...")
print("Server will be available at: http://192.168.100.11:8000")
print("="*50 + "\n")
subprocess.run([
    python_cmd,
    'manage.py',
    'runserver',
    '0.0.0.0:8000'
])






