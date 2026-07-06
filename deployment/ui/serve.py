from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main():
    ui_dir = Path(__file__).resolve().parent
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=ui_dir, **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 8088), handler)
    print(f"Serving {ui_dir / 'index.html'} at http://127.0.0.1:8088")
    server.serve_forever()


if __name__ == "__main__":
    main()
