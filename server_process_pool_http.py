import socket
import logging
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

def create_new_httpserver():
    return HttpServer()

def ProcessTheClient(connection, address):
    rcv = ""
    httpserver = create_new_httpserver()
    try:
        while True:
            data = connection.recv(1024)
            if data:
                rcv += data.decode()
                if '\r\n\r\n' in rcv:
                    logging.warning(f"[Process {address}] Request: {rcv}")
                    hasil = httpserver.proses(rcv)
                    connection.sendall(hasil)
                    connection.close()
                    return
            else:
                break
    except Exception as e:
        logging.warning(f"Error processing client {address}: {e}")
    finally:
        connection.close()

def Server():
    the_clients = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 8889))
    sock.listen(10)

    with ProcessPoolExecutor(max_workers=10) as executor:
        while True:
            try:
                connection, address = sock.accept()
                logging.warning(f"Connection from {address}")
                future = executor.submit(ProcessTheClient, connection, address)
                the_clients.append(future)
                the_clients = [c for c in the_clients if c.running()]
            except KeyboardInterrupt:
                print("Server stopped by user.")
                break
            except Exception as e:
                logging.warning(f"Server error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    Server()
