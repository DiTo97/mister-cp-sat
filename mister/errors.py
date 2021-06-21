# Custom imports
from mister.formation import Formation
from mister.position import Position


class _BaseException(Exception):
    message: str

    def __repr__(self) -> str:
        return self.message


class DuplicatePlayersError(_BaseException):
    def __init__(self):
        self.message = 'All the players need a unique name as Id.'

        super().__init__(self.message)


class InvalidFormationError(_BaseException):
    def __init__(self, n: int,
                 formation: Formation):
        """
        Parameters
        ----------
        n : int
            Number of players per team

        formation : Formation
            Formation of interest
        """
        self.message = 'Invalid formation {} cannot satisfy ' \
                       'a {}-a-side football pitch.'          \
                           .format(formation, n)

        super().__init__(self.message)


class NoSolutionError(_BaseException):
    def __init__(self):
        self.message = 'No solution was found.'

        super().__init__(self.message)


class NotEnoughPlayersError(_BaseException):
    def __init__(self, n: int, formation: Formation,
                 position: Position, nteams: int):
        """
        Parameters
        ----------
        n : int
            Number of available players for that position

        formation : Formation
            Formation of interest

        position : Position
            Position of interest

        nteams : int
            Number of teams
        """
        nvalid = nteams*formation \
                        .__dict__[position.name]

        self.message = 'Given {} {}. Expected {} for ' \
                       '{} teams with a {} formation.' \
                           .format(n, position.fullform(plura=True),
                                   nvalid, nteams, formation)

        super().__init__(self.message)


class TooManyPlayersError(_BaseException):
    def __init__(self, n: int, formation: Formation,
                 position: Position, nteams: int):
        """
        Parameters
        ----------
        n : int
            Number of available players for that position

        formation : Formation
            Formation of interest

        position : Position
            Position of interest

        nteams : int
            Number of teams
        """
        nvalid = nteams*formation \
                        .__dict__[position.name]

        self.message = 'Given {} {}. Expected {} for '   \
                       '{} teams with a {} formation. '  \
                       'The SAT model does not account ' \
                       'for reserves as of yet.'         \
                           .format(n, position.fullform(plura=True),
                                   nvalid, nteams, formation)

        super().__init__(self.message)
