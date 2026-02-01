import win32cred
import win32con

print("Checking win32cred attributes:")
try:
    print(f"win32cred.CRED_TYPE_GENERIC: {win32cred.CRED_TYPE_GENERIC}")
except AttributeError:
    print("win32cred.CRED_TYPE_GENERIC not found")

print("\nChecking win32con attributes:")
try:
    print(f"win32con.CRED_TYPE_GENERIC: {win32con.CRED_TYPE_GENERIC}")
except AttributeError:
    print("win32con.CRED_TYPE_GENERIC not found")
