import socket
import logging
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def read_full_request(connection):
    rcv = b""
    while b'\r\n\r\n' not in rcv:
        part = connection.recv(4096)
        if not part:
            break
        rcv += part

    header_data, _, body_data = rcv.partition(b'\r\n\r\n')
    headers = header_data.decode(errors='ignore').split('\r\n')

    content_length = 0
    for h in headers:
        if h.lower().startswith('content-length:'):
            try:
                content_length = int(h.split(':', 1)[1].strip())
            except:
                content_length = 0
            break

    while len(body_data) < content_length:
        more = connection.recv(4096)
        if not more:
            break
        body_data += more

    return (header_data + b'\r\n\r\n' + body_data).decode(errors='ignore')


def handle_request_in_process(request_text):
    return httpserver.proses(request_text)


def Server():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8889))
    my_socket.listen(5)

    with ProcessPoolExecutor(5) as executor:
        while True:
            connection, client_address = my_socket.accept()
            logging.warning(f"Connection from {client_address}")

            try:
                request_text = read_full_request(connection)
                logging.warning(f"Request:\n{request_text}")

                future = executor.submit(handle_request_in_process, request_text)
                response_data = future.result(timeout=10) 

                connection.sendall(response_data)
            except Exception as e:
                logging.warning(f"Error: {e}")
                connection.sendall(b"HTTP/1.0 500 Internal Server Error\r\n\r\n")
            finally:
                connection.close()


def main():
    logging.basicConfig(level=logging.WARNING)
    Server()

if __name__ == "__main__":
    main()
