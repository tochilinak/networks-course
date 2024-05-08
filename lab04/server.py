import socket
import sys
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path


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


cache_last_modified = {}
cache_etag = {}
cache_path = Path("cache")
file_cnt = 0
cache_filename = {}


def add_file_in_cache(url, content):
    global cache_path, file_cnt
    file_cnt += 1
    filename = cache_path / f"file_{file_cnt}"
    cache_filename[url] = filename
    with open(filename, "wb") as f:
        f.write(content)


def process_client(conn, addr):
    global last_full_url

    try:
        msg = read_msg(conn)
        lines = msg.split(b'\r\n')
        
        first_line = lines[0].split()
        method = first_line[0].decode()
        given_url = first_line[1][1:].decode()

        headers = {}
        if given_url in cache_last_modified:
            headers["If-Modified-Since"] = cache_last_modified[given_url]
            headers["If-None-Match"] = cache_etag[given_url]

        request = Request("http://" + given_url, method=method, headers=headers)
        log(f"URL: {given_url}, method: {method}")
        try:
            resp = urlopen(request)

            body = resp.read()
            content_length = len(body)
            status = resp.status
            reason = resp.reason

            if status == 200:
                last_modified = resp.getheader('Last-Modified')
                etag = resp.getheader('ETag')
                print(last_modified, etag)
                if last_modified is not None and etag is not None:
                    cache_last_modified[given_url] = last_modified
                    cache_etag[given_url] = etag
                    add_file_in_cache(given_url, body)

            msg = (f"HTTP/1.0 {status} {reason}\r\n".encode() +
                   f"Content-Length: {content_length}\r\n".encode() +
                   f"\r\n".encode() +
                   body)
            
            conn.send(msg)
            log(f"Response: {status} {reason}")
        
        except HTTPError as e:

            if e.code == 304:
                filename = cache_filename[given_url]
                with open(filename, 'rb') as f:
                    body = f.read()
                    status = 200
                    reason = "OK"
                    content_length = len(body)

                msg = (f"HTTP/1.0 {status} {reason}\r\n".encode() +
                       f"Content-Length: {content_length}\r\n".encode() +
                       f"\r\n".encode() +
                       body)
                conn.send(msg)
                log(f"Got result from cache.")


            else:
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

    cache_path.mkdir(exist_ok=True)

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
