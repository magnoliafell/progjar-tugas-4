import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = b""
    try:
        while b'\r\n\r\n' not in rcv:
            data = connection.recv(4096)
            if not data:
                break
            rcv += data

        header_data, _, body_data = rcv.partition(b'\r\n\r\n')
        headers = header_data.decode(errors='ignore').split('\r\n')
        content_length = 0
        for h in headers:
            if h.lower().startswith('content-length:'):
                content_length = int(h.split(':', 1)[1].strip())
                break

        while len(body_data) < content_length:
            more_data = connection.recv(4096)
            if not more_data:
                break
            body_data += more_data

        full_data = header_data + b'\r\n\r\n' + body_data
        hasil = httpserver.proses(full_data.decode(errors='ignore'))
        connection.sendall(hasil)
    except Exception as e:
        logging.warning(f"Error: {e}")
    finally:
        connection.close()


def Server():
    the_clients = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 8885))
    sock.listen(10)

    with ThreadPoolExecutor(20) as executor:
        while True:
            connection, address = sock.accept()
            logging.warning(f"Connection from {address}")
            p = executor.submit(ProcessTheClient, connection, address)
            the_clients = [c for c in the_clients if c.running()]

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    Server()
