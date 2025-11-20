@echo off
echo Starting QR Printer System...
echo.
echo Starting Printer Service in new window...
start "QR Printer Service" cmd /k "python printer_service.py"
timeout /t 2 /nobreak >nul
echo.
echo Starting File Watcher in new window...
start "QR File Watcher" cmd /k "python print_file_watcher.py"
timeout /t 2 /nobreak >nul
echo.
echo Starting Display Server in new window...
start "QR Display Server" cmd /k "python display_server.py"
timeout /t 2 /nobreak >nul
echo.
echo All services are starting...
echo - Printer Service: http://localhost:5000
echo - File Watcher: Monitoring print_input folder
echo - Display Server: http://localhost:8080
echo.
echo Press any key to exit this window (services will continue running)...
pause >nul

