# Pharmacy Website Deployment Guide
## Server + Client Setup (6 Computers)

This guide explains how to set up one computer as a server and allow 5 other computers to access the application.

---

## 📋 Prerequisites

- All 6 computers on the same network (same Wi-Fi/router)
- Python installed on all computers (or at least on the server)
- All computers can see each other on the network

---

## 🖥️ PART 1: Server Setup (Main Computer)

### Step 1: Prepare the Server Computer

1. **Find the server's IP address:**
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., `192.168.1.100`). **Write this down!**

2. **Copy your project to the server computer** (if not already there)

### Step 2: Configure Django Settings

1. **Open `pharmacy_website/pharmacy/settings.py`**

2. **Update ALLOWED_HOSTS:**
   ```python
   ALLOWED_HOSTS = ['192.168.1.100', 'localhost', '127.0.0.1']
   # Replace 192.168.1.100 with your server's IP address
   # You can also add: ALLOWED_HOSTS = ['*'] for development (less secure)
   ```

3. **Make sure database is configured:**
   - If using SQLite (default): No changes needed
   - If using PostgreSQL: Make sure credentials are correct

### Step 3: Run Migrations (if not done)

```bash
cd pharmacy_website
python manage.py migrate
```

### Step 4: Collect Static Files (if needed)

```bash
python manage.py collectstatic --noinput
```

### Step 5: Create a Startup Script

Create a file `start_server.bat` in the `pharmacy_website` folder:

```batch
@echo off
echo Starting Pharmacy Server...
cd /d %~dp0
python manage.py runserver 0.0.0.0:8000
pause
```

**Or create `start_server.ps1` (PowerShell):**

```powershell
Write-Host "Starting Pharmacy Server..." -ForegroundColor Green
Set-Location $PSScriptRoot
python manage.py runserver 0.0.0.0:8000
```

### Step 6: Configure Windows Firewall

1. Open **Windows Defender Firewall**
2. Click **"Allow an app or feature through Windows Defender Firewall"**
3. Click **"Change Settings"** → **"Allow another app"**
4. Browse to `python.exe` (usually in `C:\Users\YourName\AppData\Local\Programs\Python\...`)
5. Check both **Private** and **Public** networks
6. Click **OK**

**OR** (Easier method):
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Django Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Step 7: Start the Server

Double-click `start_server.bat` or run:
```bash
python manage.py runserver 0.0.0.0:8000
```

You should see:
```
Starting development server at http://0.0.0.0:8000/
```

**Keep this window open!** The server must be running for other computers to access it.

---

## 💻 PART 2: Client Setup (Other 5 Computers)

### Option A: Access via Web Browser (Recommended - Easiest)

1. **Open a web browser** (Chrome, Firefox, Edge)

2. **Type the server's IP address:**
   ```
   http://192.168.1.100:8000
   ```
   (Replace `192.168.1.100` with your server's IP address)

3. **Bookmark this address** for easy access

4. **That's it!** All 5 computers can now access the application.

### Option B: Create Desktop Shortcut

1. **Right-click on Desktop** → **New** → **Shortcut**

2. **Enter the address:**
   ```
   http://192.168.1.100:8000
   ```

3. **Name it:** "Pharmacy System"

4. **Double-click the shortcut** to open the application

---

## 🔧 PART 3: Advanced Configuration

### Make Server Start Automatically (Optional)

1. **Create a scheduled task:**
   - Press `Win + R` → type `taskschd.msc`
   - Click **"Create Basic Task"**
   - Name: "Pharmacy Server"
   - Trigger: **"When the computer starts"**
   - Action: **"Start a program"**
   - Program: `python`
   - Arguments: `manage.py runserver 0.0.0.0:8000`
   - Start in: `C:\Users\YourName\Cursor\pharmacy_website`
   - Check **"Open the Properties dialog"**
   - In Properties → **"Run whether user is logged on or not"**
   - Click **OK**

### Use a Custom Port (if 8000 is busy)

In `start_server.bat`, change:
```batch
python manage.py runserver 0.0.0.0:8080
```

Then clients access: `http://192.168.1.100:8080`

### Use PostgreSQL on Server (Better for Multiple Users)

1. **Install PostgreSQL on server**
2. **Update `.env` file:**
   ```
   DB_ENGINE=postgresql
   DB_NAME=pharmacy_db
   DB_USER=pharmacy_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```
3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

---

## 🛠️ TROUBLESHOOTING

### Problem: "Can't connect to server"

**Solutions:**
1. Check server IP address: `ipconfig` on server
2. Make sure server is running: Check the terminal window
3. Check firewall: Allow port 8000
4. Ping test: On client, run `ping 192.168.1.100`
5. Check network: Make sure all computers are on same Wi-Fi/network

### Problem: "DisallowedHost" error

**Solution:**
- Update `ALLOWED_HOSTS` in `settings.py`:
  ```python
  ALLOWED_HOSTS = ['192.168.1.100', '*']  # For development
  ```

### Problem: Server IP changes (Dynamic IP)

**Solution:**
1. **Set static IP on server:**
   - Open **Network Settings** → **Change adapter options**
   - Right-click your network → **Properties**
   - Select **"Internet Protocol Version 4 (TCP/IPv4)"** → **Properties**
   - Select **"Use the following IP address"**
   - Enter: IP (e.g., `192.168.1.100`), Subnet mask (`255.255.255.0`), Gateway (router IP)
   - Click **OK**

2. **Or use computer name:**
   - Find computer name: `hostname` command
   - Access via: `http://COMPUTER-NAME:8000`

### Problem: Slow performance

**Solutions:**
1. Use PostgreSQL instead of SQLite
2. Use a production server (see Production Setup below)

---

## 🚀 PRODUCTION SETUP (For Better Performance)

For a more stable setup, use a production server:

### Option 1: Waitress (Windows-friendly)

1. **Install:**
   ```bash
   pip install waitress
   ```

2. **Create `start_production.bat`:**
   ```batch
   @echo off
   cd /d %~dp0
   waitress-serve --host=0.0.0.0 --port=8000 pharmacy.wsgi:application
   ```

### Option 2: Gunicorn (if using Linux/WSL)

1. **Install:**
   ```bash
   pip install gunicorn
   ```

2. **Run:**
   ```bash
   gunicorn --bind 0.0.0.0:8000 pharmacy.wsgi:application
   ```

---

## 📝 QUICK REFERENCE

### Server Commands:
```bash
# Start server
python manage.py runserver 0.0.0.0:8000

# Check IP address
ipconfig

# Test server locally
http://localhost:8000
```

### Client Access:
```
http://SERVER-IP:8000
```

### Important Files:
- `pharmacy_website/pharmacy/settings.py` - Configuration
- `start_server.bat` - Server startup script
- `.env` - Database credentials (if using PostgreSQL)

---

## ✅ CHECKLIST

**Server Setup:**
- [ ] Python installed
- [ ] Project files copied
- [ ] IP address found
- [ ] ALLOWED_HOSTS configured
- [ ] Migrations run
- [ ] Firewall configured
- [ ] Server started

**Client Setup:**
- [ ] All 5 computers on same network
- [ ] Browser bookmarks created
- [ ] Can access `http://SERVER-IP:8000`

---

## 📞 Need Help?

If you encounter issues:
1. Check server terminal for error messages
2. Verify IP address hasn't changed
3. Test with `ping SERVER-IP` from client
4. Check Windows Firewall settings
5. Make sure server is still running

---

**Good luck with your deployment! 🎉**



