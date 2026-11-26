from Utils.Reader import Reader


class ChangeAccountSettingsMessage(Reader):

    def __init__(self, data, device):
        super().__init__(data)
        self.device = device

    def decode(self):
        print('[*] change account settings payload: {}'.format(self.buffer.hex()))

    def process(self):
        pass
