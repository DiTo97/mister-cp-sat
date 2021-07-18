import itertools as it
import random
import typing as t

from ortools.sat.python import cp_model

# Custom imports
from mister.constants import Ratings
from mister.errors import NoSolutionError
from mister.formation import Formation
from mister.player import Player
from mister.position import Position
from mister.solution import Solution
from mister.team import Team


MIN_epsilon   = 0
MAX_epsilon   = Ratings['MAX']

MIN_solutions = 3


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
        self.__solutions = []

    def on_solution_callback(self):
        if self.ObjectiveValue() <= int(MAX_epsilon*0.32):
            print('\nSolution %i with:' % self.__nsolutions)

            self.__nsolutions += 1

            solution = {ptid: self.Value(v) for ptid, v
                        in self.__players_per_tid.items()}

            self.__solutions.append(
                (self.ObjectiveValue(),
                solution))

            print('    Objective value = %i\n'
                % self.ObjectiveValue())

            # Print each team's info
            for _t in Team.from_associations(
                    self.__players_per_tid, self):
                print('    Team %i with rating = %i [\n' %
                    (_t.id, _t.rating), end='')

                for p in _t.players:
                    print('        (%s,%s,%s)\n' %
                        (p.name, p.rating, p.position), end='')

                print('    ]')

    @property
    def nsolutions(self):
        return self.__nsolutions

    def get_solutions(self) -> t.List:
        """
        Get a range of good solutions up to some threshold on the objective value.
        """
        self.__solutions.sort(key=lambda s: s[0])
        good_solutions = []

        for k, g in it.groupby(self.__solutions,
                               lambda s: s[0]):
            if len(good_solutions) >= MIN_solutions:
                break
                
            good_solutions += list(g)

        return good_solutions


class Manager:
    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def make_teams(n: int,
                   players: t.List[Player],
                   formation: Formation,
                   optimal: bool = False) -> Solution:
        if formation is not None:
            n = formation.nplayers

        nplayers = len(players)
        nteams = nplayers // n
        npositions = _npositions()

        teams_ids = range(nteams)

        # Sort players by rating
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
        e = model.NewIntVar(MIN_epsilon,
                            MAX_epsilon,
                            'epsilon')

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

        if formation is not None:
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

        if formation is None:
            # C7. Each team must have at most +-1 players
            # per position with respect to the other teams
            for k in Position:
                for i in range(len(teams_ids) - 1):
                    for j in range(i + 1, len(teams_ids)):
                        tid = teams_ids[i]
                        oid = teams_ids[j]

                        # For each pair extract the number of
                        # player at position k
                        nplayers_k_tid = sum(players_per_tid[(p, tid)]
                                             for p in players
                                             if p.position == k)

                        nplayers_k_oid = sum(players_per_tid[(p, oid)]
                                             for p in players
                                             if p.position == k)

                        # 1. Team i has the same players
                        # as Team j at position k
                        nplayers_eq = model.NewBoolVar('P: {} - N {} == N {}'
                                                       .format(k, i, j))

                        model.Add(nplayers_k_tid == nplayers_k_oid + 0) \
                             .OnlyEnforceIf(nplayers_eq)

                        # 2. Team i has one more player
                        # at position k than Team j
                        nplayers_p1 = model.NewBoolVar('P: {} - N {} == N {} + 1'
                                                       .format(k, i, j))

                        model.Add(nplayers_k_tid == nplayers_k_oid + 1) \
                             .OnlyEnforceIf(nplayers_p1)

                        # 3. Team i has one less player
                        # at position k than Team j
                        nplayers_m1 = model.NewBoolVar('P: {} - N {} == N {} - 1'
                                                       .format(k, i, j))

                        model.Add(nplayers_k_tid == nplayers_k_oid - 1) \
                             .OnlyEnforceIf(nplayers_m1)

                        # Ensure at least one is true
                        model.AddBoolOr([nplayers_eq,
                                         nplayers_p1,
                                         nplayers_m1])


        # Minimize epsilon
        model.Minimize(e)

        solution_printer = SolutionPrinter(players_per_tid)

        # Solve with the CP-SAT solver
        solver = cp_model.CpSolver()
        status = solver.SolveWithSolutionCallback(
                        model, solution_printer)

        if status != cp_model.OPTIMAL:
            if status != cp_model.FEASIBLE:
                raise NoSolutionError()

            print('{} solutions were found, but all sub-optimal.'
                  .format(solution_printer.nsolutions))

        print('\nOptimal epsilon: %i\n'
                % solver.ObjectiveValue())

        print('General statistics:')
        print('    - Conflicts : %i'   % solver.NumConflicts())
        print('    - Branches  : %i'   % solver.NumBranches())
        print('    - Wall time : %f s' % solver.WallTime())
        print('    - Total solutions : %i'
              % solution_printer.nsolutions)

        # Pick the optimal solution
        if optimal:
            return Solution.create(
                    solver.ObjectiveValue(),
                    avg_rating_per_team,
                    Team.from_associations(
                            players_per_tid, solver))

        # Pick a random solution from the set of good enough solutions
        # to better reflect the search space near convergence.
        solutions = solution_printer.get_solutions()

        if not solutions:
            raise NoSolutionError()

        epsilon, variables = random.choice(solutions)

        return Solution.create(
                epsilon, avg_rating_per_team,
                Team.from_associations(
                        variables, solver))
