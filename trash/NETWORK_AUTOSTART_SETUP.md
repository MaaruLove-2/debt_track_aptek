# Auto-Start Setup for Network Path

This guide explains how to set up auto-start for the Django server when the project is located on a network shared folder: `\\Desktop-1\новая папка\code\debt-track`

---

## 🚀 Method 1: Task Scheduler (Recommended - Most Reliable)

This is the **best method** for network paths because:
- ✅ Works even if network isn't ready at boot
- ✅ Can retry if network fails
- ✅ Runs with proper permissions
- ✅ Most reliable for UNC paths

### Quick Setup (Automated):

1. **Right-click** `setup_network_autostart.ps1` → **Run with PowerShell** (as Administrator)
   - Or open PowerShell as Administrator and run:
     ```powershell
     cd "\\Desktop-1\новая папка\code\debt-track"
     .\setup_network_autostart.ps1
     ```

2. **Follow the prompts** - the script will:
   - Check network path accessibility
   - Find Python executable
   - Create the scheduled task
   - Configure it to start on login

3. **Done!** ✅

### Manual Setup (If automated script doesn't work):

1. **Press `Win + R`** → Type: `taskschd.msc` → Press Enter

2. **Click "Create Basic Task"** (right side)

3. **Name:** "PharmacyDebtTracker"
   - Description: "Start Django Pharmacy Debt Tracker Server"
   - Click **Next**

4. **Trigger:** "When I log on"
   - Click **Next**

5. **Action:** "Start a program"
   - Click **Next**

6. **Program/script:**
   ```
   pythonw.exe
   ```
   (Or full path to Python if not in PATH)
   
   **For virtual environment, use:**
   ```
   \\Desktop-1\новая папка\code\debt-track\venv\Scripts\pythonw.exe
   ```

7. **Add arguments:**
   ```
   manage.py runserver 0.0.0.0:8000
   ```

8. **Start in:**
   ```
   \\Desktop-1\новая папка\code\debt-track
   ```

9. **Check:** "Open the Properties dialog"
   - Click **Finish**

10. **In Properties dialog:**
    - **General tab:**
      - ✅ Check **"Run whether user is logged on or not"** (if you want it to run before login)
      - ✅ Check **"Run with highest privileges"**
      - ✅ Select **"Run only when user is logged on"** (recommended for network paths)
    - **Conditions tab:**
      - ✅ Check **"Start the task only if the following network connection is available"**
      - Select **"Any connection"**
    - **Settings tab:**
      - ✅ Check **"Allow task to be run on demand"**
      - ✅ Check **"Run task as soon as possible after a scheduled start is missed"**
      - Set **"If the task fails, restart every:"** to 1 minute
      - Set **"Attempt to restart up to:"** to 3 times
    - Click **OK**

11. **Test the task:**
    - Right-click the task → **Run**
    - Check if server starts: Open browser to `http://127.0.0.1:8000`

12. **Done!** ✅

---

## 🔧 Method 2: Startup Folder (Simple but Less Reliable)

**Note:** This method may not work if the network isn't ready when Windows starts.

### Steps:

1. **Press `Win + R`** → Type: `shell:startup` → Press Enter
   - This opens your Startup folder

2. **Create a shortcut:**
   - Right-click in Startup folder → **New** → **Shortcut**

3. **Browse to the network path:**
   ```
   \\Desktop-1\новая папка\code\debt-track\start_server_network.vbs
   ```
   Or type the path directly

4. **Click Next** → Name it "Pharmacy Server" → **Finish**

5. **Right-click the shortcut** → **Properties**
   - Make sure the path is correct
   - Click **OK**

6. **Test:** Double-click the shortcut - server should start

7. **Done!** ✅

---

## 🔧 Method 3: Using Batch File in Startup

1. **Press `Win + R`** → `shell:startup`

2. **Create a new file** in Startup folder:**
   - Right-click → New → Text Document
   - Name it: `PharmacyServer.bat`
   - **Important:** Change extension from `.txt` to `.bat`

3. **Right-click** `PharmacyServer.bat` → **Edit**

