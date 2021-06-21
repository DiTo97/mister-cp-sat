import argparse
import itertools as it
import json
import pathlib

from typing import Dict
from typing import List
from typing import Tuple

# Custom imports
from mister.constants import *
from mister.errors import *

from mister.manager import Manager

from mister.formation import Formation
from mister.player import Player
from mister.team import Team

def main(_players: List[str], n: int,
         _formation: str, nteams: int = 2) \
        -> List[str]:
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
    _players : List[str]
        Encoded players as string: "{name}-{rating}-{position}"

    n : int
        Number of players per team

    _formation : str
        Encoded formation as string: "{D}-{M}-{F}"

    nteams : int
        Number of teams. The default is 2

    Returns
    -------
    List[str]
        Encoded teams as string.
    """
    # Deserialize the formation
    formation = Formation.deserialize(_formation)

    # Deserialize the players
    players = [Player.deserialize(p)
               for p in _players]

    _check_valid(players, n, formation, nteams)

    # Solve the SAT problem
    teams = Manager.make_teams(
        players, formation)

    # Serialize the teams
    if not teams:
        return []

    return [t.serialize() for t in teams]


def _check_valid(players: List[Player], n: int,
                 formation: Formation, nteams: int):
    players.sort(key=lambda p: p.position)

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

    # V3. Check whether there are enough players
    # for all the teams with that formation
    for k, g in it.groupby(players,
                           lambda p: p.position):
        ngiven = len(list(g))
        nvalid = nteams*formation \
                        .__dict__[k.name]

        if ngiven > nvalid:
            raise TooManyPlayersError(
                ngiven, formation, k, nteams)

        if ngiven < nvalid:
            raise NotEnoughPlayersError(
                ngiven, formation, k, nteams)

def _load_scenario_conf(dirpath: pathlib.Path) \
                       -> Tuple[List[str], int, str, int]:
    # Load the scenario conf JSON
    with open(str(dirpath / Filenames['CONF'])) as jfh:
        scenario_conf = json.load(jfh)

    return scenario_conf['players'],   \
           scenario_conf['n'],         \
           scenario_conf['formation'], \
           scenario_conf['nteams']


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

    # Load the scenario conf
    scenario_conf = _load_scenario_conf(conf_dirpath)

    # Read all conf params
    _players = scenario_conf[0]
    n = scenario_conf[1]
    _formation = scenario_conf[2]
    nteams = scenario_conf[3]

    # Solve the SAT problem
    _teams = main(_players, n,
                  _formation, nteams)

    if not _teams:
        raise NoSolutionError()

    # Store the solution JSON
    solution_path = conf_dirpath / Filenames['SOLU']

    with open(str(solution_path), 'w') as jfh:
        json.dump(_teams, jfh, indent=4)
