import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


class YieldHandler(SimpleHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _load_json(self, filename):
        path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _as_int(self, value, default=0):
        try:
            return int(value)
        except Exception:
            return default

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/summary":
            data = self._load_json("overall_summary.json")
            if not data:
                return self._send_json({"error": "overall_summary.json not found. Run analyze_ripa.py first."}, 404)
            return self._send_json(data[0])

        if path == "/api/yield/beat":
            rows = self._load_json("yield_by_beat.json")
            if rows is None:
                return self._send_json({"error": "yield_by_beat.json not found. Run analyze_ripa.py first."}, 404)

            min_stops = self._as_int(query.get("min_stops", ["0"])[0], 0)
            limit = self._as_int(query.get("limit", ["200"])[0], 200)
            sort = query.get("sort", ["yield_desc"])[0]

            rows = [r for r in rows if int(r.get("stops", 0)) >= min_stops]

            if sort == "yield_asc":
                rows.sort(key=lambda r: float(r.get("yield", 0.0)))
            elif sort == "stops_desc":
                rows.sort(key=lambda r: int(r.get("stops", 0)), reverse=True)
            else:
                rows.sort(key=lambda r: float(r.get("yield", 0.0)), reverse=True)

            return self._send_json(rows[:limit])

        if path == "/api/yield/reason":
            rows = self._load_json("yield_by_stop_reason.json")
            if rows is None:
                return self._send_json({"error": "yield_by_stop_reason.json not found. Run analyze_ripa.py first."}, 404)

            min_stops = self._as_int(query.get("min_stops", ["0"])[0], 0)
            limit = self._as_int(query.get("limit", ["200"])[0], 200)
            sort = query.get("sort", ["yield_desc"])[0]

            rows = [r for r in rows if int(r.get("stops", 0)) >= min_stops]

            if sort == "yield_asc":
                rows.sort(key=lambda r: float(r.get("yield", 0.0)))
            elif sort == "stops_desc":
                rows.sort(key=lambda r: int(r.get("stops", 0)), reverse=True)
            else:
                rows.sort(key=lambda r: float(r.get("yield", 0.0)), reverse=True)

            return self._send_json(rows[:limit])

        if path == "/api/yield/search":
            rows = self._load_json("search_yield_by_reason.json")
            if rows is None:
                return self._send_json({"error": "search_yield_by_reason.json not found. Run analyze_ripa.py first."}, 404)

            min_searches = self._as_int(query.get("min_searches", ["0"])[0], 0)
            limit = self._as_int(query.get("limit", ["200"])[0], 200)
            sort = query.get("sort", ["search_yield_desc"])[0]

            rows = [r for r in rows if int(r.get("searches", 0)) >= min_searches]

            if sort == "search_yield_asc":
                rows.sort(key=lambda r: float(r.get("search_yield", 0.0)))
            elif sort == "searches_desc":
                rows.sort(key=lambda r: int(r.get("searches", 0)), reverse=True)
            else:
                rows.sort(key=lambda r: float(r.get("search_yield", 0.0)), reverse=True)

            return self._send_json(rows[:limit])

        return super().do_GET()


def main():
    parser = argparse.ArgumentParser(description="Run local API + static server for RIPA Yield dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    os.chdir(BASE_DIR)
    httpd = ThreadingHTTPServer((args.host, args.port), YieldHandler)
    print(f"Serving dashboard on http://{args.host}:{args.port}")
    print("API endpoints:")
    print("- /api/summary")
    print("- /api/yield/beat?min_stops=1000&sort=yield_asc&limit=20")
    print("- /api/yield/reason?min_stops=500&sort=yield_desc&limit=20")
    print("- /api/yield/search?min_searches=200&sort=search_yield_desc&limit=20")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
