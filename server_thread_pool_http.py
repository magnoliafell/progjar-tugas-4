import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(1024)
            if data:
                rcv += data.decode()
                if '\r\n\r\n' in rcv:
                    logging.warning(f"data dari client: {rcv}")
                    hasil = httpserver.proses(rcv)
                    connection.sendall(hasil)
                    connection.close()
                    return
            else:
                break
        except Exception as e:
            logging.warning(f"Error: {e}")
            break
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
