from mister.serializable import Serializable
from typing import Dict
from typing import List

# Custom imports
from mister.player import Player
from mister.serializable import Serializable


class Team(Serializable):
    def __init__(self, id: int):
        self.id = id
        self.players = []

    def add(self, player: Player):
        self.players.append(player)
   
    @property
    def rating(self) -> int:
        return sum([p.rating for p
                   in self.players])

    def serialize(self,
                  delimiter: str = '-') \
                 -> str:
        return delimiter.join([str(self.id)]
            + [p.serialize() for p
               in self.players])

    @staticmethod
    def deserialize(econding: str,
                    delimiter: str = '-') \
                   -> 'Team':
        raise NotImplementedError()

    @staticmethod
    def from_associations(players_per_tid, cpsolver) \
                         -> List['Team']:
        """
        Generate teams from players per team Id associations.

        Parameters
        ----------
        players_per_tid : Dict[Tuple[Player, int]]
            Players per team Id associations

        cpsolver : Any
            CP solver that implements BooleanValue()
        """
        _teams = {}

        for ptid, v in players_per_tid.items():
            if cpsolver.BooleanValue(v):
                p, tid = ptid

                if tid not in _teams:
                    _teams[tid] = Team(tid)

                _teams[tid].add(p)

        return list(_teams.values())
