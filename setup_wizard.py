"""
Setup wizard for Phoenix Desktop Tracker.
Handles first-time configuration.
"""
import os
import socket
from pathlib import Path
from typing import Optional


def print_header(text: str) -> None:
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)
    print()


def print_section(text: str) -> None:
    """Print a section divider."""
    print()
    print(f"--- {text} ---")
    print()


def get_default_device_id() -> str:
    """Generate a default device ID."""
    hostname = socket.gethostname().lower()
    # Clean the hostname to make it URL-friendly
    hostname = ''.join(c if c.isalnum() or c == '-' else '-' for c in hostname)
    return f"desktop-{hostname}"


def validate_url(url: str) -> bool:
    """Validate that a URL is properly formatted."""
    if not url:
        return False
    
    # Must start with https://
    if not url.startswith('https://'):
        print("  ⚠️  URL must start with 'https://' for security")
        return False
    
    # Basic format check
    if '.' not in url and 'localhost' not in url:
        print("  ⚠️  URL doesn't appear to be valid")
        return False
    
    return True


def validate_device_id(device_id: str) -> bool:
    """Validate device ID format."""
    if not device_id:
        return False
    
    # Should be reasonable length
    if len(device_id) < 3:
        print("  ⚠️  Device ID is too short (minimum 3 characters)")
        return False
    
    if len(device_id) > 50:
        print("  ⚠️  Device ID is too long (maximum 50 characters)")
        return False
    
    # Should only contain alphanumeric, hyphens, underscores
    if not all(c.isalnum() or c in '-_' for c in device_id):
        print("  ⚠️  Device ID should only contain letters, numbers, hyphens, and underscores")
        return False
    
    return True


def prompt_for_url() -> str:
    """Prompt user for Phoenix API URL."""
    print("Enter your Phoenix server URL.")
    print("Examples:")
    print("  - https://phoenix.yourcompany.com")
    print("  - https://192.168.1.100:8000")
    print("  - https://localhost:8000 (for local testing)")
    print()
    
    while True:
        url = input("Phoenix API URL: ").strip()
        
        if not url:
            print("  ⚠️  URL cannot be empty")
            continue
        
        # Add https:// if user forgot it
        if not url.startswith('http://') and not url.startswith('https://'):
            print(f"  → Adding 'https://' prefix")
            url = f"https://{url}"
        
        # Force HTTPS (unless localhost for testing)
        if url.startswith('http://') and 'localhost' not in url:
            url = url.replace('http://', 'https://')
            print(f"  → Changed to HTTPS for security: {url}")
        
        if validate_url(url):
            # Remove trailing slash
            url = url.rstrip('/')
            return url


def prompt_for_device_id(default: str) -> str:
    """Prompt user for device ID."""
    print("Enter a unique identifier for this device.")
    print("This will be used to track which device sent the data.")
    print()
    print(f"Suggested ID: {default}")
    print()
    
    while True:
        device_id = input(f"Device ID [{default}]: ").strip()
        
        # Use default if empty
        if not device_id:
            device_id = default
        
        if validate_device_id(device_id):
            return device_id


def update_env_file(api_url: str, device_id: str) -> bool:
    """Update the .env file with configuration."""
    env_path = Path(__file__).parent / '.env'
    env_example_path = Path(__file__).parent / '.env.example'
    
    try:
        # Read the example or existing file
        if env_path.exists():
            content = env_path.read_text()
        elif env_example_path.exists():
            content = env_example_path.read_text()
        else:
            # Create minimal .env content
            content = """# Phoenix Desktop Tracker Configuration
PHOENIX_API_URL=https://your-phoenix-server.com
DEVICE_ID=workstation-1

# Capture Settings
CAPTURE_INTERVAL=60
HEARTBEAT_INTERVAL=60
SIMILARITY_THRESHOLD=0.95

# Gaming Process Blacklist (comma-separated, case-insensitive)
GAMING_PROCESSES=steam.exe,dota2.exe,csgo.exe,cyberpunk2077.exe,valorant.exe

# Performance Settings
MAX_IMAGE_WIDTH=1024
JPEG_QUALITY=70

# Security Settings
VERIFY_SSL=true
REQUEST_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
"""
        
        # Update the values
        lines = []
        updated_url = False
        updated_device = False
        
        for line in content.split('\n'):
            if line.strip().startswith('PHOENIX_API_URL='):
                lines.append(f'PHOENIX_API_URL={api_url}')
                updated_url = True
            elif line.strip().startswith('DEVICE_ID='):
                lines.append(f'DEVICE_ID={device_id}')
                updated_device = True
            else:
                lines.append(line)
        
        # Add if not found
        if not updated_url:
            lines.insert(1, f'PHOENIX_API_URL={api_url}')
        if not updated_device:
            lines.insert(2, f'DEVICE_ID={device_id}')
        
        # Write back
        env_path.write_text('\n'.join(lines))
        
        print(f"✅ Configuration saved to: {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False


def needs_setup() -> bool:
    """Check if initial setup is needed."""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        return True
    
    # Check if the .env has placeholder values
    try:
        content = env_path.read_text()
        
        # Check for placeholder URL
        if 'your-phoenix-server.com' in content:
            return True
        
        if 'PHOENIX_API_URL=https://localhost:8000' in content:
            # localhost is fine, but let's check if user explicitly set it
            # If they're using the example, they probably need setup
            if 'DEVICE_ID=workstation-1' in content:
                return True
        
        # Check if URL is set at all
        url_set = False
        for line in content.split('\n'):
            if line.strip().startswith('PHOENIX_API_URL='):
                value = line.split('=', 1)[1].strip()
                if value and value != 'https://localhost:8000':
                    url_set = True
                break
        
        if not url_set:
            return True
            
    except Exception:
        return True
    
    return False


def run_wizard() -> bool:
    """
    Run the initial setup wizard.
    
    Returns:
        True if setup completed successfully
    """
    print_header("Phoenix Desktop Tracker - Initial Setup")
    
    print("Welcome! Let's get your desktop tracker configured.")
    print()
    print("This wizard will help you set up:")
    print("  1. Phoenix server connection")
    print("  2. Device identification")
    print()
    input("Press Enter to continue...")
    
    # Get Phoenix API URL
    print_section("Phoenix Server Configuration")
    api_url = prompt_for_url()
    
    # Get Device ID
    print_section("Device Identification")
    default_device_id = get_default_device_id()
    device_id = prompt_for_device_id(default_device_id)
    
    # Save configuration
    print_section("Saving Configuration")
    if not update_env_file(api_url, device_id):
        return False
    
    # Summary
    print_header("Setup Complete!")
    print("✅ Configuration saved successfully")
    print()
    print("Configuration Summary:")
    print(f"  Phoenix API URL: {api_url}")
    print(f"  Device ID: {device_id}")
    print()
    print("Next steps:")
    print("  1. Set up authentication token:")
    print("     python token_manager.py setup")
    print()
    print("  2. Start the tracker:")
    print("     python desktop_tracker.py")
    print()
    
    return True


def main():
    """Entry point for setup wizard."""
    if run_wizard():
        print("You can always edit your configuration in the .env file")
    else:
        print("Setup was not completed. Please try again.")


if __name__ == "__main__":
    main()
