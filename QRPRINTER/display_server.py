"""
Display Server - Shows the latest QR code for 10 seconds then disappears
"""
import os
import time
from flask import Flask, send_file, jsonify
from datetime import datetime

app = Flask(__name__)

QR_OUTPUT_DIR = "qr_codes"
PRINT_CONTENT_DIR = "print_content"
COUNTER_FILE = "counter.txt"


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


@app.route('/')
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
                            // New print detected
                            if (currentPrintNumber !== data.file_number) {
                                currentPrintNumber = data.file_number;
                                
                                // Fetch and display print content
                                fetch(`/print_content/${data.content_filename}`)
                                    .then(response => response.json())
                                    .then(contentData => {
                                        // Display the print content
                                        printDisplay.textContent = contentData.content;
                                        printDisplay.style.display = 'block';
                                        
                                        // Show QR code
                                        qrImage.src = `/qr/${data.filename}?t=${Date.now()}`;
                                        qrContainer.style.display = 'flex';
                                        
                                        // Update header
                                        printNumber.textContent = `הדפסה #${data.file_number}`;
                                        status.textContent = `Print Job #${data.file_number}`;
                                        
                                        container.classList.remove('hidden');
                                        
                                        // Clear any existing timers
                                        if (countdownTimer) clearInterval(countdownTimer);
                                        if (displayTimer) clearTimeout(displayTimer);
                                        
                                        // Start countdown
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
                                        
                                        // Hide after 10 seconds
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
                            // No print available
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
            
            // Check for updates every 500ms
            setInterval(updateDisplay, 500);
            
            // Initial load
            updateDisplay();
        </script>
    </body>
    </html>
    """
    return html


@app.route('/api/latest', methods=['GET'])
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


@app.route('/print_content/<filename>', methods=['GET'])
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


@app.route('/qr/<filename>', methods=['GET'])
def serve_qr(filename):
    """Serve QR code image files"""
    filepath = os.path.join(QR_OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png')
    return jsonify({'error': 'QR code not found'}), 404


if __name__ == '__main__':
    print("=" * 50)
    print("QR Display Server Starting...")
    print("Display server running on http://localhost:8080")
    print("QR codes will be shown for 10 seconds then disappear")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8080, debug=True)

