from Utils.Writer import Writer


class LoginOkMessage(Writer):

    def __init__(self, device):
        super().__init__(device)
        self.device = device
        self.id = 20104

    def encode(self):
        p = self.device.player
        for _ in range(3):
            self.writeInt(p.high); self.writeInt(p.low)
        self.writeString(p.passToken)
        self.writeString()  # facebookId
        self.writeString()  # gameCenterId
        self.writeInt(1)    # sessionCount
        self.writeInt(0)    # playTimeSeconds
        self.writeInt(0)    # unknown
