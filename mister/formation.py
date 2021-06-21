# Custom imports
from mister.serializable import Serializable


class Formation(Serializable):
    def __init__(self, D: int, M: int, F: int):
        """
        Parameters
        ----------
        D : int
            Number of defenders

        M : int
            Number of midfielders

        F : int
            Number of forwards
        """
        self.D = D
        self.M = M
        self.F = F

    @property
    def nplayers(self):
        return self.D + self.M + self.F

    @staticmethod
    def deserialize(econding: str,
                    delimiter: str = '-') \
                   -> 'Formation':
        D, M, F = econding.split(delimiter)
        
        return Formation(int(D),
                         int(M),
                         int(F))
