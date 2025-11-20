"""
QR Printer System - All-in-one solution
Combines printer service, display server, and file watcher
"""
import os
import json
import time
import threading
import requests
from flask import Flask, request, jsonify, send_file
from datetime import datetime
import qrcode
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ============================================================================
# CONFIGURATION
# ============================================================================
QR_OUTPUT_DIR = "qr_codes"
PRINT_CONTENT_DIR = "print_content"
PRINT_INPUT_DIR = "print_input"
PRINT_ARCHIVE_DIR = "print_archive"
COUNTER_FILE = "counter.txt"

PRINTER_SERVICE_PORT = 5000
DISPLAY_SERVER_PORT = 8080

# Ensure directories exist
os.makedirs(QR_OUTPUT_DIR, exist_ok=True)
os.makedirs(PRINT_CONTENT_DIR, exist_ok=True)
os.makedirs(PRINT_INPUT_DIR, exist_ok=True)
os.makedirs(PRINT_ARCHIVE_DIR, exist_ok=True)

# ============================================================================
# PRINTER SERVICE (Flask App on port 5000)
# ============================================================================
printer_app = Flask(__name__)
printer_app.config['JSON_AS_ASCII'] = False


def get_next_file_number():
    """Get the next incrementing file number"""
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, 'r') as f:
                number = int(f.read().strip())
        except (ValueError, IOError):
            number = 0
    else:
        number = 0
    
    number += 1
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(number))
    
    return number


def create_qr_code(data, filename):
    """Create a QR code PNG file - less dense, more readable"""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=20,  # Larger boxes for less density
        border=8,  # Larger border for better spacing
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    filepath = os.path.join(QR_OUTPUT_DIR, filename)
    img.save(filepath)
    
    return filepath


@printer_app.route('/print', methods=['POST'])
def handle_print():
    """Handle print requests from computer/server"""
    try:
        if request.is_json:
            data = request.get_json()
            print_content = data.get('content', '') or data.get('text', '') or json.dumps(data)
        else:
            print_content = request.data.decode('utf-8') if request.data else request.form.get('content', '')
        
        if not print_content:
            return jsonify({'error': 'No print content provided'}), 400
        
        file_number = get_next_file_number()
        filename = f"{file_number}.png"
        content_filename = f"{file_number}.txt"
        
        # Save print content
        content_filepath = os.path.join(PRINT_CONTENT_DIR, content_filename)
        with open(content_filepath, 'w', encoding='utf-8') as f:
            f.write(print_content)
        
        # Create QR code
        filepath = create_qr_code(print_content, filename)
        
        print(f"[{datetime.now()}] Print job #{file_number} - QR saved as {filename}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content_filename': content_filename,
            'file_number': file_number,
            'filepath': filepath
        }), 200
        
    except Exception as e:
        print(f"Error processing print job: {str(e)}")
        return jsonify({'error': str(e)}), 500


@printer_app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'printer_service'}), 200


