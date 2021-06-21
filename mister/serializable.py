from abc import ABC
from abc import abstractmethod

from typing import Type


class Serializable(ABC):
    def __str__(self):
        return self.serialize()

    def serialize(self,
                  delimiter: str = '-') \
                 -> str:
        return delimiter.join(
            [str(s) for s in
             self.__dict__.values()])

    @staticmethod
    @abstractmethod
    def deserialize(encoding: str,
                    delimiter: str = '-') \
                   -> Type['Serializable']:
        raise NotImplementedError()
