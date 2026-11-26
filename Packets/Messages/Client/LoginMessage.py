import json
from Utils.Reader import Reader
from Packets.Messages.Server.LoginOkMessage import LoginOkMessage
from Packets.Messages.Server.LoginFailedMessage import LoginFailedMessage
from Logic.Player import Player


class LoginMessage(Reader):

    def __init__(self, data, device):
        super().__init__(data)
        self.device = device

    def decode(self):
        try:
            self.accountId = self.readInt(8)
            self.passToken = self.readString()
            self.resourceSha = self.readString()
            print('[*] login id={} sha={}'.format(self.accountId, self.resourceSha))
        except Exception:
            self.accountId = 0
            self.passToken = ''

    def process(self):
        config = json.load(open("config.json"))
        if config.get("Maintenance"):
            LoginFailedMessage(self.device, 10, "Maintenance").Send()
            return

        account = getattr(self, 'accountId', 0) or 0
        high = account >> 32 if account else config['AccountHighID']
        if not high:
            high = config['AccountHighID']
        low = account & 0xFFFFFFFF if account else Player.next_low(high, config)

        player = Player.load(high, low)
        if player is None:
            player = Player.create(config, high, low)
            print('[*] created new account {} ({}.{})'.format(player.name, player.high, player.low))
        else:
            print('[*] loaded account {} ({}.{})'.format(player.name, player.high, player.low))

        if getattr(self, 'passToken', ''):
            player.passToken = self.passToken
            player.save()

        self.device.player = player
        LoginOkMessage(self.device).Send()
