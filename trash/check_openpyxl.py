"""
Quick script to check if openpyxl is available in the current Python environment
Run this to verify your Django server can import openpyxl
"""
import sys

print("=" * 60)
print("Python Environment Check")
print("=" * 60)
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print()

try:
    import openpyxl
    print("[OK] openpyxl is installed!")
    print(f"  Version: {openpyxl.__version__}")
    print(f"  Location: {openpyxl.__file__}")
except ImportError as e:
    print("[ERROR] openpyxl is NOT installed!")
    print(f"  Error: {e}")
    print()
    print("To install, run:")
    print(f"  {sys.executable} -m pip install openpyxl")

print()
print("=" * 60)

