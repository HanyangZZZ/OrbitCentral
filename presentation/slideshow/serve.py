#!/usr/bin/env python3
"""
Tiny dev server that serves the slideshow AND proxies /api/ to the CLOUD backend.
This avoids CORS issues when the presentation calls the live API.

⚠️  ALWAYS uses the CLOUD API (business.orbitcentral.ca) — NOT local Docker.
    All data lives in the cloud Supabase/GCE database.
    To override: API_BACKEND=https://localhost API_HOST=orbitcentral.ca python3 serve.py

Usage:  python3 serve.py          (serves on 0.0.0.0:8090)
        python3 serve.py 9000     (custom port)
"""
import http.server
import urllib.request
import ssl
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
# ── CLOUD API (default) ──────────────────────────────────────────────────────
# Points to the production cloud server. Do NOT change to localhost.
API_BACKEND = os.environ.get('API_BACKEND', 'https://business.orbitcentral.ca')
API_HOST = os.environ.get('API_HOST', 'business.orbitcentral.ca')
ROOT = os.path.dirname(os.path.abspath(__file__))

# SSL context (permissive for self-signed certs if overridden to localhost)
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_request(self, method):
        if self.path.startswith('/api/'):
            self._proxy(method)
        else:
            if method == 'GET':
                super().do_GET()
            elif method == 'HEAD':
                super().do_HEAD()

    def do_GET(self):
        self.do_request('GET')

    def do_HEAD(self):
        self.do_request('HEAD')

    def do_POST(self):
        self._proxy('POST')

    def do_PUT(self):
        self._proxy('PUT')

    def do_PATCH(self):
        self._proxy('PATCH')

    def do_DELETE(self):
        self._proxy('DELETE')

    def do_OPTIONS(self):
        if self.path.startswith('/api/'):
            self._proxy('OPTIONS')
        else:
            self.send_response(200)
            self.end_headers()

    def _proxy(self, method):
        url = API_BACKEND + self.path
        # Read body for POST/PUT/PATCH
        body = None
        content_length = self.headers.get('Content-Length')
        if content_length:
            body = self.rfile.read(int(content_length))

        # Forward relevant headers + add Host for nginx routing
        headers = {'Host': API_HOST}
        for key in ('Content-Type', 'Authorization', 'Accept'):
            val = self.headers.get(key)
            if val:
                headers[key] = val

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30, context=_ssl_ctx) as resp:
                status = resp.status
                resp_headers = resp.headers
                resp_body = resp.read()
        except urllib.error.HTTPError as e:
            status = e.code
            resp_headers = e.headers
            resp_body = e.read()
        except Exception as e:
            self.send_error(502, f'Proxy error: {e}')
            return

        self.send_response(status)
        for key in ('Content-Type', 'Content-Length'):
            val = resp_headers.get(key)
            if val:
                self.send_header(key, val)
        self.end_headers()
        self.wfile.write(resp_body)


if __name__ == '__main__':
    with http.server.HTTPServer(('0.0.0.0', PORT), ProxyHandler) as httpd:
        print(f'Slideshow + API proxy running at http://localhost:{PORT}')
        print(f'  Static files: {ROOT}')
        print(f'  API proxy:    /api/* → {API_BACKEND}/api/*  (CLOUD)')
        httpd.serve_forever()
