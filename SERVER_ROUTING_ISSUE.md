# Phoenix Desktop Tracker - Server Routing Issue

## 🔴 Critical Issue: API Routes Returning HTML Instead of JSON

### Problem Summary
The Phoenix backend server at `https://phoenix.aiwfe.com` is incorrectly serving the React frontend HTML to API endpoints instead of processing API requests. This causes the desktop tracker client to fail when parsing responses.

---

## 📋 Issue Details

### Affected Endpoints
- `/api/screentime/heartbeat` (POST)
- `/api/screentime/capture` (POST) - likely affected

### Expected Behavior
```json
{
  "status": "success",
  "timestamp": 1733183903.520,
  "message": "Heartbeat recorded"
}
```

### Actual Behavior
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="/favicon.ico">
    <script defer src="/vendors.js"></script>
    <script defer src="/main.js"></script>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>
```

### Response Headers
```
Content-Type: text/html; charset=utf-8
Server: cloudflare
```

---

## 🔍 Root Cause Analysis

### Likely Causes
1. **API routes not registered** - Backend framework not properly handling `/api/*` paths
2. **Reverse proxy misconfiguration** - Nginx/Apache not routing API requests correctly
3. **SPA fallback catching API routes** - Frontend routing catching all requests including API paths
4. **Order of middleware** - API handlers registered after SPA fallback handler

### Request Details
```bash
# Desktop Client Request
POST https://phoenix.aiwfe.com/api/screentime/heartbeat
Headers:
  Authorization: Bearer [JWT_TOKEN]
  X-Device-ID: tufboi
  Content-Type: application/json
  User-Agent: PhoenixTracker/tufboi

Body:
{
  "timestamp": 1733183903.520,
  "app_name": "VSCode",
  "window_title": "api_client.py - Phoenix Desktop",
  "is_idle": false
}
```

---

## 🛠️ Troubleshooting Steps

### 1. Verify API Routes Are Registered
```python
# In your backend (Python/Flask example)
@app.route('/api/screentime/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    # Process heartbeat
    return jsonify({"status": "success", "timestamp": data.get("timestamp")})

# Verify route is registered
print(app.url_map)
```

### 2. Check Route Priority
Ensure API routes are registered **before** the SPA fallback:

```python
# ✅ CORRECT ORDER
# 1. Register API routes first
app.register_blueprint(api_blueprint, url_prefix='/api')

# 2. Then add SPA fallback
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    return send_from_directory('build', 'index.html')
```

```python
# ❌ WRONG ORDER - This will break API routes
@app.route('/<path:path>')
def serve_spa(path):
    return send_from_directory('build', 'index.html')

app.register_blueprint(api_blueprint, url_prefix='/api')  # Too late!
```

### 3. Test API Endpoint Directly
```bash
# Test with curl
curl -X POST https://phoenix.aiwfe.com/api/screentime/heartbeat \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "X-Device-ID: test-device" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": 1733183903,
    "app_name": "TestApp",
    "window_title": "Test Window",
    "is_idle": false
  }' \
  -v

# Expected: JSON response
# Actual: HTML response (current issue)
```

### 4. Check Reverse Proxy Configuration

#### Nginx Configuration
```nginx
server {
    listen 443 ssl;
    server_name phoenix.aiwfe.com;

    # API routes - proxy to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend - serve static files
    location / {
        root /var/www/phoenix/build;
        try_files $uri /index.html;
    }
}
```

#### Apache Configuration
```apache
<VirtualHost *:443>
    ServerName phoenix.aiwfe.com

    # API routes - proxy to backend
    ProxyPass /api/ http://localhost:8000/api/
    ProxyPassReverse /api/ http://localhost:8000/api/

    # Frontend - serve static files
    DocumentRoot /var/www/phoenix/build
    <Directory /var/www/phoenix/build>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
        
        # Fallback to index.html for SPA routing
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteCond %{REQUEST_URI} !^/api/
        RewriteRule . /index.html [L]
    </Directory>
</VirtualHost>
```

### 5. Verify Backend is Running
```bash
# Check if backend process is running
ps aux | grep python
# or
systemctl status phoenix-backend

# Check backend logs
tail -f /var/log/phoenix/backend.log
```

---

## 📝 Expected API Contract

### Heartbeat Endpoint
**Endpoint:** `POST /api/screentime/heartbeat`

**Request:**
```json
{
  "timestamp": 1733183903.520,
  "app_name": "VSCode",
  "window_title": "api_client.py - Phoenix Desktop",
  "is_idle": false
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "timestamp": 1733183903.520,
  "device_id": "tufboi",
  "cached": false
}
```

**Error Response (401 Unauthorized):**
```json
{
  "status": "error",
  "message": "Invalid or expired token",
  "code": "INVALID_TOKEN"
}
```

### Capture Endpoint
**Endpoint:** `POST /api/screentime/capture`

**Request:** (multipart/form-data)
```
file: screenshot.jpg (binary)
device_id: tufboi
timestamp: 1733183903.520
app_name: VSCode
window_title: api_client.py
```

**Success Response (200):**
```json
{
  "status": "success",
  "timestamp": 1733183903.520,
  "image_id": "img_abc123xyz",
  "context_summary": "User is coding in VSCode, editing API client file"
}
```

---

## 🔧 Client-Side Behavior

### Current Status
The Desktop Tracker is **partially working**:
- ✅ Application is running
- ✅ Detecting user activity
- ✅ Attempting to send heartbeats
- ✅ Caching failed requests for retry
- ❌ Cannot communicate with server (routing issue)
- ⚠️ May be paused by gaming detection (steamwebhelper.exe)

### Error Handling
The client gracefully handles the server error:
```python
# From api_client.py
except requests.exceptions.RequestException as e:
    logger.warning(f"Heartbeat request failed: {e}. Caching for retry.")
    self.cache.add_item('heartbeat', payload)
    return {'status': 'cached', 'error': str(e)}
```

Cached requests will automatically retry when the server is fixed.

---

## ✅ Verification Checklist

Once you've made changes, verify:

- [ ] `curl` test returns JSON (not HTML)
- [ ] Response has `Content-Type: application/json`
- [ ] Status code is 200 for valid requests
- [ ] 401 for invalid/missing tokens
- [ ] Desktop client logs show "Heartbeat sent" without errors
- [ ] No cached items accumulating in client

---

## 🐛 Additional Issues Found

### Token Encoding Issue
The debug output shows the token has UTF-16 encoding with null bytes:
```
Authorization: Bearer b'p\\x00h\\x00x\\x00_\\x00z\\x00s\\x00x\\x00y\\x00F\\x00X\\x00E\\x00D\\x00
```

This suggests the token is being stored in UTF-16 instead of UTF-8. **This should be fixed client-side** after the routing issue is resolved.

---

## 📞 Support

### Desktop Client Logs
```
Location: C:\Users\marku\Documents\phoenix-desktop\logs\
Latest: phoenix_tracker_20251203_093822.log
```

### Test Script
A debug script has been created at:
```
C:\Users\marku\Documents\phoenix-desktop\debug_server.py
```

Run with:
```bash
cd C:\Users\marku\Documents\phoenix-desktop
venv\Scripts\python.exe debug_server.py
```

---

**Last Updated:** 2025-12-03  
**Status:** 🔴 Critical - Blocking all desktop tracker functionality
