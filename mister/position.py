from enum import Enum


class Position(str, Enum):
    D = 'D',
    M = 'M',
    F = 'F',

    def __str__(self):
        return str(self.value)

    def fullform(self,
                 plura: bool = False,
                 upper: bool = False) -> str:
        """
        Adjust the position's fullform.

        Parameters
        ----------
        plura : bool
            Whether to make the fullform plural.
            The default is True.

        upper : bool
            Whether to make the fullform upper case.
            The default is False.
        """
        pos = _Fullforms[self]
        pos += 's' if plura else ''

        return pos.capitalize() \
            if upper else pos

_Fullforms = {
    Position.D : 'defender',
    Position.M : 'midfielder',
    Position.F : 'forward',
}
