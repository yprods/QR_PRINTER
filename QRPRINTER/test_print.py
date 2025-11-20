"""
Test script to send print requests to the printer service
"""
import requests
import time
import sys

def send_print_request(content):
    """Send a print request to the printer service"""
    try:
        response = requests.post(
            'http://localhost:5000/print',
            json={'content': content},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Print job successful!")
            print(f"  QR Code saved as: {data['filename']}")
            print(f"  File number: {data['file_number']}")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to printer service.")
        print("  Make sure printer_service.py is running on port 5000")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Use command line argument as content
        content = ' '.join(sys.argv[1:])
    else:
        # Default test content
        content = f"Test print job at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"Sending print request: {content}")
    send_print_request(content)

