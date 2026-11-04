#!/usr/bin/env python3
"""Start the Rust Course on this computer.

Serves this folder at http://127.0.0.1:8766 and opens it in your browser.
Keep this window open while you study; close it (or press Ctrl+C) to stop.

The port stays the same every time on purpose: your browser keeps your
progress per address, so a different port would look like a fresh start.
"""
import http.server
import os
import sys
import threading
import webbrowser

PORT = 8766
HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".wasm": "application/wasm",
        ".js": "text/javascript",
        ".json": "application/json",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HERE, **kwargs)

    def log_message(self, *args):  # keep the window quiet
        pass


def main():
    url = f"http://127.0.0.1:{PORT}/"
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print(f"Port {PORT} is busy. The course may already be running: {url}")
        webbrowser.open(url)
        sys.exit(0)
    print(f"Rust Course is running at {url}")
    print("Leave this window open while you study. Press Ctrl+C to stop.")
    threading.Timer(0.8, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
