import json
import os
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from CryptoRC4.Crypto import KEY  # noqa: E402
from Crypto.Cipher import ARC4 as RC4  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 19391
HTTP_PORT = 18091


def recv_exact(s, size):
    data = b''
    while len(data) < size:
        chunk = s.recv(size - len(data))
        if not chunk:
            raise EOFError
        data += chunk
    return data


def recv_message(s):
    header = recv_exact(s, 7)
    pid = int.from_bytes(header[:2], 'big')
    length = int.from_bytes(header[2:5], 'big')
    return pid, recv_exact(s, length)


def send_message(s, pid, payload=b''):
    s.sendall(pid.to_bytes(2, 'big') + len(payload).to_bytes(3, 'big') + (0).to_bytes(2, 'big') + payload)


def read_string(buf, off):
    n = int.from_bytes(buf[off:off + 4], 'big')
    off += 4
    return buf[off:off + n], off + n


def connect_and_login(account_id, token=b'e2e-token'):
    s = socket.create_connection(('127.0.0.1', PORT), timeout=10)
    send_message(s, 10122)
    pid, data = recv_message(s)
    assert pid == 20122, 'expected SecureConnectionOk, got {}'.format(pid)
    nonce, _ = read_string(data, 0)

    key = KEY + nonce
    enc = RC4.new(key); enc.encrypt(b'\0' * len(key))
    dec = RC4.new(key); dec.encrypt(b'\0' * len(key))

    payload = account_id.to_bytes(8, 'big')
    payload += len(token).to_bytes(4, 'big') + token
    payload += len(b'').to_bytes(4, 'big')
    send_message(s, 10101, enc.encrypt(payload))
    pid, data = recv_message(s)
    assert pid == 20104, 'expected LoginOk, got {}'.format(pid)
    d = dec.encrypt(data)
    high = int.from_bytes(d[0:4], 'big')
    low = int.from_bytes(d[4:8], 'big')
    echoed, _ = read_string(d, 24)
    assert (high << 32) | low == account_id, 'echoed id {} != {}'.format((high << 32) | low, account_id)
    assert echoed == token, 'echoed token mismatch'

    send_message(s, 14101, enc.encrypt(b''))
    pid, data = recv_message(s)
    assert pid == 24101, 'expected OwnHomeData, got {}'.format(pid)
    assert len(data) > 1000, 'OwnHomeData too small'

    turn = (7).to_bytes(4, 'big') + (123).to_bytes(4, 'big') + b'\x01\x02\x03'
    send_message(s, 14102, enc.encrypt(turn))
    pid, data = recv_message(s)
    assert pid == 24112, 'expected EndClientTurnOk, got {}'.format(pid)

    import urllib.request
    body = json.loads(urllib.request.urlopen('http://127.0.0.1:{}/env_settings'.format(HTTP_PORT)).read())
    assert body['status'] == 'ok'

    s.close()
    return high, low


def main():
    env = dict(os.environ, HAYDAY_PORT=str(PORT), HAYDAY_HTTP_PORT=str(HTTP_PORT))
    server = subprocess.Popen([sys.executable, 'Main.py'], cwd=REPO, env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                probe = socket.create_connection(('127.0.0.1', PORT), timeout=1)
                probe.close()
                break
            except OSError:
                time.sleep(0.2)
        else:
            raise RuntimeError('server did not start')

        high, low = connect_and_login(1)
        assert os.path.exists(os.path.join(REPO, 'Database', '{}_{}.json'.format(high, low)))
        print('[PASS] first login, farm, turn, persistence file {}.{}'.format(high, low))

        connect_and_login(2)
        assert os.path.exists(os.path.join(REPO, 'Database', '0_2.json'))
        print('[PASS] second account got its own file')

        print('ALL TESTS PASSED')
    finally:
        server.kill()
        server.wait()
        for name in ('0_1.json', '0_2.json'):
            path = os.path.join(REPO, 'Database', name)
            if os.path.exists(path):
                os.remove(path)


if __name__ == '__main__':
    main()
