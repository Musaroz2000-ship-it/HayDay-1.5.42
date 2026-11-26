try:
    from Crypto.Cipher import ARC4 as RC4
except ImportError:
    class _StreamCipher:
        def __init__(self, key):
            s = list(range(256))
            j = 0
            for i in range(256):
                j = (j + s[i] + key[i % len(key)]) & 0xFF
                s[i], s[j] = s[j], s[i]
            self.s = s
            self.i = 0
            self.j = 0

        def encrypt(self, data):
            s, i, j = self.s, self.i, self.j
            out = bytearray()
            for b in data:
                i = (i + 1) & 0xFF
                j = (j + s[i]) & 0xFF
                s[i], s[j] = s[j], s[i]
                out.append(b ^ s[(s[i] + s[j]) & 0xFF])
            self.i, self.j = i, j
            return bytes(out)

        decrypt = encrypt

    class RC4:
        @staticmethod
        def new(key):
            return _StreamCipher(key)


KEY = b'gWZW0tm9Elv78dX6kX1ew3FB837yc2CSaVLlTjei4hW0'


class CryptoRc4:
    def __init__(self, nonce: bytes):
        k = KEY + nonce
        self.rx = RC4.new(k)
        self.rx.encrypt(b'\0' * len(k))
        self.tx = RC4.new(k)
        self.tx.encrypt(b'\0' * len(k))

    def decrypt(self, data):
        return self.rx.encrypt(data)

    def encrypt(self, data):
        return self.tx.encrypt(data)
