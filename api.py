import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ORDERS_FILE = Path(__file__).resolve().with_name("orders.json")


class OrdersHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path != "/GetOrders":
            self.send_error(404, "Not Found")
            return

        try:
            with ORDERS_FILE.open(encoding="utf-8") as orders_file:
                orders = json.load(orders_file)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            logging.exception("Could not read orders from %s", ORDERS_FILE)
            self.send_json(500, {"error": "Could not read orders"})
            return

        self.send_json(200, orders)

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = os.environ.get("PORT")
    host = "0.0.0.0" if port is not None else "127.0.0.1"
    server = ThreadingHTTPServer((host, int(port) if port is not None else 8000), OrdersHandler)
    print(f"Serving on {host}:{server.server_port}; endpoint: /GetOrders", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()