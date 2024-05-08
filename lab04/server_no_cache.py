import socket
import sys
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def read_msg(conn):
    msg = b""
    while True:
        cur = conn.recv(1024)
        msg += cur
        if len(cur) < 1024:
            break
    return msg


def log(msg):
    print(msg)
    with open("log.txt", "a") as file:
        file.write(msg + "\n")


last_full_url = ""


def process_client(conn, addr):
    global last_full_url

    try:
        msg = read_msg(conn)
        lines = msg.split(b'\r\n')
        
        first_line = lines[0].split()
        method = first_line[0].decode()
        given_url = first_line[1][1:].decode()

        if given_url[:4] != "www.":
            given_url = last_full_url + "/" + given_url
        else:
            last_full_url = given_url

        request = Request("http://" + given_url, method=method)
        log(f"URL: {given_url}, method: {method}")
        try:
            resp = urlopen(request)

            body = resp.read()
            content_length = len(body)
            status = resp.status
            reason = resp.reason

            msg = (f"HTTP/1.0 {status} {reason}\r\n".encode() +
                   f"Content-Length: {content_length}\r\n".encode() +
                   f"\r\n".encode() +
                   body)
            
            conn.send(msg)
            log(f"Response: {status} {reason}")
        
        except HTTPError as e:

            msg = f"HTTP/1.0 {e.code} {e.msg}\r\n\r\n"
            conn.send(msg.encode())
            log(f"Response: {e.code} {e.msg}")

    except Exception as e:
        print("Request failed with exception", e)

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
            # single-threaded server, for one client
            conn, addr = sock.accept()
            t = Thread(target=process_client, args=(conn, addr))
            t.run()
