# QR Printer System

A printer driver system that converts print requests into QR code PNG files, and a display server that shows the latest QR code for 10 seconds.

## Components

1. **Printer Service** (`printer_service.py`): Receives print requests and generates QR code PNG files with incrementing integer filenames
2. **Display Server** (`display_server.py`): Web server that displays the latest QR code for 10 seconds, then hides it

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Printer Service

Run the printer service on port 5000:
```bash
python printer_service.py
```

The service will:
- Listen for print requests on `http://localhost:5000/print`
- Save QR code PNG files in the `qr_codes/` directory
- Use incrementing integer filenames (1.png, 2.png, 3.png, etc.)

### Starting the Display Server

Run the display server on port 8080:
```bash
python display_server.py
```

Open your browser to `http://localhost:8080` to see the QR code display.

The display will:
- Automatically show the latest QR code when a new print job arrives
- Display each QR code for 10 seconds
- Hide the QR code after 10 seconds
- Auto-refresh to check for new QR codes

### Sending Print Requests

You can send print requests to the printer service using various methods:

#### Using curl:
```bash
curl -X POST http://localhost:5000/print \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, World!"}'
```

#### Using Python:
```python
import requests

response = requests.post('http://localhost:5000/print', 
                        json={'content': 'Your text here'})
print(response.json())
```

#### Using PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:5000/print -Method Post -ContentType "application/json" -Body '{"content":"Hello from PowerShell"}'
```

## How It Works

1. **Print Request**: Send data to `http://localhost:5000/print`
2. **QR Generation**: The printer service converts the content to a QR code
3. **File Saving**: Saves as `{number}.png` where number increments each time
4. **Display**: The display server automatically detects new QR codes and shows them for 10 seconds

## File Structure

```
QRPRINTER/
├── printer_service.py    # Printer service (port 5000)
├── display_server.py      # Display server (port 8080)
├── requirements.txt       # Python dependencies
├── qr_codes/             # Generated QR code PNG files
├── counter.txt           # Tracks the last file number
└── README.md            # This file
```

## API Endpoints

### Printer Service (port 5000)
- `POST /print` - Send print request (creates QR code)
- `GET /health` - Health check
- `GET /last_qr` - Get info about the last QR code

### Display Server (port 8080)
- `GET /` - Main display page
- `GET /api/latest` - Get latest QR code info (JSON)
- `GET /qr/<filename>` - Serve QR code image files

## Notes

- QR codes are saved in the `qr_codes/` directory
- The counter file (`counter.txt`) tracks the last used number
- The display server checks for new QR codes every 500ms
- Each QR code is displayed for exactly 10 seconds before disappearing

