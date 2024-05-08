import socket
import sys
import random

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

if __name__ == "__main__":
    timeout = int(sys.argv[1])

    with socket.socket(socket.AF_INET,
                       socket.SOCK_DGRAM) as sock:

        sock.bind((UDP_IP, UDP_PORT))
        sock.settimeout(timeout)

        content_length = None
        result = b""
        expected = 0
        while content_length is None or len(result) < content_length:
            try:
                data, addr = sock.recvfrom(2048)
                number = int(data[0])
                print("Got packet", number)

                if random.random() < 0.7:
                    sock.sendto(number.to_bytes(1), addr)
                
                if number == expected: 
                    if content_length is None:
                        content_length = int.from_bytes(data[1:])
                    else:
                        result += data[1:]

                    print(f"Read {len(result)}/{content_length}")
                    expected = (number + 1) % 2

            except TimeoutError:
                print("...timeout...")

        with open("result", "wb") as f:
            f.write(result)
