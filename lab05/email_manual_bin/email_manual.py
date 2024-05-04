import socket
import ssl
import sys
from email.base64mime import body_encode as encode_base64
from getpass import getpass
import uuid


context = ssl.create_default_context()
hostname = "smtp.yandex.ru"
port = 465


def read_msg(ssock):
    msg = b""
    while True:
        cur = ssock.recv(1024)
        msg += cur
        if len(cur) < 1024:
            break
    result = msg.decode()
    for line in result.split('\r\n')[:-1]:
        print("<< ", line)
    print()

    return result


def send_msg(ssock, msg, hidden=False):
    if hidden:
        print(">>  [hidden message]")
    else:
        print(">> ", msg)
    ssock.send((msg + "\r\n").encode())


if __name__ == "__main__":

    receiver = sys.argv[1]
    filename = sys.argv[2]
    login = "tochilina.2002@yandex.ru"
    password = getpass()

    with open(filename, 'rb') as file:
        content = file.read()

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            read_msg(ssock)
            send_msg(ssock, f"HELO {login}")
            read_msg(ssock)
            auth_info = "\0%s\0%s" % (login, password)
            send_msg(ssock, f"AUTH PLAIN {encode_base64(auth_info.encode(), eol='')}", hidden=True)
            read_msg(ssock)
            send_msg(ssock, f"MAIL FROM: <{login}>")
            read_msg(ssock)
            send_msg(ssock, f"RCPT TO: <{receiver}>")
            read_msg(ssock)
            send_msg(ssock, "DATA")
            read_msg(ssock)
            
            send_msg(ssock, f"From: Ekaterina Tochilina <{login}>")
            send_msg(ssock, "Subject: Mail from Lab05")
            boundary = str(uuid.uuid4())
            send_msg(ssock, f"Content-Type: multipart/mixed; boundary={boundary}")
            send_msg(ssock, "")
            send_msg(ssock, "--" + boundary)

            send_msg(ssock, f"Content-Type: application/octet-stream")
            send_msg(ssock, f"Content-Disposition: attachment; filename={filename}")
            send_msg(ssock, f"Content-Transfer-Encoding: base64")
            send_msg(ssock, "")
            send_msg(ssock, encode_base64(content), hidden=True)
            send_msg(ssock, "")
            send_msg(ssock, "--" + boundary)

            send_msg(ssock, "Content-Type: text/plain")
            send_msg(ssock, "")
            send_msg(ssock, "The file is attached.")
            send_msg(ssock, "")
            send_msg(ssock, "--" + boundary + "--")
            
            send_msg(ssock, ".")
            read_msg(ssock)
            send_msg(ssock, "QUIT")
            read_msg(ssock)
            exit(0)
            ssock.send("\r\n".encode())
            print(ssock.recv(1024))
            boundary = str(uuid.uuid4())
            boundary_msg = "--" + boundary + "\r\n"
            ssock.send("DATA\r\n".encode())
            print(ssock.recv(1024))
            ssock.send("From: Ekaterina Tochilina <tochilina.2002@yandex.ru>\r\n".encode())
            ssock.send("Subject: Mail from 5 lab\r\n".encode())
            ssock.send(f"Content-Type: multipart/mixed; boundary={boundary}\r\n".encode())
            ssock.send("\r\n".encode())
            ssock.send(boundary_msg.encode())
            ssock.send("Content-Type: text/plain\r\n".encode())
            ssock.send("\r\n".encode())
            ssock.send("Some message\r\n".encode())
            ssock.send("\r\n".encode())
            ssock.send(boundary_msg.encode())
            ssock.send("Content-Type: application/octet-stream\r\n".encode())
            ssock.send("Content-Disposition: attachment; filename=apple.jpg\r\n".encode())
            ssock.send("Content-Transfer-Encoding: base64\r\n".encode())
            ssock.send("\r\n".encode())
            ssock.send((encode_base64(file_content) + "\r\n").encode())
            ssock.send("\r\n".encode())
            ssock.send(("--" + boundary + "--\r\n").encode())
            ssock.send(".\r\n".encode())
            print(ssock.recv(1024))
            ssock.send("QUIT\r\n".encode())
            print(ssock.recv(1024))
