from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
from threading import Thread
from datetime import datetime
import os
import json


BASE_DIR = pathlib.Path()


class MainServer(BaseHTTPRequestHandler):

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        self.save_data_via_socket(data_parse)

        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def save_data_via_socket(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = '0.0.0.0', 5000
        data = message.encode()
        sock.sendto(data, server)
        sock.close()


def run(server_class=HTTPServer, handler_class=MainServer):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        print('Старт server')
        socket_server = Thread(target=server_socket)
        socket_server.start()
        http.serve_forever()
    except KeyboardInterrupt:
        print()
        print('вихід')
        http.server_close()


def server_socket():
    print("Старт socket_server")
    UDP_IP = '0.0.0.0'
    UDP_PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = (UDP_IP, UDP_PORT)
    sock.bind(server)
    # server_socket.listen(2)
    try:
        while True:
            data, address = sock.recvfrom(1024)

            if not os.path.exists('storage'):
                os.makedirs('storage')

            if not data:
                break
            time_data = datetime.now()
            data_parm = urllib.parse.parse_qs(data.decode())
            if data_parm:
                data_to_save = {str(time_data):
                                {'username': str(data_parm.get('username', [''])[0]),
                                 'message': str(data_parm.get('message', [''])[0])}
                                }
            print(data_to_save)
            with open('storage/data.json', 'a') as file:
                json.dump(data_to_save, file, indent=2)
            print("Записано та збережено")
    except KeyboardInterrupt:
        print(f'Щось зламалося')
    finally:
        sock.close()


if __name__ == '__main__':
    run()
