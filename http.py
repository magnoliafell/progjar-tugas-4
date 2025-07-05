import os
import base64
from glob import glob
from datetime import datetime

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html',
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = [
            f"HTTP/1.0 {kode} {message}\r\n",
            f"Date: {tanggal}\r\n",
            "Connection: close\r\n",
            "Server: myserver/1.0\r\n",
            f"Content-Length: {len(messagebody)}\r\n"
        ]
        for kk in headers:
            resp.append(f"{kk}: {headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers = ''.join(resp)
        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()
        return response_headers.encode() + messagebody

    def proses(self, data):
        requests = data.split("\r\n")
        if len(requests) < 1:
            return self.response(400, 'Bad Request', '', {})
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n != '']

        body = ""
        if "\r\n\r\n" in data:
            body_start = data.find("\r\n\r\n") + 4
            body = data[body_start:].strip()

        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            path = j[1].strip()
            if method == 'GET':
                return self.http_get(path, all_headers)
            elif method == 'POST':
                return self.http_post(path, all_headers, body)
            elif method == 'DELETE':
                return self.http_delete(path, all_headers)
            else:
                return self.response(400, 'Bad Request', '', {})
        except:
            return self.response(400, 'Bad Request', '', {})

    def http_get(self, path, headers):
        files = glob('./*')
        if path == '/':
            return self.response(200, 'OK', 'Ini Adalah web Server percobaan', {})
        if path == '/video':
            return self.response(302, 'Found', '', {'Location': 'https://youtu.be/katoxpnTf04'})
        if path == '/santai':
            return self.response(200, 'OK', 'santai saja', {})
        if path == '/list':
            file_list = glob('./upload/*')
            if file_list:
                names = '\n'.join([f"- {os.path.basename(f)}" for f in file_list])
                return self.response(200, 'OK', f"Files:\n{names}", {})
            else:
                return self.response(200, 'OK', 'No file detected', {})

        filename = '.' + path
        if not os.path.exists(filename):
            return self.response(404, 'Not Found', '', {})
        ext = os.path.splitext(filename)[1]
        content_type = self.types.get(ext, 'application/octet-stream')
        with open(filename, 'rb') as f:
            data = f.read()
        return self.response(200, 'OK', data, {'Content-Type': content_type})

    def http_post(self, path, headers, body):
        if path == '/upload':
            header_dict = {}
            for h in headers:
                if ':' in h:
                    k, v = h.split(':', 1)
                    header_dict[k.strip()] = v.strip()
            filename = header_dict.get('X-Filename')
            if not filename:
                return self.response(400, 'Bad Request', 'X-Filename header missing', {})
            try:
                filedata = base64.b64decode(body)
                os.makedirs('./upload', exist_ok=True)
                with open(f'./upload/{filename}', 'wb') as f:
                    f.write(filedata)
                return self.response(200, 'OK', f'File {filename} berhasil diupload', {})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Error: {e}', {})
        return self.response(404, 'Not Found', 'POST endpoint tidak ditemukan', {})

    def http_delete(self, path, headers):
        filename = path.lstrip('/')
        filepath = f'./upload/{filename}'
        if not os.path.exists(filepath):
            return self.response(404, 'Not Found', 'File not found', {})
        try:
            os.remove(filepath)
            return self.response(200, 'OK', 'Success delete file', {})
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error: {e}', {})
