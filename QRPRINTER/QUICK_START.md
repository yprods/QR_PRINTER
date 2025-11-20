# Quick Start Guide - QR Printer Installation

## 🚀 Quick Installation Steps

### 1. Install Dependencies (Already Done!)
```bash
pip install -r requirements.txt
```
✅ All dependencies are now installed!

### 2. Install the Windows Printer

**Option A: Automated (PowerShell)**
1. Right-click `install_printer.ps1` → "Run with PowerShell"
2. Follow the prompts (may require Administrator rights)

**Option B: Manual Installation**
1. Double-click `install_printer_simple.bat`
2. Follow the on-screen instructions
3. When adding printer, use:
   - Port: **FILE: (Print to File)**
   - Driver: **Generic / Text Only**
   - Name: **QR Printer**
4. When printing, save to: `print_input\print.txt`

### 3. Start the System

**Easy Way:** Double-click `start_all.bat`

**Or start individually:**
1. `start_printer_service.bat` - Main printer service
2. `start_file_watcher.bat` - Monitors for print files
3. `start_display_server.bat` - Web display (optional)

### 4. Test It!

1. Open Notepad
2. Type some text
3. Press `Ctrl + P` (Print)
4. Select **"QR Printer"**
5. When asked for filename, use: `print_input\print.txt`
6. Watch the QR code appear on `http://localhost:8080`!

## 📋 What Each Component Does

- **printer_service.py** - Receives print requests, creates QR codes
- **print_file_watcher.py** - Watches for Windows print files, sends to service
- **display_server.py** - Shows QR codes on web page for 10 seconds

## 🔧 Troubleshooting

**Printer not working?**
- Make sure `print_file_watcher.py` is running
- Check that files are saved to `print_input\print.txt`
- Verify `printer_service.py` is running

**Need help?** See `INSTALL_PRINTER.md` for detailed instructions.

