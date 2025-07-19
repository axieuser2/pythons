#!/usr/bin/env python3
"""
Web Server for RAG File Processing
Handles file uploads and processing via HTTP API
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cgi
from universal_file_processor import process_files_from_directory, UniversalFileProcessor

class FileUploadHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_json_response({"status": "healthy", "message": "RAG File Processor is running"})
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/process-files':
            self.handle_file_upload()
        else:
            self.send_error(404, "Not Found")
    
    def handle_file_upload(self):
        """Handle file upload and processing"""
        try:
            # Parse the multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Expected multipart/form-data")
                return
            
            # Create temporary directory for uploaded files
            temp_dir = tempfile.mkdtemp(prefix="rag_upload_")
            
            try:
                # Parse form data
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': content_type,
                    }
                )
                
                files_saved = 0
                
                # Save uploaded files
                for field_name in form.keys():
                    if field_name.startswith('file_'):
                        file_item = form[field_name]
                        if file_item.filename:
                            # Save file to temporary directory
                            file_path = os.path.join(temp_dir, file_item.filename)
                            with open(file_path, 'wb') as f:
                                f.write(file_item.file.read())
                            files_saved += 1
                
                if files_saved == 0:
                    self.send_json_response({
                        "success": False,
                        "message": "No files were uploaded"
                    })
                    return
                
                # Process the uploaded files
                result = process_files_from_directory(temp_dir)
                self.send_json_response(result)
                
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            self.send_json_response({
                "success": False,
                "message": "Error processing files",
                "error": str(e)
            }, status_code=500)
    
    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log message format"""
        print(f"[{self.date_time_string()}] {format % args}")

def run_server(port: int = 8000):
    """Run the web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FileUploadHandler)
    
    print(f"🚀 RAG File Processor Server starting on port {port}")
    print(f"📁 Upload endpoint: http://localhost:{port}/process-files")
    print(f"❤️  Health check: http://localhost:{port}/health")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()