4. **Paste this code:**
   ```batch
   @echo off
   REM Wait for network to be ready
   timeout /t 10 /nobreak >nul
   
   REM Network path
   set "NETWORK_PATH=\\Desktop-1\новая папка\code\debt-track"
   
   REM Change to network directory
   cd /d "%NETWORK_PATH%"
   
   REM Check if accessible
   if not exist "manage.py" (
       exit /b 1
   )
   
   REM Start server
   if exist "venv\Scripts\pythonw.exe" (
       start "" /MIN venv\Scripts\pythonw.exe manage.py runserver 0.0.0.0:8000
   ) else (
       start "" /MIN pythonw.exe manage.py runserver 0.0.0.0:8000
   )
   
   exit
   ```

5. **Save and close**

6. **Test:** Double-click the `.bat` file

7. **Done!** ✅

---

## 🛠️ Troubleshooting

### Problem: Task doesn't start at login

**Solutions:**
1. Check Task Scheduler → Task Scheduler Library → Find your task
2. Check "Last Run Result" - if it shows an error code, check what it means
3. Make sure network path is accessible before login
4. Try changing trigger to "When computer starts" instead of "When I log on"

### Problem: "Network path not accessible"

**Solutions:**
1. Make sure Desktop-1 computer is on and network share is accessible
2. Map the network drive to a drive letter (e.g., Z:), then use that in the task
3. Add a delay in the task (use a batch file that waits before starting)
4. Check Windows Firewall settings
5. Verify you have permissions to access the network share

### Problem: "Python not found"

**Solutions:**
1. Use full path to Python in Task Scheduler
2. For virtual environment, use: `\\Desktop-1\новая папка\code\debt-track\venv\Scripts\pythonw.exe`
3. Add Python to system PATH

### Problem: Server starts but stops immediately

**Solutions:**
1. Check `server_log.txt` in the project folder for errors
2. Make sure Django dependencies are installed
3. Check if port 8000 is already in use
4. Run the server manually to see error messages:
   ```batch
   cd "\\Desktop-1\новая папка\code\debt-track"
   python manage.py runserver 0.0.0.0:8000
   ```

### Problem: Task runs but server doesn't respond

**Solutions:**
1. Check if server is actually running: `netstat -an | findstr :8000`
2. Check Windows Firewall - allow port 8000
3. Make sure server is binding to `0.0.0.0:8000` (not just `127.0.0.1:8000`)

---

## ✅ Verify Server is Running

### Method 1: Check Task Manager
1. Press `Ctrl + Shift + Esc`
2. Look for `python.exe` or `pythonw.exe` process
3. If found, server is running

### Method 2: Check Port
```powershell
netstat -an | findstr :8000
```
If you see `LISTENING`, server is running.

### Method 3: Open Browser
Open: `http://127.0.0.1:8000` or `http://YOUR-SERVER-IP:8000`

---

## 🛑 How to Stop the Server

### Option 1: Task Manager
1. Press `Ctrl + Shift + Esc`
2. Find `python.exe` or `pythonw.exe`
3. Right-click → **End Task**

### Option 2: Command Line
```batch
taskkill /F /IM pythonw.exe
taskkill /F /IM python.exe
```

### Option 3: Stop Task Scheduler Task
1. Open Task Scheduler
2. Find "PharmacyDebtTracker"
3. Right-click → **End**

---

## 📝 Important Notes

1. **Network Availability:** The network share must be accessible when the task runs. If the network isn't ready at boot, the task may fail. Use Task Scheduler with retry settings.

2. **Permissions:** Make sure the user account has:
   - Read/write access to the network share
   - Permission to run Python
   - Permission to bind to port 8000

3. **Firewall:** Windows Firewall may block the server. Allow port 8000 in firewall settings.

4. **Virtual Environment:** If using a virtual environment, make sure the path to `venv\Scripts\pythonw.exe` is correct in the task.

5. **Logging:** Check `server_log.txt` in the project folder for startup logs and errors.

---

## 🎉 That's It!

Your server will now:
- ✅ Start automatically when you log on (or when computer starts)
- ✅ Run in background (no window)
- ✅ Be accessible from all computers on the network
- ✅ Retry if network isn't ready
- ✅ Keep running until you stop it

**No more manual server startup!** 🎊







