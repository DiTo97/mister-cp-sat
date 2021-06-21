import itertools as it
import typing as t

from ortools.sat.python import cp_model

# Custom imports
from mister.errors import NoSolutionError
from mister.formation import Formation
from mister.player import Player
from mister.position import Position
from mister.solution import Solution
from mister.team import Team


def _npositions():
    return len(Position)


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """
    Intermediate solutions printer.
    """
    def __init__(self, players_per_tid: t.Dict[t.Tuple[Player, int],
                                               cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)

        self.__nsolutions = 0
        self.__players_per_tid = players_per_tid

    def on_solution_callback(self):
        print('\nSolution %i with:' % self.__nsolutions)
        self.__nsolutions += 1

        print('    Objective value = %i\n'
              % self.ObjectiveValue())

        # Print each team's info
        for t in Team.from_associations(
                self.__players_per_tid, self):
            print('    Team %i with rating = %i [\n' %
                (t.id, t.rating), end='')

            for p in t.players:
                print('        (%s,%s,%s)\n' %
                    (p.name, p.rating, p.position), end='')

            print('    ]')

    @property
    def nsolutions(self):
        return self.__nsolutions

class Manager:
    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def make_teams(players: t.List[Player],
                   formation: Formation) \
                  -> Solution:
        n = formation.nplayers

        nplayers = len(players)
        nteams = nplayers // n
        npositions = _npositions()

        teams_ids = range(nteams)

        #
        # Group all players by position
        #

        players.sort(key=lambda p: p.position)

        players_per_position = {}

        for k, g in it.groupby(players,
                               lambda p: p.position):
            players_per_position[k] = list(g)

        #
        # Extract metrics by rating
        #

        players.sort(key=lambda p: p.rating)

        players_top_n  = players[-nteams:]
        players_flop_n = players[:nteams]

        tot_ratings = sum([p.rating for p
                           in players])

        avg_rating_per_team = tot_ratings//nteams

        print('CP model has %i players, %i teams, '
              'and %i positions with:'
              % (nplayers, nteams, npositions))

        print('    Average rating per team = %i'
              % avg_rating_per_team)

        # Create a constant programming SAT solver
        model = cp_model.CpModel()

        #
        # Create SAT constraints
        #

        players_per_tid = {} # Players per team Id associations

        for p in players:
            for tid in teams_ids:
                players_per_tid[(p, tid)] = model.NewBoolVar(
                    'Player %s in team %d' % (p.name, tid))

        # Objective function to minimize:
        # epsilon := Rating deviation of each
        #            team from the average
        e = model.NewIntVar(0, 100, 'epsilon')

        # C1. Each team must have the same size.
        for tid in teams_ids:
            model.Add(sum(players_per_tid[(p, tid)]
                          for p in players) == n)

        # C2. One player must belong exactly to one team.
        for p in players:
            model.Add(sum(players_per_tid[(p, tid)]
                          for tid in teams_ids) == 1)

        # C3. Each team's rating has to be around
        # the average rating. It means in the range:
        # [-epsilon + avg, avg + epsilon]
        for tid in teams_ids:
            trating = sum(players_per_tid[(p, tid)]
                              *p.rating
                          for p in players)

            model.Add(trating >= avg_rating_per_team - e)
            model.Add(trating <= avg_rating_per_team + e)

        # C4. Each team must have a fixed number of players
        # per position as stated in the formation.
        for k in Position:
            for tid in teams_ids:
                model.Add(sum(players_per_tid[(p, tid)]
                              for p in players
                              if p.position == k)
                          == formation.__dict__[k.name])

        # C5. One team cannot have more than one
        # of the Nteams highest-rated players.
        for tid in teams_ids:
            model.Add(sum(players_per_tid[(p, tid)]
                          for p in players_top_n) == 1)

        # C6. One team cannot have more than one
        # of the Nteams lowest-rated players.
        for tid in teams_ids:
            model.Add(sum(players_per_tid[(p, tid)]
                          for p in players_flop_n) == 1)

        # Minimize epsilon
        model.Minimize(e)

        solution_printer = SolutionPrinter(players_per_tid)

        # Solve with the CP-SAT solver
        solver = cp_model.CpSolver()
        status = solver.SolveWithSolutionCallback(
                        model, solution_printer)

        if status != cp_model.OPTIMAL:
            raise NoSolutionError()

        print('\nOptimal epsilon: %i\n'
                % solver.ObjectiveValue())

        print('General statistics:')
        print('    - Conflicts : %i'   % solver.NumConflicts())
        print('    - Branches  : %i'   % solver.NumBranches())
        print('    - Wall time : %f s' % solver.WallTime())
        print('    - Total solutions : %i'
              % solution_printer.nsolutions)

        return Solution.create(
                solver.ObjectiveValue(),
                avg_rating_per_team,
                Team.from_associations(
                        players_per_tid, solver))
