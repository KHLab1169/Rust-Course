#!/usr/bin/env python3
"""Start the Rust Course on this computer.

Serves this folder at http://127.0.0.1:8766 and opens it in your browser.
Keep this window open while you study; close it (or press Ctrl+C) to stop.

If Rust is installed (rustc on the PATH or in ~/.cargo/bin), the course can also
compile your answers and run the exercise tests here, through api/grade, and show
Clippy's style notes through api/style. Only the course page itself may call them.

The port stays the same every time on purpose: your browser keeps your
progress per address, so a different port would look like a fresh start.
"""
import http.server
import json
import os
import sys
import threading
import webbrowser

PORT = 8766
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rsgrade  # noqa: E402

ALLOWED_ORIGINS = {f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"}
GRADING = threading.Semaphore(2)  # at most two compilations at once
MAX_BODY = 512 * 1024


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

    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/rust":
            return self._json(200, rsgrade.status())
        return super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        if path not in ("/api/grade", "/api/style"):
            return self._json(404, {"error": "not found"})
        # Only the course page may ask this computer to compile code: other websites can't
        # send this Origin, and a JSON content type can't be sent cross-site without CORS.
        if self.headers.get("Origin") not in ALLOWED_ORIGINS or \
                not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self._json(403, {"error": "forbidden"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_BODY:
                return self._json(413, {"error": "too large"})
            req = json.loads(self.rfile.read(n) or b"{}")
            code, spec = req.get("code") or "", req.get("spec") or {}
            if not isinstance(code, str) or not isinstance(spec, dict) or not isinstance(spec.get("cases"), list):
                return self._json(400, {"error": "bad request"})
        except (ValueError, OSError):
            return self._json(400, {"error": "bad request"})
        with GRADING:
            if path == "/api/grade":
                return self._json(200, rsgrade.grade(code, spec))
            return self._json(200, {"notes": rsgrade.style_for(code, spec)})


def main():
    url = f"http://127.0.0.1:{PORT}/"
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print(f"Port {PORT} is busy. The course may already be running: {url}")
        webbrowser.open(url)
        sys.exit(0)
    st = rsgrade.status()
    print(f"Rust Course is running at {url}")
    print(f"Autograding: on ({st['version']})" if st.get("rust") else
          "Autograding: off (Rust isn't installed; see https://rustup.rs). Test in Playground still works.")
    print("Leave this window open while you study. Press Ctrl+C to stop.")
    threading.Timer(0.8, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
