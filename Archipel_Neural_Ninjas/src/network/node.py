import socket
import struct
import threading
import time
import argparse
import uuid
# from pyexpat.errors import messages
#
# from src.network.peer_table import PeerTable
# from src.network.receiver import mreq

MULTICAST_GROUP_IP = "239.255.42.99"
MULTICAST_GROUP_PORT = 6000

class Node:
    def __init__(self, tcp_port):
        self.tcp_port = tcp_port
        self.node_id = str(uuid.uuid4())[:8]
        self.peers = {}
        self.lock = threading.Lock()
        self.connections = {}
        self.conn_lock = threading.Lock()

    def start(self):
        threading.Thread(target=self.listen_multicast,daemon=True).start()
        threading.Thread(target=self.send_hello,daemon=True).start()
        threading.Thread(target=self.clean_peers,daemon=True).start()
        threading.Thread(target=self.start_tcp_server,daemon=True).start()

        print("Node started")
        print(f"Node id: {self.node_id}")
        print(f"TCP Port: {self.tcp_port}")

        while True:
            time.sleep(30)
            print(f"[Peers:] {self.peers}")

    def listen_multicast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind(("",MULTICAST_GROUP_PORT))

        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP_IP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            data,addr = sock.recvfrom(1024)
            message = data.decode()

            if message.startswith("HELLO"):
                _, node_id, tcp_port = message.split(":")
                tcp_port = int(tcp_port)
                if node_id != self.node_id:
                    with self.lock:
                        self.peers[node_id] = {
                            "ip": addr[0],
                            "port": tcp_port,
                            "last_seen": time.time()
                        }
                    print(f"Discovered peer: {node_id} at {addr[0]}:{tcp_port}")

    def send_hello(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ttl = struct.pack("b",1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        while True:
            message=f"HELLO:{self.node_id}:{self.tcp_port}"
            sock.sendto(message.encode(),(MULTICAST_GROUP_IP,MULTICAST_GROUP_PORT))
            print("HELLO!")
            time.sleep(30)

    def clean_peers(self):
        while True:
            now = time.time()
            to_remove = []
            with self.lock:
                for node_id, info in list(self.peers.items()):
                    if now-info["last_seen"] > 90:
                        to_remove.append(node_id)
                for node_id in to_remove:
                    print(f"Peer {node_id} timed out")
                    del self.peers[node_id]
            time.sleep(5)

    def start_tcp_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0",self.tcp_port))
        server.listen(5)

        print(f"Listening on port {self.tcp_port}")

        while True:
            conn, addr = server.accept()
            node_id = addr[0]
            with self.conn_lock:
                self.connections[node_id] = conn

            print(f"Connection from {addr}")
            threading.Thread(target=self.handle_client, args=(node_id,conn), daemon=True).start()


    def handle_client(self, node_id, conn):
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received from {node_id}: {data.decode()}")
        conn.close()

    def connect_to_peer(self, node_id, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

        with self.conn_lock:
            self.connections[node_id] = sock

        threading.Thread(target=self.handle_peer_connection, args=(node_id,sock), daemon=True).start()

        print(f"connected to {node_id}")

    def handle_peer_connection(self, node_id, conn):
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"From {node_id}: {data.decode()}")
        finally:
            print(f"Disconnected from {node_id}")
            conn.close()
            if node_id in self.connections:
                del self.connections[node_id]

    def send_to_peer(self, node_id, message):
        if node_id in self.connections:
            with self.conn_lock:
                sock = self.connections[node_id]
                sock.send(message.encode())
        else:
            print("Not connected to that peer")

    # while True:
    #     cmd = input(">> ")
    #     if cmd.startswith("connect"):
    #         _, ip, port = cmd.split()
    #         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         sock.connect((ip, int(port)))
    #         sock.send(b"Hello from " + self.node_id.encode())
    #         sock.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port",type=int,required=True)
    args = parser.parse_args()

    node = Node(args.port)
    node.start()

