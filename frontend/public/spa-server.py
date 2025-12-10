#!/usr/bin/env python3
"""
Simple HTTP server with SPA routing support
Falls back to index.html for all routes (like nginx try_files)
"""

import http.server
import socketserver
import os
from pathlib import Path

class SPAHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Get the path
        path = self.translate_path(self.path)
        
        # If it's a file that exists, serve it
        if os.path.isfile(path):
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # If it's a directory and has index.html, serve it
        if os.path.isdir(path):
            index_path = os.path.join(path, 'index.html')
            if os.path.exists(index_path):
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # Otherwise, fall back to root index.html (SPA routing)
        self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

PORT = 3000
Handler = SPAHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving SPA on port {PORT}")
    print(f"URL: http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()
