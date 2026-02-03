import os
from PyQt6.QtCore import QDir

path = QDir.tempPath() + "/phoenix_sidebar.lock"
print(f"Lock file path: {path}")

try:
    if os.path.exists(path):
        os.remove(path)
        print("Removed lock file via os.remove")
    else:
        print("File not found.")
except Exception as e:
    print(f"Error: {e}")
