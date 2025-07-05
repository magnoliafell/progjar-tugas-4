import socket
import logging
import base64
import os

server_address = ('localhost', 8889)

def make_socket():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)
        return sock
    except Exception as e:
        logging.warning(f"Socket error: {e}")
        return None

def send_command(command_str):
    if not command_str.endswith('\r\n\r\n'):
        command_str += '\r\n\r\n'
    sock = make_socket()
    if not sock:
        return False
    try:
        sock.sendall(command_str.encode())
        response = b""
        while True:
            data = sock.recv(4096)
            if data:
                response += data
            else:
                break
        sock.close()
        return response.decode(errors='ignore')
    except Exception as e:
        logging.warning(f"Error: {e}")
        sock.close()
        return False

def get_file_list():
    print("== LIST FILES ==")
    response = send_command("GET /list HTTP/1.0")
    print(response or "Failed to get file list")

def upload_file(filepath):
    print("== UPLOAD FILE ==")
    if not os.path.exists(filepath):
        print("File not found:", filepath)
        return
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode()
    cmd = (
    f"POST /upload HTTP/1.0\r\n"
    f"X-Filename: {filename}\r\n"
    f"Content-Length: {len(encoded.encode())}\r\n"
    f"\r\n{encoded}"
    )
    response = send_command(cmd)
    print(response or "Upload failed")

def delete_file(filename):
    print("== DELETE FILE ==")
    cmd = f"DELETE /{filename} HTTP/1.0"
    response = send_command(cmd)
    print(response or "Delete failed")

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    get_file_list()
    upload_file("donalbebek2.jpg")
    get_file_list()
    delete_file("donalbebek2.jpg")
    get_file_list()
