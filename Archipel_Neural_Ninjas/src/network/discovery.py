import socket
import struct
import threading
import time
import json
import argparse
import platform
from peer_table import PeerTable

DEFAULT_GROUP = '239.1.1.1'
DEFAULT_MPORT = 5000


class Discovery:
    def __init__(self, name=None, tcp_port=6000, group=DEFAULT_GROUP, mport=DEFAULT_MPORT, iface='0.0.0.0', interval=2):
        self.name = name or platform.node() or 'unknown'
        self.tcp_port = tcp_port
        self.group = group
        self.mport = mport
        self.iface = iface
        self.interval = interval
        self.peer_table = PeerTable()
        self._stop = threading.Event()

    def start(self, once=False, duration=None):
        self._stop.clear()
        self.listener_thread = threading.Thread(target=self._listener, daemon=True)
        self.sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self.listener_thread.start()
        self.sender_thread.start()
        start = time.time()
        try:
            while not self._stop.is_set():
                time.sleep(0.2)
                self.peer_table.remove_stale()
                if once:
                    # wait a short time then stop
                    time.sleep(1.0)
                    break
                if duration and (time.time() - start) >= duration:
                    break
        except KeyboardInterrupt:
            pass
        self.stop()

    def stop(self):
        self._stop.set()

    def _sender_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ttl = struct.pack('b', 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        try:
            if self.iface != '0.0.0.0':
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.iface))
        except Exception:
            pass

        msg = {'name': self.name, 'tcp_port': self.tcp_port}
        while not self._stop.is_set():
            try:
                sock.sendto(json.dumps(msg).encode(), (self.group, self.mport))
            except Exception:
                pass
            time.sleep(self.interval)

    def _listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('', self.mport))
        except OSError as e:
            print('Bind error:', e)
            return

        mreq = struct.pack('4s4s', socket.inet_aton(self.group), socket.inet_aton(self.iface))
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except Exception:
            pass

        sock.settimeout(1.0)
        while not self._stop.is_set():
            try:
                data, addr = sock.recvfrom(4096)
            except socket.timeout:
                continue
            except Exception:
                break
            try:
                obj = json.loads(data.decode())
                name = obj.get('name')
                tcp_port = int(obj.get('tcp_port', 0))
                ip = addr[0]
                self.peer_table.add_or_update(ip, name, tcp_port)
                print(f"Discovered {name} at {ip}:{tcp_port}")
            except Exception:
                # ignore non-json or malformed messages
                pass


def main():
    parser = argparse.ArgumentParser(description='Discovery: multicast HELLO sender+listener')
    parser.add_argument('--name', help='Your node name')
    parser.add_argument('--tcp-port', type=int, default=6000, help='Your TCP service port')
    parser.add_argument('--group', default=DEFAULT_GROUP, help='Multicast group')
    parser.add_argument('--mport', type=int, default=DEFAULT_MPORT, help='Multicast UDP port')
    parser.add_argument('--iface', default='0.0.0.0', help='Local interface IP to join from')
    parser.add_argument('--interval', type=float, default=2.0, help='HELLO send interval (s)')
    parser.add_argument('--once', action='store_true', help='Send one HELLO and listen shortly then exit')
    parser.add_argument('--duration', type=float, help='Run for N seconds then exit')
    args = parser.parse_args()

    d = Discovery(name=args.name, tcp_port=args.tcp_port, group=args.group, mport=args.mport, iface=args.iface, interval=args.interval)
    d.start(once=args.once, duration=args.duration)
    print('Final peers:', d.peer_table.get_peers())


if __name__ == '__main__':
    main()
