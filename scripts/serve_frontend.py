#!/usr/bin/env python3
"""
Simple HTTP server for AutoAgentHire frontend
Serves the autoagenthire/index.html with proper CORS
"""

import http.server
import socketserver
from pathlib import Path
import os

PORT = 8080
DIRECTORY = "frontend/autoagenthire"

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with CORS support"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def main():
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"\n🚀 Starting AutoAgentHire Frontend Server")
    print(f"📂 Serving from: {DIRECTORY}")
    print(f"🌐 URL: http://localhost:{PORT}")
    print(f"📄 Dashboard: http://localhost:{PORT}/index.html")
    print(f"\n✨ Backend API: http://localhost:8000")
    print(f"\n🎯 Open the dashboard and enter your LinkedIn credentials!\n")
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")
            return

if __name__ == "__main__":
    main()
