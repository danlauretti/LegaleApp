#!/usr/bin/env python3
"""
Simple HTTP Server to run the Restaurant Reviews Map application
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# Configuration
PORT = 8000
HOSTNAME = "localhost"
FILE_TO_OPEN = "restaurant_map.html"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow local file access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        # Custom logging
        print(f"[Server] {self.address_string()} - {format % args}")

def main():
    # Change to the script's directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    print("=" * 70)
    print("🍽️  Restaurant Reviews Map - Local Server")
    print("=" * 70)
    print(f"📁 Serving files from: {script_dir}")
    print(f"🌐 Server running at: http://{HOSTNAME}:{PORT}")
    print(f"📄 Opening: {FILE_TO_OPEN}")
    print("=" * 70)
    print("\n🚀 Starting server...")

    # Create server
    Handler = MyHTTPRequestHandler

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            url = f"http://{HOSTNAME}:{PORT}/{FILE_TO_OPEN}"

            print(f"✅ Server started successfully!")
            print(f"\n🔗 Open this URL in your browser:")
            print(f"   {url}")
            print(f"\n💡 Press Ctrl+C to stop the server")
            print("=" * 70)

            # Automatically open browser
            print("\n🌐 Opening browser...")
            try:
                webbrowser.open(url)
                print("✅ Browser opened!")
            except Exception as e:
                print(f"⚠️  Could not auto-open browser: {e}")
                print(f"   Please manually open: {url}")

            print("\n📊 Server logs:")
            print("-" * 70)

            # Start serving
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("🛑 Server stopped by user")
        print("=" * 70)
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {PORT} is already in use!")
            print(f"   Please close the other application or change the PORT variable")
            print(f"   You can also try: python3 run_restaurant_app.py --port 8080")
        else:
            print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