@printer_app.route('/last_qr', methods=['GET'])
def get_last_qr():
    """Get the filename of the last generated QR code"""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r') as f:
                number = int(f.read().strip())
            filename = f"{number}.png"
            content_filename = f"{number}.txt"
            filepath = os.path.join(QR_OUTPUT_DIR, filename)
            if os.path.exists(filepath):
                return jsonify({
                    'filename': filename,
                    'content_filename': content_filename,
                    'file_number': number,
                    'exists': True
                }), 200
        return jsonify({'exists': False}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@printer_app.route('/print_content/<filename>', methods=['GET'])
def get_print_content(filename):
    """Get the print content text file"""
    try:
        filepath = os.path.join(PRINT_CONTENT_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'content': content,
                'filename': filename
            }), 200
        return jsonify({'error': 'Content file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_printer_service():
    """Run the printer service on port 5000"""
    print("=" * 60)
    print("QR Printer Service Starting...")
    print(f"QR codes will be saved to: {os.path.abspath(QR_OUTPUT_DIR)}")
    print(f"Listening on http://localhost:{PRINTER_SERVICE_PORT}/print")
    print("=" * 60)
    printer_app.run(host='0.0.0.0', port=PRINTER_SERVICE_PORT, debug=False, use_reloader=False)


# ============================================================================
# DISPLAY SERVER (Flask App on port 8080)
# ============================================================================
display_app = Flask(__name__)
display_app.config['JSON_AS_ASCII'] = False


def get_latest_qr_filename():
    """Get the filename of the latest QR code"""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r') as f:
                number = int(f.read().strip())
            filename = f"{number}.png"
            content_filename = f"{number}.txt"
            filepath = os.path.join(QR_OUTPUT_DIR, filename)
            content_filepath = os.path.join(PRINT_CONTENT_DIR, content_filename)
            if os.path.exists(filepath):
                return filename, filepath, content_filename, content_filepath
    except Exception as e:
        print(f"Error getting latest QR: {e}")
    return None, None, None, None


@display_app.route('/')
def index():
    """Main page that displays the print content"""
    html = """
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>תצוגת הדפסה - Print Display</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif, 'Arial Hebrew', 'David';
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                overflow: auto;
                padding: 20px;
            }
            
            .container {
                text-align: center;
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 95vw;
                width: 100%;
                max-width: 1200px;
                transition: opacity 0.5s ease-in-out, transform 0.5s ease-in-out;
            }
            
            .container.hidden {
                opacity: 0;
                transform: scale(0.8);
                pointer-events: none;
            }
            
            h1 {
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            
            .print-content {
                background: #f8f9fa;
                border: 2px solid #667eea;
                border-radius: 10px;
                padding: 40px;
                margin: 30px 0;
                text-align: right;
                font-size: 1.5em;
                line-height: 1.8;
                white-space: pre-wrap;
                word-wrap: break-word;
                min-height: 200px;
                color: #333;
                font-family: 'Courier New', monospace, 'Arial Hebrew', 'David';
                box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.1);
            }
            
            .qr-container {
                margin: 30px 0;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .qr-container img {
                max-width: 400px;
                width: 100%;
                height: auto;
                border: 5px solid #667eea;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            }
            
            .status {
                margin-top: 20px;
                color: #666;
                font-size: 1.2em;
            }
            
            .countdown {
                margin-top: 15px;
                font-size: 1.5em;
                color: #667eea;
                font-weight: bold;
            }
            
            .no-print {
                color: #999;
                font-size: 1.5em;
                padding: 40px;
            }
            
            .header-info {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            
            .print-number {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                font-size: 1.2em;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container" id="container">
            <div class="header-info">
                <h1>📄 תצוגת הדפסה</h1>
                <div class="print-number" id="print-number"></div>
            </div>
            <div id="print-display" class="print-content">
                <div class="no-print">ממתין להדפסה... Waiting for print job...</div>
            </div>
            <div class="qr-container" id="qr-container" style="display: none;">
                <img id="qr-image" src="" alt="QR Code">
            </div>
            <div class="status" id="status"></div>
            <div class="countdown" id="countdown"></div>
        </div>
        
        <script>
            let countdownTimer = null;
            let displayTimer = null;
            let currentPrintNumber = null;
            
            function updateDisplay() {
                fetch('/api/latest')
                    .then(response => response.json())
                    .then(data => {
                        const container = document.getElementById('container');
                        const printDisplay = document.getElementById('print-display');
                        const qrContainer = document.getElementById('qr-container');
                        const qrImage = document.getElementById('qr-image');
                        const printNumber = document.getElementById('print-number');
                        const status = document.getElementById('status');
                        const countdown = document.getElementById('countdown');
                        
                        if (data.exists && data.filename && data.content_filename) {
                            if (currentPrintNumber !== data.file_number) {
                                currentPrintNumber = data.file_number;
                                
                                fetch(`/print_content/${data.content_filename}`)
                                    .then(response => response.json())
                                    .then(contentData => {
                                        printDisplay.textContent = contentData.content;
                                        printDisplay.style.display = 'block';
                                        
                                        qrImage.src = `/qr/${data.filename}?t=${Date.now()}`;
                                        qrContainer.style.display = 'flex';
                                        
                                        printNumber.textContent = `הדפסה #${data.file_number}`;
                                        status.textContent = `Print Job #${data.file_number}`;
                                        
                                        container.classList.remove('hidden');
                                        
                                        if (countdownTimer) clearInterval(countdownTimer);
                                        if (displayTimer) clearTimeout(displayTimer);
                                        
                                        let seconds = 10;
                                        countdown.textContent = `מוצג למשך ${seconds} שניות... Displaying for ${seconds} seconds...`;
                                        
                                        countdownTimer = setInterval(() => {
                                            seconds--;
                                            if (seconds > 0) {
                                                countdown.textContent = `מוצג למשך ${seconds} שניות... Displaying for ${seconds} seconds...`;
                                            } else {
                                                countdown.textContent = '';
                                                clearInterval(countdownTimer);
                                            }
                                        }, 1000);
                                        
                                        displayTimer = setTimeout(() => {
                                            container.classList.add('hidden');
                                            status.textContent = 'הדפסה הוסתרה. ממתין להדפסה הבאה... Print hidden. Waiting for next print job...';
                                            countdown.textContent = '';
                                        }, 10000);
                                    })
                                    .catch(error => {
                                        console.error('Error fetching print content:', error);
                                    });
                            }
                        } else {
                            if (!currentPrintNumber) {
                                printDisplay.innerHTML = '<div class="no-print">אין הדפסה זמינה. ממתין להדפסה...<br>No print available yet. Waiting for print job...</div>';
                                qrContainer.style.display = 'none';
                                printNumber.textContent = '';
                                status.textContent = '';
                                countdown.textContent = '';
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching print data:', error);
                    });
            }
            
            setInterval(updateDisplay, 500);
            updateDisplay();
        </script>
    </body>
    </html>
    """
    return html


@display_app.route('/api/latest', methods=['GET'])
def api_latest():
    """API endpoint to get latest QR code info"""
    filename, filepath, content_filename, content_filepath = get_latest_qr_filename()
    if filename and filepath:
        try:
            number = int(filename.replace('.png', ''))
            return jsonify({
                'exists': True,
                'filename': filename,
                'content_filename': content_filename,
                'file_number': number
            }), 200
        except:
            pass
    return jsonify({'exists': False}), 200


@display_app.route('/print_content/<filename>', methods=['GET'])
def display_get_print_content(filename):
    """Get the print content text file"""
    try:
        filepath = os.path.join(PRINT_CONTENT_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'content': content,
                'filename': filename
            }), 200
        return jsonify({'error': 'Content file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@display_app.route('/qr/<filename>', methods=['GET'])
def serve_qr(filename):
    """Serve QR code image files"""
    filepath = os.path.join(QR_OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png')
    return jsonify({'error': 'QR code not found'}), 404


def run_display_server():
    """Run the display server on port 8080"""
    print("=" * 60)
    print("QR Display Server Starting...")
    print(f"Display server running on http://localhost:{DISPLAY_SERVER_PORT}")
    print("QR codes will be shown for 10 seconds then disappear")
    print("=" * 60)
    display_app.run(host='0.0.0.0', port=DISPLAY_SERVER_PORT, debug=False, use_reloader=False)


# ============================================================================
# FILE WATCHER (Monitors print_input directory)
# ============================================================================
class PrintFileHandler(FileSystemEventHandler):
    """Handle new print files"""
    
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(0.5)  # Wait for file to be fully written
            self.process_file(event.src_path)
    
    def process_file(self, filepath):
        """Process a print file and send to printer service"""
        try:
            filename = os.path.basename(filepath)
            print(f"[{datetime.now()}] Processing print file: {filename}")
            
            # Read file content
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                print(f"  Warning: File is empty, skipping...")
                return
            
            # Send to printer service
            try:
                response = requests.post(
                    f"http://localhost:{PRINTER_SERVICE_PORT}/print",
                    json={'content': content},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✓ QR code created: {result['filename']}")
                    
                    # Move file to archive
                    archive_path = os.path.join(PRINT_ARCHIVE_DIR, filename)
                    if os.path.exists(filepath):
                        os.rename(filepath, archive_path)
                        print(f"  ✓ File archived to: {archive_path}")
                else:
                    print(f"  ✗ Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print(f"  ✗ Error: Could not connect to printer service")
                print(f"    Waiting for service to start...")
            except Exception as e:
                print(f"  ✗ Error sending to printer service: {str(e)}")
                
        except Exception as e:
            print(f"  ✗ Error processing file: {str(e)}")


def run_file_watcher():
    """Start watching the print input directory"""
    # Wait a bit for printer service to start
    time.sleep(2)
    
    event_handler = PrintFileHandler()
    observer = Observer()
    observer.schedule(event_handler, PRINT_INPUT_DIR, recursive=False)
    observer.start()
    
    print("=" * 60)
    print("Print File Watcher Started")
    print(f"Watching directory: {os.path.abspath(PRINT_INPUT_DIR)}")
    print(f"Sending to: http://localhost:{PRINTER_SERVICE_PORT}/print")
    print("=" * 60)
    print("\nWaiting for print files...\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\nStopping file watcher...")
    
    observer.join()
    print("File watcher stopped.")


# ============================================================================
# MAIN - Start all services
# ============================================================================
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("QR PRINTER SYSTEM - Starting All Services")
    print("=" * 60)
    print("\nStarting services in separate threads...")
    print(f"- Printer Service: http://localhost:{PRINTER_SERVICE_PORT}")
    print(f"- Display Server: http://localhost:{DISPLAY_SERVER_PORT}")
    print(f"- File Watcher: Monitoring {PRINT_INPUT_DIR}")
    print("\nPress Ctrl+C to stop all services\n")
    print("=" * 60 + "\n")
    
    # Start printer service in a thread
    printer_thread = threading.Thread(target=run_printer_service, daemon=True)
    printer_thread.start()
    
    # Wait a moment for printer service to start
    time.sleep(1)
    
    # Start display server in a thread
    display_thread = threading.Thread(target=run_display_server, daemon=True)
    display_thread.start()
    
    # Wait a moment for display server to start
    time.sleep(1)
    
    # Start file watcher in a thread
    watcher_thread = threading.Thread(target=run_file_watcher, daemon=True)
    watcher_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("Stopping all services...")
        print("=" * 60)
        print("\nAll services stopped. Goodbye!")

