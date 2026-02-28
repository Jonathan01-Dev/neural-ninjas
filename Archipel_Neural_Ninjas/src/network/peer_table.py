import time
from threading import Lock

class PeerTable:
    """Simple in-memory peer table.

    Stores peers as {key: {'name':..., 'ip':..., 'tcp_port':..., 'last_seen':...}}
    Keying uses ip:tcp_port to avoid collisions.
    """
    def __init__(self, ttl=60):
        self.peers = {}
        self.ttl = ttl
        self.lock = Lock()

    def _key(self, ip, tcp_port):
        return f"{ip}:{tcp_port}"

    def add_or_update(self, ip, name, tcp_port):
        key = self._key(ip, tcp_port)
        now = time.time()
        with self.lock:
            self.peers[key] = {
                'name': name,
                'ip': ip,
                'tcp_port': tcp_port,
                'last_seen': now,
            }

    def remove_stale(self):
        now = time.time()
        with self.lock:
            stale = [k for k,v in self.peers.items() if now - v['last_seen'] > self.ttl]
            for k in stale:
                del self.peers[k]

    def get_peers(self):
        with self.lock:
            # return a shallow copy
            return {k: v.copy() for k, v in self.peers.items()}

    def __len__(self):
        with self.lock:
            return len(self.peers)


if __name__ == '__main__':
    # tiny smoke test
    t = PeerTable(ttl=1)
    t.add_or_update('10.0.0.5', 'alice', 6000)
    t.add_or_update('10.0.0.7', 'bob', 6000)
    print('Peers after add:', t.get_peers())
    time.sleep(1.1)
    t.remove_stale()
    print('Peers after cleanup:', t.get_peers())
