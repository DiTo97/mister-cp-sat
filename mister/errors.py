# Custom imports
from mister.formation import Formation
from mister.position import Position


class DuplicatePlayersError(Exception):
    def __init__(self, *args, **kwargs):
        errmsg = 'All the players need a unique name as Id.'

        super().__init__(errmsg, *args, **kwargs)


class InvalidFormationError(Exception):
    def __init__(self, n: int,
                 formation: Formation,
                 *args, **kwargs):
        """
        Parameters
        ----------
        n : int
            Number of players per team

        formation : Formation
            Formation of interest
        """
        errmsg = 'Invalid formation {} cannot satisfy ' \
                 'a {}-a-side football pitch.'          \
                     .format(formation, n)

        super().__init__(errmsg, *args, **kwargs)


class NoSolutionError(Exception):
    def __init__(self, *args, **kwargs):
        errmsg = 'No solution was found.'

        super().__init__(errmsg, *args, **kwargs)


class NotEnoughPlayersError(Exception):
    def __init__(self, n: int, formation: Formation,
                 position: Position, nteams: int,
                 *args, **kwargs):
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

        errmsg = 'Given {} {}. Expected {} for ' \
                 '{} teams with a {} formation.' \
                     .format(n, position.fullform(plura=True),
                             nvalid, nteams, formation)

        super().__init__(errmsg, *args, **kwargs)


class TooManyPlayersError(Exception):
    def __init__(self, n: int, formation: Formation,
                 position: Position, nteams: int,
                 *args, **kwargs):
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

        errmsg = 'Given {} {}. Expected {} for '   \
                 '{} teams with a {} formation. '  \
                 'The SAT model does not account ' \
                 'for reserves as of yet.'         \
                     .format(n, position.fullform(plura=True),
                             nvalid, nteams, formation)

        super().__init__(errmsg, *args, **kwargs)
