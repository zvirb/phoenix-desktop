from phoenix.core.api_client import APIClient
from phoenix.core.token_manager import get_auth_token
from config import config

def probe_api():
    token = get_auth_token()
    if not token:
        print("No token found.")
        return

    client = APIClient(config.PHOENIX_API_URL, config.DEVICE_ID, verify_ssl=False)
    # Perform Auth Exchange
    print("Authenticating...")
    auth_res = client.authenticate(token)
    if 'access_token' not in auth_res:
        print(f"Auth failed: {auth_res}")
        return
    
    print("Auth success. Probing...")
    
    endpoints = [
        '/api/v1/health',
        '/api/v1/users/me',
        '/api/v1/user/me',
        '/api/v1/gamification/player',
        '/api/v1/gamification/profile',
        '/api/v1/gamification/stats',
        '/api/v1/focus',
    ]

    for ep in endpoints:
        res = client._make_request('GET', ep)
        print(f"{ep}: {res}")

if __name__ == "__main__":
    probe_api()
