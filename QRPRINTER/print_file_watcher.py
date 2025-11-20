"""
Print File Watcher - Monitors a directory for print files and sends them to the printer service
"""
import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Configuration
PRINT_INPUT_DIR = "print_input"
PRINT_ARCHIVE_DIR = "print_archive"
PRINTER_SERVICE_URL = "http://localhost:5000/print"

# Ensure directories exist
os.makedirs(PRINT_INPUT_DIR, exist_ok=True)
os.makedirs(PRINT_ARCHIVE_DIR, exist_ok=True)


class PrintFileHandler(FileSystemEventHandler):
    """Handle new print files"""
    
    def on_created(self, event):
        if not event.is_directory:
            # Wait a moment for file to be fully written
            time.sleep(0.5)
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
                    PRINTER_SERVICE_URL,
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
                print(f"  ✗ Error: Could not connect to printer service at {PRINTER_SERVICE_URL}")
                print(f"    Make sure printer_service.py is running!")
            except Exception as e:
                print(f"  ✗ Error sending to printer service: {str(e)}")
                
        except Exception as e:
            print(f"  ✗ Error processing file: {str(e)}")


def start_watcher():
    """Start watching the print input directory"""
    event_handler = PrintFileHandler()
    observer = Observer()
    observer.schedule(event_handler, PRINT_INPUT_DIR, recursive=False)
    observer.start()
    
    print("=" * 60)
    print("Print File Watcher Started")
    print(f"Watching directory: {os.path.abspath(PRINT_INPUT_DIR)}")
    print(f"Sending to: {PRINTER_SERVICE_URL}")
    print("=" * 60)
    print("\nWaiting for print files... (Press Ctrl+C to stop)\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\nStopping file watcher...")
    
    observer.join()
    print("File watcher stopped.")


if __name__ == '__main__':
    start_watcher()

