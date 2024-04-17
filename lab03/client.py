import socket
import sys


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]

    with socket.socket() as sock:
        sock.connect((host, port))

        msg = f"GET /{filename} HTTP/1.1"
        sock.send(msg.encode())
        
        answer = sock.recv(1024)
        print(answer)
