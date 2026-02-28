import socket
import threading
import argparse


def handle_client(conn, addr, echo=False):
    try:
        data = conn.recv(4096)
        if not data:
            return
        print(f"TCP from {addr}: {data.decode(errors='replace')}")
        if echo:
            conn.sendall(data)
    except Exception as e:
        print('Client handler error:', e)
    finally:
        try:
            conn.close()
        except Exception:
            pass


def run_server(host='0.0.0.0', port=6000, echo=False, once=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)
    print(f"TCP server listening on {host}:{port}")
    try:
        while True:
            conn, addr = sock.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr, echo), daemon=True)
            t.start()
            if once:
                break
    except KeyboardInterrupt:
        print('\nServer interrupted')
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description='Simple threaded TCP server')
    parser.add_argument('--host', default='0.0.0.0', help='Bind address')
    parser.add_argument('--port', type=int, default=6000, help='Port')
    parser.add_argument('--echo', action='store_true', help='Echo received data back')
    parser.add_argument('--once', action='store_true', help='Accept one connection then exit')
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, echo=args.echo, once=args.once)


if __name__ == '__main__':
    main()
