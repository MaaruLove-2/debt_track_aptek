# -*- coding: utf-8 -*-
import os
import sys
import subprocess

os.chdir(r'D:\новая папка\code\debt-track')

# Try venv first
venv_python = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python.exe')
if os.path.exists(venv_python):
    python = venv_python
else:
    python = sys.executable

# Install deps if needed
try:
    import django
except:
    print("Installing dependencies...")
    subprocess.run([python, '-m', 'pip', 'install', '-r', 'requirements.txt'])

# Run server
print("Starting server at http://127.0.0.1:8000")
subprocess.run([python, 'manage.py', 'runserver'])







