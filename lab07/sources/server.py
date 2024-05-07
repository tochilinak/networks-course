import socket
import random

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

with socket.socket(socket.AF_INET,
                   socket.SOCK_DGRAM) as sock:

    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        print("received message: %s from" % data, addr)
        new_msg = data.upper()
        if random.random() < 0.8:
            sock.sendto(new_msg, addr)
