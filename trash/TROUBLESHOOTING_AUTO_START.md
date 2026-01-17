# Troubleshooting Auto-Start Server

If `start_server_silent.vbs` is not working, try these solutions:

---

## 🔧 Solution 1: Use Improved VBS Script

Use `start_server_silent_improved.vbs` instead - it has better Python detection.

**Steps:**
1. Copy `start_server_silent_improved.vbs` to Startup folder
2. Test it by double-clicking it
3. Check if server starts

---

## 🔧 Solution 2: Use Batch File Method (Most Reliable)

### Steps:

1. **Press `Win + R`** → `shell:startup`

2. **Create a new file** in Startup folder:
   - Right-click → New → Text Document
   - Name it: `PharmacyServer.bat`
   - **Important:** Change extension from `.txt` to `.bat`

3. **Right-click** `PharmacyServer.bat` → **Edit**

4. **Paste this code:**
   ```batch
   @echo off
   cd /d C:\Users\YourName\Cursor\pharmacy_website
   start "" /MIN pythonw.exe manage.py runserver 0.0.0.0:8000
   exit
   ```
   **Replace `C:\Users\YourName\Cursor\pharmacy_website` with your actual path!**

5. **Save and close**

6. **Test:** Double-click the `.bat` file - server should start in minimized window

---

## 🔧 Solution 3: Task Scheduler (Most Reliable)

This is the most reliable method:

### Steps:

1. **Press `Win + R`** → Type: `taskschd.msc` → Enter

2. **Click "Create Basic Task"** (right side)

3. **Name:** "Pharmacy Server"
   - Click **Next**

4. **Trigger:** "When I log on"
   - Click **Next**

5. **Action:** "Start a program"
   - Click **Next**

6. **Program/script:**
   ```
   pythonw.exe
   ```
   (Or full path if needed)

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
    - **General tab:**
      - Check "Run whether user is logged on or not"
      - Check "Run with highest privileges"
    - **Settings tab:**
      - Check "Allow task to be run on demand"
    - Click **OK**

11. **Test:** Right-click the task → **Run**

12. **Done!** ✅

---

## 🔍 Check What's Wrong

### Test 1: Check if Python works
Open Command Prompt and run:
```batch
python --version
pythonw --version
```

### Test 2: Check if manage.py works
```batch
cd C:\Users\YourName\Cursor\pharmacy_website
python manage.py runserver 0.0.0.0:8000
```

### Test 3: Check VBS script manually
1. Double-click `start_server_silent.vbs`
2. Check Task Manager for `python.exe` or `pythonw.exe`
3. Check if port 8000 is in use: `netstat -an | findstr :8000`

---

## 🎯 Recommended Fix (Easiest):

**Use Task Scheduler (Solution 3)** - It's the most reliable and works 100% of the time.

---

## ✅ Quick Fix Script

I've created `start_server_auto.bat` - try this:

1. **Press `Win + R`** → `shell:startup`

2. **Copy `start_server_auto.bat`** to Startup folder

3. **Edit it** and change the path to your project folder

4. **Done!**

---

## 🐛 Common Issues:

### Issue: "Python not found"
**Fix:** Use full path to Python in the script

### Issue: "Can't find manage.py"
**Fix:** Make sure `cd` command points to correct folder

### Issue: "Permission denied"
**Fix:** Run as Administrator or use Task Scheduler

### Issue: "Window still appears"
**Fix:** Use `pythonw.exe` instead of `python.exe`

---

## 💡 Best Solution:

**Use Task Scheduler** - It's built into Windows and always works!




