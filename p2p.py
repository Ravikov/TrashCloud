import requests
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

SAVE_DIR = "./share"
CHUNK_SIZE = 2048 * 2048
os.makedirs(SAVE_DIR, exist_ok=True)

class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        filename: str = self.headers.get("X-Filename", "download")
        filelength: int = int(self.headers["Content-Length"])

        remainning: int = filelength

        path: str = os.path.join(SAVE_DIR, filename)
        with open(path, "wb") as f:
            while remainning > 0:
                chunk = self.rfile.read(min(CHUNK_SIZE, remainning))
                if not chunk:
                    break
                f.write(chunk)
                remainning -= len(chunk)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def read_in_chunk(filepath: str):
    with open(filepath, "rb") as f:
        while True:
            chunk: bytes = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

def send(target_ip: str, target_port: int, filepath: str):
    filename: str = os.path.basename(filepath)
    
    r = requests.post(
        f"http://{target_ip}:{target_port}",
        data=read_in_chunk(filepath),
        headers={"X-Filename": filename},
        timeout=300
    )
    print("状态码：{r.status_code}")

if __name__ == "__main__":
    if sys.argv[1] == "serve":
        print("监听")
        server = HTTPServer(("", 7070), Handler)
        server.serve_forever()
    elif sys.argv[1] == "send":
        send(sys.argv[2], int(sys.argv[3]), sys.argv[4])