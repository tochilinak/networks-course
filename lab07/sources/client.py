import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)
print()

with socket.socket(socket.AF_INET,
                   socket.SOCK_DGRAM) as sock:
    
    sock.settimeout(1)
    
    start = time.time()
    for i in range(1, 11):
        print("Ping", i, round((time.time() - start) * 1000), "mls")
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        try:
            answer = sock.recv(1024)
            print("Got from server:", answer)
        except TimeoutError:
            print("Request timed out")
