import socket
import struct
import sys


def send_echo(ttl: int, host):
    # extracted these bytes from wireshark
    a = [0x08,0x00,0x82,0x6a,0x00,0x0f,0x00,0x01,0x48,0x49,0x4a,0x4b,0x4c,0x4d,
         0x4e,0x4f,0x50,0x51,0x52,0x53,0x54,0x55,0x56,0x57,0x58,0x59,0x5a,0x5b,0x5c,0x5d,
         0x5e,0x5f,0x60,0x61,0x62,0x63,0x64,0x65,0x66,0x67]

    msg = bytes(a)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    sock.sendto(msg, (host, 1))



if __name__ == "__main__":
    host = sys.argv[1]
    proto = socket.getprotobyname('icmp')
    path = []
    with socket.socket(type=socket.SOCK_RAW, proto=proto) as sock:
        sock.settimeout(1)
        i = 0
        while True:
            i += 1
            send_echo(i, host)
            try:
                data, addr = sock.recvfrom(1024)
                # print("Got ", data, "from", addr)
                t, c = data[20], data[21]
                print("(type, code):", (t, c))
                print("from", addr[0])
                path.append(addr[0])
                if t == 0 and c == 0:
                    break
            except TimeoutError:
                print("..timeout..")

        print()
        print("Route:")
        for addr in path:
            try:
                name = (socket.gethostbyaddr(addr)[0],)
            except:
                name = tuple()
            print("    ", addr, *name)
