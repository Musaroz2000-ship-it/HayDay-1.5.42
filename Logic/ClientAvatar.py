from Logic.GameData import BITLIST_TABLES, GameData


class LogicClientAvatar:
    def __init__(self, player):
        self.player = player
        self.data = GameData()

    def encode(self, w):
        p = self.player
        w.writeInt(p.high); w.writeInt(p.low)

        res = []
        for name, value in p.money.items():
            if not value:
                continue
            gid = self.data.gid(19, name)
            if gid is not None:
                res.append((gid, value))
        w.writeInt(len(res), 2)
        for gid, value in res:
            w.writeInt(gid); w.writeInt(value)

        for tid in BITLIST_TABLES:
            n = self.data.count(tid)
            bits = p.bits.get(tid, [])
            words = [0] * ((n + 31) // 32)
            for i in range(min(len(bits), n)):
                if bits[i]:
                    words[i >> 5] |= 1 << (i & 31)
            for x in words:
                w.writeInt(x)

        w.writeInt(0, 2)  # roadside shop
        w.writeString(p.name)  # name
        w.writeInt(0)  # mail
        w.writeInt(0)  # new shop items
        w.writeInt(0)  # shared boat crates
