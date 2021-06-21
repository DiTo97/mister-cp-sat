import typing as t

# Custom imports
from mister.serializable import DictSerializable
from mister.team import Team

class Solution(DictSerializable):
    N: int
    balance: float
    teams: t.List[Team]

    def __init__(self, N: int,
                 balance: float,
                 teams: t.List[Team]):
        self.N = N
        self.balance = round(balance, 3)
        self.teams = teams

    @staticmethod
    def create(objvalue: int,
               avgrating: int,
               teams: t.List[Team]) \
              -> 'Solution':
        N = len(teams)
        balance = 1.*(avgrating - objvalue) \
                    / avgrating

        return Solution(N, balance, teams)

    @staticmethod
    def deserialize(encoding: t.Dict) \
                   -> 'Solution':
        raise NotImplementedError()
