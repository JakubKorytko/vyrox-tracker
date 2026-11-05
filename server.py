"""Minimal static server + Toornament API proxy (CORS workaround)."""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8765


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/") or self.path.startswith("/media/"):
            self._proxy_api()
            return
        super().do_GET()

    def _proxy_api(self):
        url = "https://play.toornament.com" + self.path
        req = urllib.request.Request(
            url, headers={"User-Agent": "vyrox-tracker/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                ctype = resp.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as e:
            body = e.read()
            ctype = e.headers.get("Content-Type", "application/json")
            self.send_response(e.code)
            self.send_header("Content-Type", ctype)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        if self.path.startswith("/api/"):
            print(f"[api] {args[0]} {args[1]}")
        elif not self.path.endswith((".png", ".ico", ".woff2")):
            print(f"[web] {args[0]} {args[1]}")


if __name__ == "__main__":
    os.chdir(ROOT)
    print(f"vyrox tracker: http://127.0.0.1:{PORT}/")
    print("Ctrl+C to stop")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
