# test_imports.py
import sys
import PyQt6

print("--- sys.executable ---")
print(sys.executable) # This will show the Python interpreter VS Code is ACTUALLY using to run this
print("\n--- sys.path ---")
for p in sys.path:
    print(p)

print("\n--- PyQt6 location ---")
print(PyQt6.__file__) # Where is PyQt6 itself located?

print("\n--- Attempting to import QtCharts ---")
try:
    from PyQt6 import QtCharts
    print("SUCCESS: PyQt6.QtCharts imported!")
    print(QtCharts) # Print the module object
except ImportError as e:
    print(f"ERROR: Could not import PyQt6.QtCharts: {e}")
except Exception as e_gen:
    print(f"GENERAL ERROR during QtCharts import: {e_gen}")