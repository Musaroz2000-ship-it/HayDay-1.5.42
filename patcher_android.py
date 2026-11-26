"""Patch the Hay Day APK to point at a local server.

Usage: python3 patcher_android.py [in.apk] [out.apk] [host] [port]

Defaults: the first *.apk in this folder or the parent, gamepatched.apk,
host 127.0.0.1, port 8080. Removes the old signature (META-INF); sign the
result with MT Manager or similar before installing.
"""
import glob
import os
import re
import sys
import zipfile

URL = re.compile(rb'http://[^\x00/]+/+env_settings\?[^\x00]*')


def patch_bytes(data, origin):
    count = 0

    def sub(m):
        nonlocal count
        old = m.group(0)
        tail = old[old.index(b'env_settings'):]
        pad = len(old) - len(origin) - len(tail)
        if pad < 1:
            return old
        count += 1
        return origin + b'/' * pad + tail

    return URL.sub(sub, data), count


def main():
    args = sys.argv[1:]
    if args:
        src = args[0]
    else:
        candidates = glob.glob('*.apk') + glob.glob('../*.apk')
        if not candidates:
            sys.exit('no .apk found, pass one: python3 patcher_android.py <in.apk>')
        src = candidates[0]
    dst = args[1] if len(args) > 1 else 'gamepatched.apk'
    host = args[2] if len(args) > 2 else '127.0.0.1'
    port = args[3] if len(args) > 3 else '8080'
    origin = 'http://{}:{}'.format(host, port).encode()

    total = 0
    touched = []
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zo:
        for info in zi.infolist():
            name = info.filename
            if name.startswith('META-INF/') and (name.endswith('.SF') or name.endswith('.RSA') or name.endswith('.DSA') or name.endswith('.MF')):
                continue
            data = zi.read(name)
            if not name.endswith('.xml') and not name.endswith('.png') and not name.endswith('.jpg'):
                data, n = patch_bytes(data, origin)
                if n:
                    total += n
                    touched.append((name, n))
            zo.writestr(info, data)

    for name, n in touched:
        print('patched {} in {}'.format(n, name))
    if total != 3:
        print('WARNING: expected 3 URLs, patched {}'.format(total))
        if total == 0:
            sys.exit('no env_settings URLs found in {}'.format(src))
    print('apk:', dst)


if __name__ == '__main__':
    main()
