# PowerShell script to install QR Printer in Windows
# Run this script as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QR Printer Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Get the current directory (where this script is located)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$printInputDir = Join-Path $scriptPath "print_input"

# Ensure print_input directory exists
if (-not (Test-Path $printInputDir)) {
    New-Item -ItemType Directory -Path $printInputDir -Force | Out-Null
    Write-Host "Created directory: $printInputDir" -ForegroundColor Green
}

# Printer name
$printerName = "QR Printer"

# Check if printer already exists
$existingPrinter = Get-Printer -Name $printerName -ErrorAction SilentlyContinue

if ($existingPrinter) {
    Write-Host "Printer '$printerName' already exists. Removing old printer..." -ForegroundColor Yellow
    Remove-Printer -Name $printerName -ErrorAction SilentlyContinue
}

# Add printer port (File port)
$portName = "FILE:"
$portPath = Join-Path $printInputDir "print_%Y%m%d_%H%M%S.txt"

Write-Host "Adding printer port..." -ForegroundColor Yellow
Add-PrinterPort -Name $portName -FileName $portPath -ErrorAction SilentlyContinue

# Add printer using Generic / Text Only driver
Write-Host "Installing printer '$printerName'..." -ForegroundColor Yellow

try {
    # Try to add printer with Generic Text driver
    Add-Printer -Name $printerName -PortName $portName -DriverName "Generic / Text Only" -ErrorAction Stop
    Write-Host "✓ Printer installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Attempting alternative installation method..." -ForegroundColor Yellow
    
    # Alternative: Use Microsoft Print To PDF driver as base, but redirect to file
    try {
        # Create a local port
        $localPort = Join-Path $printInputDir "print.txt"
        Add-PrinterPort -Name "FILE:" -FileName $localPort -ErrorAction SilentlyContinue
        
        # Try with Microsoft Print To PDF (more commonly available)
        $drivers = Get-PrinterDriver | Where-Object { $_.Name -like "*Text*" -or $_.Name -like "*Generic*" }
        if ($drivers) {
            $driverName = $drivers[0].Name
            Add-Printer -Name $printerName -PortName "FILE:" -DriverName $driverName -ErrorAction Stop
            Write-Host "✓ Printer installed successfully!" -ForegroundColor Green
        } else {
            throw "No suitable printer driver found"
        }
    } catch {
        Write-Host "ERROR: Could not install printer automatically." -ForegroundColor Red
        Write-Host ""
        Write-Host "Manual Installation Steps:" -ForegroundColor Yellow
        Write-Host "1. Open Settings > Devices > Printers & scanners" -ForegroundColor White
        Write-Host "2. Click 'Add a printer or scanner'" -ForegroundColor White
        Write-Host "3. Click 'The printer that I want isn't listed'" -ForegroundColor White
        Write-Host "4. Select 'Add a local printer or network printer with manual settings'" -ForegroundColor White
        Write-Host "5. Select 'Use an existing port' and choose 'FILE: (Print to File)'" -ForegroundColor White
        Write-Host "6. Select 'Generic / Text Only' as the driver" -ForegroundColor White
        Write-Host "7. Name it 'QR Printer'" -ForegroundColor White
        Write-Host "8. When printing, it will ask for a filename - use: $printInputDir\print.txt" -ForegroundColor White
        Write-Host ""
        pause
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Printer Name: $printerName" -ForegroundColor White
Write-Host "Print files will be saved to: $printInputDir" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Start the printer service: python printer_service.py" -ForegroundColor White
Write-Host "2. Start the file watcher: python print_file_watcher.py" -ForegroundColor White
Write-Host "3. Print from any application to '$printerName'" -ForegroundColor White
Write-Host ""
pause

