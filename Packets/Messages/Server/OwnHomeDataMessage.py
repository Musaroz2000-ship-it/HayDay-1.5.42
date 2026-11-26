from Utils.Writer import Writer
from Logic.ClientAvatar import LogicClientAvatar


class OwnHomeDataMessage(Writer):

    def __init__(self, device):
        super().__init__(device)
        self.device = device
        self.id = 24101

    def encode(self):
        player = self.device.player
        self.writeInt(0)  # startTime
        self.writeString(player.home)  # farm
        LogicClientAvatar(player).encode(self)
        self.writeInt(0)
