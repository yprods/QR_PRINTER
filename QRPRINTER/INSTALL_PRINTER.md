# How to Install the QR Printer

This guide will help you set up the QR Printer so that Windows can send print jobs to it.

## Method 1: Automated Installation (Recommended)

### Step 1: Install Additional Dependencies

```bash
pip install -r requirements.txt
```

This will install the `watchdog` library needed for the file watcher.

### Step 2: Run the Installation Script

**Option A: PowerShell Script (Automated)**
1. Right-click on `install_printer.ps1`
2. Select "Run with PowerShell"
3. If prompted, allow the script to run
4. The script will automatically install the printer

**Option B: Simple Batch File (Manual Guide)**
1. Double-click `install_printer_simple.bat`
2. Follow the on-screen instructions to manually add the printer

## Method 2: Manual Installation

### Step 1: Open Windows Printer Settings

1. Press `Windows + I` to open Settings
2. Go to **Devices** > **Printers & scanners**
3. Click **"Add a printer or scanner"**
4. Click **"The printer that I want isn't listed"**

### Step 2: Configure the Printer

1. Select **"Add a local printer or network printer with manual settings"**
2. Click **Next**
3. Select **"Use an existing port"**
4. Choose **"FILE: (Print to File)"** from the dropdown
5. Click **Next**

### Step 3: Install Driver

1. Select **"Generic"** as the manufacturer
2. Select **"Generic / Text Only"** as the printer
3. Click **Next**
4. Name the printer **"QR Printer"**
5. Click **Next**, then **Finish**

### Step 4: Configure Print Output Location

When you print to this printer, Windows will ask for a filename. Use this path:

```
C:\Users\yprod\OneDrive\Desktop\QRPRINTER\print_input\print.txt
```

**Tip:** You can create a shortcut or bookmark this path for easy access.

## Starting the System

After installing the printer, you need to start three components:

### 1. Start the Printer Service
```bash
python printer_service.py
```
Or double-click `start_printer_service.bat`

### 2. Start the File Watcher
```bash
python print_file_watcher.py
```
This monitors the `print_input` folder for new print files.

### 3. Start the Display Server (Optional)
```bash
python display_server.py
```
Or double-click `start_display_server.bat`

Or use `start_all.bat` to start everything at once!

## How to Use

1. **Make sure all services are running:**
   - Printer Service (port 5000)
   - File Watcher (monitoring print_input folder)
   - Display Server (port 8080) - optional

2. **Print from any application:**
   - Open any application (Notepad, Word, Browser, etc.)
   - Press `Ctrl + P` or go to File > Print
   - Select **"QR Printer"** from the printer list
   - Click Print
   - When prompted for filename, use: `print_input\print.txt`

3. **The system will:**
   - Detect the print file
   - Send it to the printer service
   - Generate a QR code PNG file
   - Display it on the web interface (if display server is running)

## Troubleshooting

### Printer doesn't appear in the list
- Make sure you completed the installation steps
- Try restarting your computer
- Check Windows Settings > Printers & scanners

### Print files aren't being processed
- Make sure `print_file_watcher.py` is running
- Check that the file is saved to `print_input\print.txt`
- Verify `printer_service.py` is running on port 5000

### "Could not connect to printer service" error
- Make sure `printer_service.py` is running
- Check that it's listening on port 5000
- Try restarting the printer service

### File watcher not detecting files
- Make sure files are saved to the `print_input` folder
- Check that the filename is exactly `print.txt` (or the watcher will process any new file)
- Restart the file watcher

## Alternative: Direct HTTP Printing

If you don't want to use Windows printer, you can send print jobs directly via HTTP:

```bash
python test_print.py "Your text here"
```

Or use PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:5000/print -Method Post -ContentType "application/json" -Body '{"content":"Hello World"}'
```

## File Structure

```
QRPRINTER/
├── printer_service.py       # Main printer service (port 5000)
├── print_file_watcher.py    # Monitors print_input folder
├── display_server.py        # Web display server (port 8080)
├── print_input/            # Where Windows saves print files
├── print_archive/          # Processed print files (archived)
├── qr_codes/               # Generated QR code PNG files
└── counter.txt             # Tracks last QR code number
```

