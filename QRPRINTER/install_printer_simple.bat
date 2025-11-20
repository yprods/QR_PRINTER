@echo off
echo ========================================
echo QR Printer Simple Installation
echo ========================================
echo.
echo This will guide you through installing the QR Printer.
echo.
pause

echo.
echo Step 1: Opening Windows Printer Settings...
echo.
start ms-settings:printers

echo.
echo Please follow these steps:
echo.
echo 1. Click "Add a printer or scanner"
echo 2. Click "The printer that I want isn't listed"
echo 3. Select "Add a local printer or network printer with manual settings"
echo 4. Click Next
echo 5. Select "Use an existing port" and choose "FILE: (Print to File)"
echo 6. Click Next
echo 7. Select "Generic" manufacturer and "Generic / Text Only" printer
echo 8. Click Next
echo 9. Name the printer "QR Printer"
echo 10. Click Next, then Finish
echo.
echo IMPORTANT: When you print, Windows will ask for a filename.
echo Use this path: %CD%\print_input\print.txt
echo.
echo After installation, make sure to:
echo 1. Start printer_service.py
echo 2. Start print_file_watcher.py
echo.
pause

