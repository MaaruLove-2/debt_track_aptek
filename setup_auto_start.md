# Setup Auto-Start Server (No Window)

Choose one of these methods to run the server automatically in the background:

---

## 🚀 Method 1: Startup Folder (Easiest - Recommended)

### Steps:

1. **Press `Win + R`** → Type: `shell:startup` → Press Enter
   - This opens the Startup folder

2. **Create a shortcut:**
   - Right-click in the Startup folder → **New** → **Shortcut**

3. **Browse to:**
   ```
   C:\Users\YourName\Cursor\pharmacy_website\start_server_silent.vbs
   ```
   (Adjust path to your actual location)

4. **Click Next** → Name it "Pharmacy Server" → **Finish**

5. **Done!** ✅
   - Server will start automatically when Windows boots
   - No window will appear
   - Server runs in background

### To Stop Server:
- Run `stop_server.bat` from the pharmacy_website folder
- Or use Task Manager → End Python processes

---

## 🔧 Method 2: Task Scheduler (More Control)

### Steps:

1. **Press `Win + R`** → Type: `taskschd.msc` → Press Enter

2. **Click "Create Basic Task"** (right side)

3. **Name:** "Pharmacy Server"
   - Description: "Start Pharmacy Website Server"
   - Click **Next**

4. **Trigger:** "When the computer starts"
   - Click **Next**

5. **Action:** "Start a program"
   - Click **Next**

6. **Program/script:**
   ```
   pythonw.exe
   ```
   (Or full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python310\pythonw.exe`)

7. **Add arguments:**
   ```
   manage.py runserver 0.0.0.0:8000
   ```

8. **Start in:**
   ```
   C:\Users\YourName\Cursor\pharmacy_website
   ```
   (Your actual project path)

9. **Check:** "Open the Properties dialog"
   - Click **Finish**

10. **In Properties:**
    - Check **"Run whether user is logged on or not"**
    - Check **"Run with highest privileges"** (if needed)
    - Click **OK**

11. **Done!** ✅

---

## ⚙️ Method 3: Windows Service (Advanced - Most Reliable)

### Prerequisites:
1. Download **NSSM** (Non-Sucking Service Manager):
   - Go to: https://nssm.cc/download
   - Download the latest release
   - Extract `nssm.exe` to `pharmacy_website` folder

### Steps:

1. **Run as Administrator:**
   - Right-click `install_as_service.bat`
   - Select **"Run as administrator"**

2. **Follow the prompts**

3. **Service will be installed and started automatically**

### Service Commands:
```batch
# Start service
nssm start PharmacyServer

# Stop service
nssm stop PharmacyServer

# Restart service
nssm restart PharmacyServer

# Remove service
nssm remove PharmacyServer confirm
```

---

## 🎯 Quick Setup (Recommended):

### Fastest Method:

1. **Press `Win + R`** → `shell:startup`

2. **Copy `start_server_silent.vbs`** to Startup folder

3. **Done!** Server starts automatically on boot, no window!

---

## 🛑 How to Stop the Server:

### Option 1: Use the stop script
```batch
stop_server.bat
```

### Option 2: Task Manager
1. Press `Ctrl + Shift + Esc`
2. Find `pythonw.exe` or `python.exe`
3. Right-click → **End Task**

### Option 3: Command Line
```batch
taskkill /F /IM pythonw.exe
```

---

## ✅ Verify Server is Running:

1. **Open browser** on any computer
2. **Go to:** `http://SERVER-IP:8000`
3. **If it loads** → Server is running! ✅

---

## 🔍 Check Server Status:

### Method 1: Check if port is in use
```powershell
netstat -an | findstr :8000
```
If you see output, server is running.

### Method 2: Check Python processes
```powershell
tasklist | findstr python
```

---

## 📝 Notes:

- **pythonw.exe** = Python without window (silent)
- **python.exe** = Python with window (visible)
- Server runs in background - no window needed
- Can access from any computer on network
- Server starts automatically on Windows boot

---

## 🎉 That's It!

Your server will now:
- ✅ Start automatically when Windows boots
- ✅ Run in background (no window)
- ✅ Be accessible from all 5 client computers
- ✅ Keep running until you stop it

**No more confusion with open windows!** 🎊



