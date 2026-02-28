import socket
import struct
import argparse
import time

parser = argparse.ArgumentParser(description='Multicast receiver')
parser.add_argument('--group', default='239.1.1.1', help='Multicast group IP')
parser.add_argument('--port', type=int, default=5000, help='UDP port')
parser.add_argument('--iface', default='172.20.10.5', help='Local interface IP to join from (0.0.0.0 = default)')
args = parser.parse_args()

GROUP = args.group
PORT = args.port
IFACE = args.iface

INTERFAC_IP = '172.20.10.5'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# Allow multiple programs on same machine to bind the same port (best-effort)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sock.bind(('', PORT))
except OSError as e:
    print(f"Erreur bind sur le port {PORT}: {e}")
    raise

mreq = struct.pack('4s4s', socket.inet_aton(GROUP), socket.inet_aton(INTERFAC_IP))
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"En attente de messages sur {GROUP}:{PORT} (iface={IFACE})...")
try:
    while True:
        data, addr = sock.recvfrom(4096)
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"[{ts}] Reçu {len(data)} octets de {addr}: {data.decode(errors='replace')}")
except KeyboardInterrupt:
    print('\nInterrompu par l\'utilisateur, quittation du groupe...')
    try:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    except Exception:
        pass
    sock.close()