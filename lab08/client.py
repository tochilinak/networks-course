import socket
import sys
import time
import random

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFSIZE = 1024


def send_msg(number, msg):
    if random.random() < 0.7:
        sock.sendto(number.to_bytes(1) + msg, (UDP_IP, UDP_PORT))
    
    print("Sent", number)


if __name__ == "__main__":
    timeout = int(sys.argv[1])
    filename = sys.argv[2]
    with open(filename, "rb") as f:
        content = f.read()

    messages = [len(content).to_bytes(4)]
    idx = 0
    while idx < len(content):
        messages.append(content[idx:idx+BUFSIZE])
        idx += BUFSIZE

    with socket.socket(socket.AF_INET,
                       socket.SOCK_DGRAM) as sock:
        
        sock.settimeout(timeout)

        number = 0
        while number < len(messages):
            send_msg(number % 2, messages[number])
            try:
                answer = sock.recv(1024)
                if int(answer[0]) == number % 2:
                    number += 1
                    print(f"Sending portion from {(number-1)*BUFSIZE} bytes.")
            except TimeoutError:
                print("...timeout...")
