# Quick Start Guide - Server Setup

## 🚀 Fast Setup (5 minutes)

### On Server Computer (Main PC):

1. **Find your IP address:**
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., `192.168.1.100`)

2. **Start the server:**
   - Double-click `start_server.bat`
   - OR run: `python manage.py runserver 0.0.0.0:8000`
   - Keep this window open!

3. **Configure Firewall** (if needed):
   ```powershell
   # Run PowerShell as Administrator
   New-NetFirewallRule -DisplayName "Django Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

### On Client Computers (Other 5 PCs):

1. **Open web browser**
2. **Type:** `http://YOUR-SERVER-IP:8000`
   - Example: `http://192.168.1.100:8000`
3. **Bookmark it!**

That's it! 🎉

---

## 📝 Notes:

- **Server must be running** for clients to access
- All computers must be on **same network** (same Wi-Fi/router)
- If IP changes, update the bookmark on client computers

---

## 🔧 Troubleshooting:

**Can't connect?**
- Check server is running
- Check firewall allows port 8000
- Verify IP address: `ipconfig` on server
- Test: `ping SERVER-IP` from client

**Need help?** See `DEPLOYMENT_GUIDE.md` for detailed instructions.


