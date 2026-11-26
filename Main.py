import socket
import traceback
from threading import *
from Packets.MessageFactory import *
from Logic.Device import Device
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os


class ServerThread():
    def __init__(self, ip, port):
        self.address = str(ip)
        self.port = int(port)
        self.client = socket.socket()

    def start(self):
        self.client.bind((self.address, self.port))

        print('[*] Server is listening on {}:{}'.format(self.address, self.port))
        print("[*] Let's play HayDay!")

        while True:
            self.client.listen(5)
            client, address = self.client.accept()

            print("[*] New connection from {}".format(address[0]))
            clientThread = ClientThread(client).start()


class ClientThread(Thread):
    def __init__(self, client):
        Thread.__init__(self)

        self.client = client
        self.device = Device(self.client)

    def recvall(self, size, timeout=5.0):
        data = []
        while size > 0:
            self.client.settimeout(timeout)
            s = self.client.recv(size)
            self.client.settimeout(None)
            if not s:
                raise EOFError
            data.append(s)
            size -= len(s)
        return b''.join(data)

    def run(self):
        try:
            self.loop()
        except (EOFError, OSError):
            pass
        finally:
            self.client.close()
            print('[*] Client disconnected')

    def loop(self):
        while True:
            header   = self.recvall(7, None)
            packetid = int.from_bytes(header[:2], 'big')
            length   = int.from_bytes(header[2:5], 'big')
            version  = int.from_bytes(header[5:], 'big')
            data     = self.recvall(length)

            if len(header) >= 7:
                if length == len(data):
                    print("[*] {} received".format(packetid))

                    try:
                        decrypted = self.device.decrypt(data)
                        if packetid in availablePackets:

                            Message = availablePackets[packetid](decrypted, self.device)

                            Message.decode()
                            Message.process()

                        else:
                            print("[*] {} not handled, payload: {}".format(packetid, decrypted.hex()))  # hex for reversing

                    except:
                            print('[*] Error while decrypting / handling {}'.format(packetid))
                            traceback.print_exc()
                else:
                    print('[*] Incorrect Length for packet {} (header length: {}, data length: {})'.format(packetid, length, len(data)))
            else:
                print('[*] Received an invalid packet from client')
                return
            
class EnvHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        c = json.load(open("config.json"))
        body = json.dumps({
            "environment": "maintenance" if c["Maintenance"] else c["Environment"],
            "serverHost": c["Host"],
            "assetUrl": "http://{}:{}/assets/".format(c["Host"], c["HttpPort"]),
            "updateUrl": "",
            "status": "ok",
        }).encode()
        print('[HTTP] GET {}'.format(self.path))
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    conf = json.load(open("config.json"))
    port = int(os.environ.get('HAYDAY_PORT', conf["Port"]))
    http_port = int(os.environ.get('HAYDAY_HTTP_PORT', conf["HttpPort"]))
    Thread(target=ThreadingHTTPServer(("0.0.0.0", http_port), EnvHandler).serve_forever, daemon=True).start()
    server = ServerThread("0.0.0.0", port)
    server.start()
