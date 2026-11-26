import json
import os
from Logic.GameData import GameData


class Player:
    DIRECTORY = 'Database'

    def __init__(self, high, low):
        self.high = int(high)
        self.low = int(low)
        self.passToken = ''
        self.name = 'Farmer'
        self.money = {'Diamonds': 0, 'Cash': 0, 'ExpLevel': 1, 'ExpPoints': 0}
        self.bits = {}
        self.home = ''

    @property
    def id(self):
        return (self.high << 32) | self.low

    @classmethod
    def path(cls, high, low):
        return os.path.join(cls.DIRECTORY, '{}_{}.json'.format(high, low))

    @classmethod
    def load(cls, high, low):
        path = cls.path(high, low)
        if not os.path.exists(path):
            return None
        with open(path) as f:
            state = json.load(f)
        player = cls(state['high'], state['low'])
        player.passToken = state.get('passToken', '')
        player.name = state.get('name', 'Farmer')
        player.money = state.get('money', player.money)
        player.bits = {int(tid): values for tid, values in state.get('bits', {}).items()}
        player.home = state.get('home', '')
        return player

    @classmethod
    def create(cls, config):
        data = GameData()
        tutorialTable = config.get('TutorialTable', 36)
        player = cls(config['AccountHighID'], config['AccountLowID'])
        player.passToken = config.get('PassToken', '')
        player.name = config.get('Name', 'Farmer')
        player.money = {
            'Diamonds': config.get('Diamonds', 0),
            'Cash': config.get('Cash', 0),
            'ExpLevel': config.get('ExpLevel', 1),
            'ExpPoints': config.get('ExpPoints', 0),
        }
        if config.get('SkipTutorial'):
            player.bits[tutorialTable] = [1] * data.count(tutorialTable)
        with open(config.get('HomeFile', 'JSON/home.json')) as f:
            player.home = f.read()
        return player

    def save(self):
        os.makedirs(self.DIRECTORY, exist_ok=True)
        state = {
            'high': self.high,
            'low': self.low,
            'passToken': self.passToken,
            'name': self.name,
            'money': self.money,
            'bits': {str(tid): values for tid, values in self.bits.items()},
            'home': self.home,
        }
        with open(self.path(self.high, self.low), 'w') as f:
            json.dump(state, f)
