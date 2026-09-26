#!/usr/bin/env python3
"""
Local development server for film-tvs static site.
Usage:
    python bin/serve.py [port]

Default port: 8080
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from functools import partial


class SilentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with cleaner log output."""

    def log_message(self, format, *args):
        print(f"  {self.address_string()} - {format % args}")

    def end_headers(self):
        # Disable caching for local development
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

    # Serve from the project root (one level up from bin/)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    handler = partial(SilentHTTPRequestHandler, directory=root_dir)

    url = f"http://localhost:{port}"
    print(f"Serving '{root_dir}'")
    print(f"Local: {url}")
    print("Press Ctrl+C to stop.\n")

    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.allow_reuse_address = True
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
