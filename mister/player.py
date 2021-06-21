import typing as t

# Custom imports
from mister.position import Position
from mister.serializable import DictSerializable


class Player(DictSerializable):
    def __init__(self, name: str, rating: int,
                 position: t.Union[str, Position]):
        self.name = name
        self.rating = rating

        if isinstance(position, str):
            position = Position(position)

        self.position = position

    @staticmethod
    def deserialize(encoding: t.Dict) \
                   -> 'Player':
        name = encoding['name']
        position = encoding['position']
        rating = encoding['rating']
        
        return Player(name,
                      int(rating),
                      position)
