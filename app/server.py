from __future__ import annotations

import json
import mimetypes
import numpy as np
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.predictor import EngineSwapPredictor


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle NumPy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
PREDICTOR = EngineSwapPredictor()


class PredictorRequestHandler(BaseHTTPRequestHandler):
    server_version = "EngineSwapPredictor/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/meta":
            self._json(PREDICTOR.metadata())
            return
        if parsed.path == "/api/example":
            self._json(PREDICTOR.sample_request())
            return
        if parsed.path in {"/", "/index.html"}:
            self._static_file(STATIC / "index.html")
            return
        self._static_file(STATIC / parsed.path.removeprefix("/"))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
        except Exception as e:
            print(f"Error reading JSON: {e}")
            self._json({"error": f"Invalid JSON: {str(e)}"}, status=400)
            return
        
        try:
            if parsed.path == "/api/predict":
                self._json(PREDICTOR.predict(payload))
                return
            if parsed.path == "/api/compare":
                self._json(PREDICTOR.compare(payload))
                return
            self._json({"error": "Route not found"}, status=404)
        except StopIteration:
            self._json({"error": "Unknown engine_code or chassis_code"}, status=400)
        except (TypeError, ValueError, KeyError) as error:
            print(f"Error in {parsed.path}: {error}")
            self._json({"error": str(error)}, status=400)
        except Exception as error:
            print(f"Unexpected error in {parsed.path}: {error}")
            self._json({"error": f"Server error: {str(error)}"}, status=500)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def _json(self, payload: dict | list, status: int = 200) -> None:
        body = json.dumps(payload, indent=2, cls=NumpyEncoder).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static_file(self, path: Path) -> None:
        requested = path.resolve()
        if not str(requested).startswith(str(STATIC.resolve())) or not requested.exists() or requested.is_dir():
            self._json({"error": "Not found"}, status=404)
            return
        body = requested.read_bytes()
        content_type = mimetypes.guess_type(str(requested))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    server = ThreadingHTTPServer((host, port), PredictorRequestHandler)
    print(f"Engine Swap Performance Predictor running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
