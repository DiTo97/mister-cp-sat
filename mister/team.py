import typing as t

from ortools.sat.python import cp_model

# Custom imports
from mister.player import Player
from mister.serializable import DictSerializable


class Team(DictSerializable):
    def __init__(self, id: int):
        self.id = id
        self.players = []

    def add(self, player: Player):
        self.players.append(player)
   
    @property
    def rating(self) -> int:
        return sum([p.rating for p
                   in self.players])

    @staticmethod
    def deserialize(encoding: t.Dict) \
                   -> 'Team':
        raise NotImplementedError()

    @staticmethod
    def from_associations(players_per_tid: 
                              t.Dict[t.Tuple[Player, int],
                                     cp_model.IntVar],
                          cpsolver) -> t.List['Team']:
        """
        Generate teams from players per team Id associations.

        Parameters
        ----------
        players_per_tid : Dict[Tuple[Player, int]]
            Players per team Id associations

        cpsolver : Any
            CP solver that implements BooleanValue()
        """
        _T = {}

        for ptid, v in players_per_tid.items():
            if cpsolver.BooleanValue(v):
                p, tid = ptid

                if tid not in _T:
                    _T[tid] = Team(tid)

                _T[tid].add(p)

        return list(_T.values())
