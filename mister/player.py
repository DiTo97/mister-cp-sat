from typing import Union

# Custom imports
from mister.position import Position
from mister.serializable import Serializable


class Player(Serializable):
    def __init__(self, name: str, rating: int,
                 position: Union[str, Position]):
        self.name = name
        self.rating = rating

        if isinstance(position, str):
            position = Position(position)

        self.position = position

    def serialize(self,
                  delimiter: str = ',') \
                 -> str:
        return super().serialize(delimiter)

    @staticmethod
    def deserialize(econding: str,
                    delimiter: str = ',') \
                   -> 'Player':
        name, rating, position = econding.split(delimiter)
        
        return Player(name,
                      int(rating),
                      position)
