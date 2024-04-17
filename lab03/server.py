import socket
import sys
from pathlib import Path
from threading import Thread


def process_client(conn, addr):
    try:
        while True:
            msg = conn.recv(1024)
            if len(msg) == 0:
                break
            lines = msg.split(b'\r\n')
            
            print("Request:\n", lines)
            
            given_path = lines[0].split()[1][1:].decode()
            path = Path('server_data') / given_path
            
            print("Requested path:", path)

            try:
                with open(path, 'r') as file:
                    content = file.read()
                    msg = f"HTTP/1.1 200 OK\r\n" + \
                          f"Content-Length: {len(content)}\r\n" + \
                          f"\r\n" + \
                          content
                    conn.send(msg.encode())
            except (FileNotFoundError, IsADirectoryError):
                content = "404 Not Found"
                msg = f"HTTP/1.1 404 Not Found\r\n" + \
                      f"Content-Length: {len(content)}\r\n" + \
                      f"\r\n" + \
                      content
                conn.send(msg.encode())

    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit(1)

    port = int(sys.argv[1])
    print("Starting server at port", port)

    with socket.socket() as sock:
        sock.bind(('localhost', port))
        sock.listen(1)

        while True:
            conn, addr = sock.accept()
            t = Thread(target=process_client, args=(conn, addr))
            t.start()
