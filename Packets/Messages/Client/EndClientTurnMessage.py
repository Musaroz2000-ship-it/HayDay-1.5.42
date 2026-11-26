from Utils.Reader import Reader
from Packets.Messages.Server.EndClientTurnOkMessage import EndClientTurnOkMessage


class EndClientTurnMessage(Reader):

    def __init__(self, data, device):
        super().__init__(data)
        self.device = device

    def decode(self):
        try:
            self.turn = self.readInt()
            self.time = self.readInt()
            self.commands = self.buffer[self.i:]
            print('[*] turn {} ({} command bytes)'.format(self.turn, len(self.commands)))
        except Exception:
            self.commands = b''

    def process(self):
        EndClientTurnOkMessage(self.device).Send()
