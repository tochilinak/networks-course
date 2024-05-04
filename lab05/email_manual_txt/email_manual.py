import socket
import ssl
import sys
from email.base64mime import body_encode as encode_base64
from getpass import getpass


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

    with open(filename, 'r') as file:
        content = file.readlines()

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
            send_msg(ssock, "")
            for line_raw in content:
                line = line_raw.strip()
                assert line != "."
                send_msg(ssock, line)
            send_msg(ssock, ".")
            read_msg(ssock)
            send_msg(ssock, "QUIT")
            read_msg(ssock)
