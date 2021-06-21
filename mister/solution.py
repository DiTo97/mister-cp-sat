import typing as t

# Custom imports
from mister.serializable import DictSerializable
from mister.team import Team

class Solution(DictSerializable):
    balance: float
    teams: t.List[Team]

    def __init__(self, balance: float,
                 teams: t.List[Team]):
        self.balance = round(balance, 3)
        self.teams = teams

    @staticmethod
    def create(objvalue: int,
               avgrating: int,
               teams: t.List[Team]) \
              -> 'Solution':
        balance = 1.*(avgrating - objvalue) \
                    / avgrating

        return Solution(balance, teams)

    @staticmethod
    def deserialize(encoding: t.Dict) \
                   -> 'Solution':
        raise NotImplementedError()
