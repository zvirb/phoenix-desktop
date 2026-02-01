# Phoenix Desktop Tracker - Authentication Flow Update

## ✅ GOOD NEWS: Device Authentication is Working!

### What's Fixed
1. ✅ Updated endpoints to use `/api/v1/*` instead of `/api/*`
2. ✅ Device authentication endpoint working: `/api/v1/devices/authenticate`
3. ✅ Token is valid and properly decoded
4. ✅ Desktop tracker connects and authenticates successfully

### Authentication Test Results

#### ✅ Device Authentication - WORKING
```bash
POST https://phoenix.aiwfe.com/api/v1/devices/authenticate
Authorization: Bearer phx_efhKT8cpu1ZDH3WB...

Response: 200 OK
{
  "valid": true,
  "user_id": "47fb8244-ecaa-404b-b1b1-2f1048d6cea9",
  "email": "markuszvirbulis@gmail.com",
  "display_name": "Markus",
  "device_name": "TufBoi"
}
```

#### ❌ Heartbeat Endpoint - Still 401
```bash
POST https://phoenix.aiwfe.com/api/v1/screentime/heartbeat
Authorization: Bearer phx_efhKT8cpu1ZDH3WB...

Response: 401 Unauthorized
{"detail":"Invalid or expired token"}
```

---

## 🔍 Problem Analysis

The device token works for `/api/v1/devices/authenticate` but NOT for `/api/v1/screentime/heartbeat`.

This suggests one of two scenarios:

### Scenario 1: Session-Based Authentication
The backend might expect:
1. Authenticate first with device token → get session token/JWT
2. Use session token for subsequent heartbeat/capture requests

### Scenario 2: Different Middleware
The heartbeat endpoint might have different authentication middleware that doesn't recognize device tokens.

---

## ❓ Questions for Backend Check

1. **Does `/api/v1/screentime/heartbeat` support device tokens?**
   - Or does it only support user JWT tokens?
   
2. **Is there a session flow?**
   - Do we need to call `/authenticate` first and get a session token?
   - Should we cache the session token and refresh it?

3. **What headers does heartbeat expect?**
   - Just `Authorization: Bearer {device_token}`?
   - Or something additional like `X-Session-Token`?

4. **Check backend code:**
   ```python
   # What authentication does the heartbeat endpoint use?
   @router.post("/api/v1/screentime/heartbeat")
   @requires_auth(...)  # What's here?
   def heartbeat(data: HeartbeatData):
       ...
   ```

---

## 🛠️ Desktop Tracker Updates Made

### config.py
```python
# Added v1 to endpoints
@property
def auth_url(self) -> str:
    return f"{self.PHOENIX_API_URL}/api/v1/devices/authenticate"

@property  
def heartbeat_url(self) -> str:
    return f"{self.PHOENIX_API_URL}/api/v1/screentime/heartbeat"

@property
def capture_url(self) -> str:
    return f"{self.PHOENIX_API_URL}/api/v1/screentime/capture"
```

### api_client.py
```python
def test_connection(self) -> bool:
    """Test using device authentication endpoint."""
    response = self.session.post(
        config.auth_url,
        timeout=config.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    
    data = response.json()
    if data.get('valid'):
        logger.info(f"Device authenticated: {data.get('device_name')}")
        return True
    return False
```

---

## 🎯 Next Steps

### Option A: If Backend Supports Device Tokens for Heartbeat
Update the heartbeat endpoint's authentication middleware to accept device tokens the same way `/authenticate` does.

### Option B: If Session Flow is Intended
We need to:
1. Call `/api/v1/devices/authenticate` on startup
2. Extract session token from response (if provided)
3. Use session token for heartbeat/capture requests
4. Implement token refresh logic

### Recommended: Check Backend Route Definitions
```python
# In your FastAPI/Flask backend
@router.post("/api/v1/screentime/heartbeat")
# What middleware/dependency is here? Should match /devices/authenticate
async def create_heartbeat(data: HeartbeatData, device: Device = Depends(get_current_device)):
    ...
```

---

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Device Token | ✅ Working | Properly stored and decoded |
| `/api/v1/devices/authenticate` | ✅ Working | Returns valid device info |
| `/api/v1/screentime/heartbeat` | ❌ Failing | 401 - Doesn't accept device token |
| `/api/v1/screentime/capture` | ❓ Unknown | Likely same issue as heartbeat |

---

## 🔧 Temporary Workaround

Until the backend is updated, the tracker will:
- ✅ Successfully authenticate on startup
- ❌ Cache all heartbeats/screenshots locally
- 🔄 Retry when connection is restored

**No data is lost** - everything is cached and will upload once the heartbeat endpoint accepts device tokens.

---

**Last Updated:** 2025-12-03 11:46 AEDT  
**Status:** ⏸️ Waiting for backend heartbeat endpoint to support device tokens
