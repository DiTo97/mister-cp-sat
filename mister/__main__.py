import argparse
import itertools as it
import json
import pathlib
import typing as t

# Custom imports
from mister.constants import *
from mister.errors import *
from mister.formation import Formation
from mister.manager import Manager
from mister.player import Player
from mister.types import *

    
def fromjson(scenario_conf: JSON) \
            -> JSON:
    """
    Generate N equally matched football teams from JSON scenario conf.

    Parameters
    ----------
    scenario_conf: JSON
        Encoded scenario conf as JSON
    """
    # Mandatory parameters
    n = int(scenario_conf['n'])
    nteams = int(scenario_conf['nteams'])
    _players = scenario_conf['players']

    # Optional parameters
    _formation = None
    optimal = False

    if 'formation' in scenario_conf:
        _formation = scenario_conf['formation']

    if 'optimal' in scenario_conf:
        optimal = str2bool(
            scenario_conf['optimal']
            )

    return main(n, nteams, _players,
                _formation, optimal)

def main(n: int, nteams: int,
         _players: t.List[JSON],
         _formation: str = None,
         optimal: bool = False) -> JSON:
    """
    Generate N equally matched football teams given a list of players, the group size n of
    an n-a-side football pitch, with n being either 5, 6, or 7, the formation and the number of teams N.

    Each player has a name, a position and a rating. The position can either be F, for Forward, M, for Midfielder,
    and D, for Defender, while there's no signature letter for Goalkeepers as, granted a relatively small football pitch,
    they are assumed to be either flying or rotating between the players; the rating, instead, is between 0 and 100.  
    
    The objective is to construct N groups whose sum of ratings is as close to the average as possible.
    Furthermore, depending on the group size n, a certain number of positions have to be covered, say k_i,
    with i being either F, M, or D, such that at least k players of the i-th position are in each group.

    Parameters
    ----------
    n : int
        Number of players per team

    nteams : int
        Number of teams

    _players : JSON
        Encoded players as JSON

    _formation : str
        Encoded formation as string: "{D}-{M}-{F}". The default is None.

    optimal : bool
        Whether to return the optimal solution. The default is False.

    Returns
    -------
    JSON
        Encoded teams as JSON.
    """
    # Deserialize the formation
    formation = Formation.deserialize(_formation) \
                if _formation is not None else None

    # Deserialize the players
    players = [Player.deserialize(p)
               for p in _players]

    _check_valid(n, nteams, players, formation)

    # Solve the SAT problem
    return Manager.make_teams(
        n, players, formation, optimal) \
                  .serialize()

def _check_valid(n: int, nteams: int,
                 players: t.List[Player],
                 formation: Formation):
    players.sort(key=lambda p: p.position)

    if formation is not None:
        # V1. Check whether the formation has
        # the right number of players n
        if n != formation.nplayers:
            raise InvalidFormationError(n, formation)

    # V2. Check whether all the players
    # have a unique name as Id
    players_names = [p.name for p in players]
    players_names_unique = set(players_names)

    if len(players_names_unique) \
            != len(players_names):
        raise DuplicatePlayersError()

    if formation is not None:
        # V3. Check whether there are enough players
        # for all the teams with that formation
        players_per_position = {
            k: len(list(g)) for k, g
                            in it.groupby(players,
                                lambda p: p.position)
                            }

        for k in Position:
            if k not in players_per_position.keys():
                raise NotEnoughPlayersError(
                    0, formation, k, nteams)

            ngiven = players_per_position[k]
            nvalid = nteams*formation \
                            .__dict__[k.name]

            if ngiven > nvalid:
                raise TooManyPlayersError(
                    ngiven, formation, k, nteams)

            if ngiven < nvalid:
                raise NotEnoughPlayersError(
                    ngiven, formation, k, nteams)

    if formation is None:
        # V4. Check whether there are enough players
        # for all the teams with an an n-a-side pitch.
        if not (len(players) == n*nteams):
            raise NotEnoughTotalPlayersError(
                            len(players), n, nteams)

    # V5. Check whether all the players have
    # a rating within the desired boundaries
    for p in players:
        if p.rating < Ratings['MIN']:
            raise InvalidRatingError()

        if p.rating > Ratings['MAX']:
            raise InvalidRatingError()

def _load_scenario_conf(dirpath: pathlib.Path) \
                       -> JSON:
    # Load the scenario conf JSON
    with open(str(dirpath / Filenames['CONF'])) as jfh:
        scenario_conf = json.load(jfh)

    return scenario_conf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        'conf_dirpath',
        help='Name of the configuration folder'
    )

    args = parser.parse_args()

    conf_dirpath = pathlib.Path(
        args.conf_dirpath).absolute()

    solution_path = conf_dirpath \
                        / Filenames['SOLU']

    # Load the JSON scenario conf
    scenario_conf = _load_scenario_conf(conf_dirpath)

    # Solve the SAT problem
    # and store the solution JSON
    with open(str(solution_path), 'w') as jfh:
        json.dump(fromjson(scenario_conf),
                  jfh, indent=4)
