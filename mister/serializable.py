import collections
import typing as t

from abc import ABC
from abc import abstractmethod

from collections import Iterable


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
                   -> t.Type['Serializable']:
        raise NotImplementedError()

class DictSerializable(Serializable):
    def serialize(self) \
                 -> t.Dict:
        _D = self.__dict__

        for k, v in _D.items():
            if (isinstance(v, Serializable)):
                _D[k] = v.serialize()
            elif (isinstance(v, type([]))):
                _D[k] = [o if not isinstance(o, Serializable)
                           else o.serialize() for o in v]

        return _D

    @staticmethod
    @abstractmethod
    def deserialize(encoding: t.Dict) \
                   -> t.Type['Serializable']:
        raise NotImplementedError()
