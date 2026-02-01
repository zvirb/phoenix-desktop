# Phoenix Desktop Tracker - Authentication Diagnostic Report

**Generated:** 2025-12-03 11:39 AEDT

## 🔴 Issue: Token Authentication Failing

### Current Status
- ✅ Server routing: WORKING (returning JSON)
- ✅ Token encoding: FIXED (UTF-16 → UTF-8)
- ✅ Token storage: WORKING (stored correctly)
- ❌ Token authentication: FAILING (401 Unauthorized)

---

## 📋 Token Details

**Stored Token:**
```
phx_efhKT8cpu1ZDH3WBgZGPiAxd-NbFlPnQ3-vtn0EIIy56RQjgySrjKm29QPG7u4o6
```

**Length:** 68 characters  
**Format:** `phx_` prefix + 64 characters  
**Storage:** Windows Credential Manager (decoded from UTF-16LE)

---

## 🧪 Test Results

All three authentication methods tested:

### Test 1: Minimal Headers
```bash
POST https://phoenix.aiwfe.com/api/screentime/heartbeat
Authorization: Bearer phx_efhKT8cpu1ZDH3WB...
Content-Type: application/json

Response: 401 - {"detail":"Invalid or expired token"}
```

### Test 2: With X-Device-ID Header
```bash
POST https://phoenix.aiwfe.com/api/screentime/heartbeat
Authorization: Bearer phx_efhKT8cpu1ZDH3WB...
X-Device-ID: tufboi
Content-Type: application/json

Response: 401 - {"detail":"Invalid or expired token"}
```

### Test 3: With device_id in Payload
```bash
POST https://phoenix.aiwfe.com/api/screentime/heartbeat
Authorization: Bearer phx_efhKT8cpu1ZDH3WB...
Content-Type: application/json
Body: { "device_id": "tufboi", ... }

Response: 401 - {"detail":"Invalid or expired token"}
```

**Result:** All formats rejected with 401

---

## 🔍 Root Cause Analysis

Since the token is consistently rejected regardless of request format, the issue is **server-side token validation**, not client configuration.

### Likely Causes (Backend):

1. **Token Not Saved in Database**
   - Token was generated in frontend but not persisted
   - Database transaction failed/rolled back
   - Token creation endpoint has a bug

2. **Device ID Mismatch**
   - Token was created for a different device_id
   - Backend expects exact match: `tufboi`
   - Case sensitivity issue (e.g., `tufboi` vs `TufBoi`)

3. **Token Format Issue**
   - Backend doesn't expect the `phx_` prefix
   - Wrong token type (e.g., user token vs device token)
   - Encoding issue in backend storage

4. **Token Validation Logic**
   - JWT signature validation failing
   - Token lookup query has bug
   - Token marked as expired/revoked

---

## 🛠️ Backend Troubleshooting Steps

### Step 1: Check Backend Logs
Look for authentication errors when this token is used:
```bash
# Check recent logs
tail -f /var/log/phoenix/backend.log | grep -i "auth\|token\|401"

# Or in application logs
grep "phx_efhKT8cpu1ZDH3WB" /var/log/phoenix/*.log
```

### Step 2: Verify Token in Database
Check if the token exists in your database:
```sql
-- PostgreSQL example
SELECT * FROM device_tokens 
WHERE token = 'phx_efhKT8cpu1ZDH3WBgZGPiAxd-NbFlPnQ3-vtn0EIIy56RQjgySrjKm29QPG7u4o6';

-- Check device association
SELECT * FROM device_tokens dt
JOIN devices d ON dt.device_id = d.id
WHERE d.device_name = 'tufboi';
```

### Step 3: Test Token Validation Manually
In your backend code/console:
```python
# Example Django/Python backend
from your_app.models import DeviceToken

token_string = "phx_efhKT8cpu1ZDH3WBgZGPiAxd-NbFlPnQ3-vtn0EIIy56RQjgySrjKm29QPG7u4o6"
try:
    token = DeviceToken.objects.get(token=token_string)
    print(f"Token found: {token}")
    print(f"Device: {token.device}")
    print(f"Active: {token.is_active}")
    print(f"Expires: {token.expires_at}")
except DeviceToken.DoesNotExist:
    print("Token not found in database!")
```

### Step 4: Check Token Generation Code
Review your token generation endpoint:
```python
# Example - ensure token is saved
@api.post("/tokens")
def create_device_token(device_id: str):
    token = generate_token()  # phx_xxx...
    
    # Make sure this is saved!
    db_token = DeviceToken.create(
        token=token,
        device_id=device_id,
        created_at=datetime.now()
    )
    db.session.add(db_token)
    db.session.commit()  # Don't forget to commit!
    
    return {"token": token}
```

### Step 5: Test with curl
From your server (to bypass any proxy/CDN issues):
```bash
# On backend server
curl -X POST http://localhost:8000/api/screentime/heartbeat \
  -H "Authorization: Bearer phx_efhKT8cpu1ZDH3WBgZGPiAxd-NbFlPnQ3-vtn0EIIy56RQjgySrjKm29QPG7u4o6" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": 1733187573,
    "app_name": "CurlTest",
    "window_title": "Test",
    "is_idle": false
  }' \
  -v
```

---

## ✅ Client-Side Verification (Already Done)

- ✅ Token encoding: Fixed UTF-16LE decoding
- ✅ Token storage: Correct in Windows Credential Manager
- ✅ Token retrieval: Working (`phx_efhKT8cpu1ZDH3WB...`)
- ✅ Request format: Tested 3 different formats
- ✅ Headers: Correctly formatted
- ✅ Device ID: Set to `tufboi`

---

## 🎯 Recommended Action

**The client is working correctly.** The issue is in the backend token validation.

### Immediate Next Steps:
1. Check backend logs for authentication errors
2. Verify the token exists in your database
3. Confirm device_id association is `tufboi`
4. Test token validation logic directly
5. Generate a fresh token and verify it's saved before using

### Alternative Test:
Create a **new device** with a **new token** from scratch:
1. Create device with name `test-device-001`
2. Generate token for that device
3. Copy token **immediately** after generation
4. Update desktop tracker with new device_id and token
5. Test immediately

This will help isolate whether it's a token generation issue or device association issue.

---

## 📞 Support Information

### Desktop Client
- **Version:** Running from `c:\Users\marku\Documents\phoenix-desktop\`
- **Device ID:** `tufboi`
- **Token Location:** Windows Credential Manager → `PhoenixTracker_tufboi`

### Backend
- **URL:** `https://phoenix.aiwfe.com`
- **API Endpoint:** `/api/screentime/heartbeat`
- **Expected Response:** `200 OK` with JSON

### Test Scripts
Located in `c:\Users\marku\Documents\phoenix-desktop\`:
- `check_token.py` - View stored token
- `test_auth.py` - Test authentication
- `debug_server.py` - Full request/response debug
- `update_token.py` - Update stored token

---

**Status:** Waiting for backend token validation fix or fresh token generation.
