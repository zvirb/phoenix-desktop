import win32cred
import win32con

print("Checking win32cred attributes:")
try:
    print(f"win32cred.CRED_PERSIST_LOCAL_MACHINE: {win32cred.CRED_PERSIST_LOCAL_MACHINE}")
except AttributeError:
    print("win32cred.CRED_PERSIST_LOCAL_MACHINE not found")

print("\nChecking win32con attributes:")
try:
    print(f"win32con.CRED_PERSIST_LOCAL_MACHINE: {win32con.CRED_PERSIST_LOCAL_MACHINE}")
except AttributeError:
    print("win32con.CRED_PERSIST_LOCAL_MACHINE not found")
