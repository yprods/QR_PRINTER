"""
Printer Service - Receives print requests and generates QR code PNG files
"""
import os
import json
from flask import Flask, request, jsonify
import qrcode
from PIL import Image
from datetime import datetime

app = Flask(__name__)

# Directory to store QR code images
QR_OUTPUT_DIR = "qr_codes"
# Directory to store print content
PRINT_CONTENT_DIR = "print_content"
# File to track the last used number
COUNTER_FILE = "counter.txt"

# Ensure output directories exist
os.makedirs(QR_OUTPUT_DIR, exist_ok=True)
os.makedirs(PRINT_CONTENT_DIR, exist_ok=True)


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
    
    # Increment and save
    number += 1
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(number))
    
    return number


def create_qr_code(data, filename):
    """Create a QR code PNG file from the given data - less dense, more readable"""
    # Create QR code instance with larger spacing for less density
    qr = qrcode.QRCode(
        version=None,  # Auto-detect version
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
        box_size=20,  # Larger boxes for less density (was 10)
        border=8,  # Larger border for better spacing (was 4)
    )
    
    # Add data to QR code
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create image from QR code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to file
    filepath = os.path.join(QR_OUTPUT_DIR, filename)
    img.save(filepath)
    
    return filepath


@app.route('/print', methods=['POST'])
def handle_print():
    """Handle print requests from computer/server"""
    try:
        # Get print data from request
        if request.is_json:
            data = request.get_json()
            # Extract text content
            print_content = data.get('content', '') or data.get('text', '') or json.dumps(data)
        else:
            # Get raw text data
            print_content = request.data.decode('utf-8') if request.data else request.form.get('content', '')
        
        if not print_content:
            return jsonify({'error': 'No print content provided'}), 400
        
        # Get next file number
        file_number = get_next_file_number()
        filename = f"{file_number}.png"
        content_filename = f"{file_number}.txt"
        
        # Save print content to text file
        content_filepath = os.path.join(PRINT_CONTENT_DIR, content_filename)
        with open(content_filepath, 'w', encoding='utf-8') as f:
            f.write(print_content)
        
        # Create QR code
        filepath = create_qr_code(print_content, filename)
        
        print(f"[{datetime.now()}] Print job received - Saved QR code as {filename}")
        
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


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'printer_service'}), 200


@app.route('/last_qr', methods=['GET'])
def get_last_qr():
    """Get the filename of the last generated QR code"""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r') as f:
                number = int(f.read().strip())
            filename = f"{number}.png"
            content_filename = f"{number}.txt"
            filepath = os.path.join(QR_OUTPUT_DIR, filename)
            content_filepath = os.path.join(PRINT_CONTENT_DIR, content_filename)
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


if __name__ == '__main__':
    print("=" * 50)
    print("QR Printer Service Starting...")
    print(f"QR codes will be saved to: {os.path.abspath(QR_OUTPUT_DIR)}")
    print("Listening for print requests on http://localhost:5000/print")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)

