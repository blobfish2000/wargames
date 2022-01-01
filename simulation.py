from model import *
from tqdm import tqdm


class Encounter:
    """
    Class for an encounter between a group of players and a group of monsters.

    Attributes:
        players (list): List of players in the encounter.
        monsters (list): List of monsters in the encounter.

    Methods:
        __init__(self, players, monsters): Initializes the encounter.
        run(self): Runs the encounter.
    """

    def __init__(self, players, monsters):
        """
        Initializes the encounter.

        Args:
            players (list): List of players in the encounter.
            monsters (list): List of monsters in the encounter.
        """
        self.players = players
        self.monsters = monsters
        self.initiative_order = []

    def run(self):
        for player in self.players:
            initiative = player.roll_initiative()
            self.initiative_order.append((initiative, player))
        for monster in self.monsters:
            initiative = monster.roll_initiative()
            self.initiative_order.append((initiative, monster))

        self.initiative_order.sort(key=lambda x: x[0], reverse=True)

        round_number = 1
        while True:
            print("----- ROUND {} -----".format(round_number))

            for actor in self.players + self.monsters:
                print("{} is at distance {} with mobility {}".format(actor.name, actor.distance, actor.mobility))


            for initiative, entity in self.initiative_order:
                print("-- {}'s turn: --".format(entity.name))
                if entity in self.players:
                    entity.perform_turn(self.monsters)
                else:
                    entity.perform_turn(self.players)

            player_alive = False
            for player in self.players:
                player_alive = player_alive or player.alive

            monster_alive = False
            for monster in self.monsters:
                monster_alive = monster_alive or monster.alive

            if not player_alive:
                print("Players lose")
                for actor in self.players + self.monsters:
                    print("{}'s HP: {}".format(actor.name, actor.hp_current))
                return False
            elif not monster_alive:
                print("Monsters lose")
                for actor in self.players + self.monsters:
                    print("{}'s HP: {}".format(actor.name, actor.hp_current))
                return True

            round_number += 1

    def monte_carlo_simulation(self, iterations=100):
        """
        Runs a Monte Carlo simulation of the encounter.

        Args:
            iterations (int): Number of iterations to run.

        Returns:
            int: Number of wins.
        """
        wins = 0

        for _ in tqdm(range(iterations)):
            dummy_players = [player.copy() for player in self.players]
            dummy_monsters = [monster.copy() for monster in self.monsters]
            encounter = Encounter(dummy_players, dummy_monsters)
            outcome = encounter.run()
            if outcome:
                wins += 1
        return wins/iterations
        




