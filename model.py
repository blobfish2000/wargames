import random
import math
from copy import deepcopy

DAMAGE_TYPES = [
    "acid",
    "bludgeoning",
    "bludgeoning-magic",
    "cold",
    "fire",
    "force",
    "lightning",
    "necrotic",
    "piercing",
    "piercing-magic",
    "poison",
    "psychic",
    "radiant",
    "slashing",
    "slashing-magic",
    "thunder"
]

ABILITY_SCORES = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma"
]

class DiceRoll:
    """
    A class to represent a dice roll.

    Attributes:
        dice (list): A list of integers representing the dice rolled.
        modifier (int): An integer representing the modifier applied to the roll.
    """
    def __init__(self, dice, modifier):
        self.dice = dice
        self.modifier = modifier

    def __str__(self):
        dice_count = {}
        for die in self.dice:
            if die in dice_count:
                dice_count[die] += 1
            else:
                dice_count[die] = 1
        output = ""
        for die in dice_count:
            output += str(dice_count[die]) + "d" + str(die) + " + "

        output += str(self.modifier)
        return output

    def __repr__(self):
        return str(self.dice) + " + " + str(self.modifier)

    def __add__(self, other):
        if isinstance(other, int):
            return DiceRoll(self.dice, self.modifier + other)
        elif isinstance(other, DiceRoll):
            return DiceRoll(self.dice + other.dice, self.modifier + other.modifier)
        else:
            raise TypeError("Can only add integers or DiceRoll objects.")

    def __radd__(self, other):
        if isinstance(other, int):
            return DiceRoll(self.dice, self.modifier + other)
        elif isinstance(other, DiceRoll):
            return DiceRoll(self.dice + other.dice, self.modifier + other.modifier)
        else:
            raise TypeError("Can only add integers or DiceRoll objects.")

    def __sub__(self, other):
        if isinstance(other, int):
            return DiceRoll(self.dice, self.modifier - other)
        elif isinstance(other, DiceRoll):
            dice_count = {}
            for die in self.dice:
                if die in dice_count:
                    dice_count[die] += 1
                else:
                    dice_count[die] = 1
            other_dice_count = {}
            for die in other.dice:
                if die in other_dice_count:
                    other_dice_count[die] += 1
                else:
                    other_dice_count[die] = 1

            for die in other_dice_count:
                if die in dice_count:
                    dice_count[die] -= other_dice_count[die]

            output_dice = [dice_count[die] for die in dice_count]
            output_modifier = self.modifier - other.modifier
            return DiceRoll(output_dice, output_modifier)

    def __eq__(self, other):
        if isinstance(other, DiceRoll):
            dice_count = {}
            for die in self.dice:
                if die in dice_count:
                    dice_count[die] += 1
                else:
                    dice_count[die] = 1
            other_dice_count = {}
            for die in other.dice:
                if die in other_dice_count:
                    other_dice_count[die] += 1
                else:
                    other_dice_count[die] = 1
            return dice_count == other_dice_count and self.modifier == other.modifier
        else:
            raise TypeError("Can only compare DiceRoll objects.")

    def roll(self):
        """
        Rolls the dice and returns the result.
        """
        return sum(random.randint(1, die) for die in self.dice) + self.modifier

    def average(self):
        """
        Returns the average of the dice roll.
        """
        return sum([die + 1 for die in self.dice])/2 + self.modifier
    def max(self):
        """
        Returns the maximum possible roll.
        """
        return sum(die for die in self.dice) + self.modifier

    def min(self):
        """
        Returns the minimum possible roll.
        """
        return len(self.dice) + self.modifier

    def probability_above(self, value, simulations=10000):
        """
        Returns the probability of rolling a value or higher.
        """
        if value > self.max():
            return 0
        elif value <= self.min():
            return 1
        return sum(1 for _ in range(simulations) if self.roll() >= value)/simulations

    def probability_below(self, value, simulations=10000):
        """
        Returns the probability of rolling a value or lower.
        """
        return 1 - self.probability_above(value+1, simulations)

class Attack:
    """
    A class to represent an attack.

    Attributes:
        name (str): The name of the attack.
        damage_profile (list): A list of tuples of the form (damage_type, damage_dice) where...
            damage_type (str): The type of damage the attack does.
            damage_dice (DiceRoll): The dice roll representing the damage.
        attack_roll (DiceRoll): The dice rolled for the attack.
        save_dc (int): The DC for the saving throw.
        save_ability (str): The ability used for the saving throw.
        actor (Character): The character performing the attack.
        attack_range (function): A function that returns the effectiveness of the attack based on the distance between the encounter and the target.
        advantage (int): positive for advantage, negative for disadvantage, 0 for no advantage.
        additional_effects (list): A list of functions that are called when the attack hits.
    """

    def __init__(self, name, damage_profile, actor, attack_roll=None,
            save_dc=None, attack_range=0, save_ability=None,
            additional_effects=[], advantage=0):
        self.name = name
        for damage_type, damage_dice in damage_profile:
            if damage_type not in DAMAGE_TYPES:
                raise ValueError("Invalid damage type: " + damage_type)
        self.damage_profile = damage_profile
        self.actor = actor
        if isinstance(attack_roll, DiceRoll):
            self.attack_roll = attack_roll
        elif isinstance(attack_roll, int):
            self.attack_roll = DiceRoll([20], attack_roll)
        else:
            self.attack_roll = None
        self.save_dc = save_dc
        if isinstance(attack_range, int):
            # if attack_range is passed as an integer, turn it into a step function
            self.attack_range = lambda x: 1 if x <= attack_range else 0
        elif callable(attack_range):
            self.attack_range = attack_range
        else:
            raise TypeError("attack_range must be either an integer or a function.")

        self.save_ability = save_ability
        self.additional_effects = additional_effects
        self.advantage_status = advantage

        

    def __str__(self):
        return self.name + ": " + str(self.damage_profile)

    def __repr__(self):
        return self.name + ": " + str(self.damage_profile)


    def attack(self, target, log=True, advantage=False, disadvantage=False):
        """
        Performs the attack.

        Args:
            target (Character): The target of the attack.
            log (bool): Whether or not to print the attack.
        """
        log_string = self.actor.name + " attacks " + target.name + " with " + self.name + ":\n"

        effective_distance = max(0, target.distance - self.actor.mobility)
        if log:
            log_string += "Effective distance: " + str(effective_distance) + "\n"
        range_multiplier = self.attack_range(effective_distance)
        damage_multiplier = range_multiplier
        if self.advantage_status > 0:
            advantage = True
        elif self.advantage_status < 0:
            disadvantage = True
        critical_hit = False
        damage = 0
        if range_multiplier == 0:
            log_string += "Out of range.\n"
        elif self.attack_roll is not None:
            roll = self.attack_roll.roll()
            if advantage and not disadvantage:
                roll = max(roll, self.attack_roll.roll())
            elif disadvantage and not advantage:
                roll = min(roll, self.attack_roll.roll())

            if roll - self.attack_roll.modifier == 20:
                critical_hit = True
                log_string += " Rolls " + str(roll) + " : Critical Hit\n"
            elif roll >= target.ac:
                log_string += " Rolls " + str(roll) + " >= " + str(target.ac) + ": Hit\n"
            else:
                log_string += " Rolls " + str(roll) + " < " + str(target.ac) + ": Miss"
                damage_multiplier = 0
        elif self.save_dc is not None:
            target_save = target.saves[self.save_ability].roll()
            if self.save_dc >= target_save:
                log_string += " Rolls " + str(target_save) + " >= " + str(self.save_dc) + ": Save\n"
                damage_multiplier = damage_multiplier * 0.5
            else:
                log_string += " Rolls " + str(target_save) + " < " + str(self.save_dc) + ": Fails\n"


        for damage_type, damage_dice in self.damage_profile:
            unmodified_damage = damage_dice.roll()
            if critical_hit:
                unmodified_damage = unmodified_damage + damage_dice.roll() - damage_dice.modifier
            damage = unmodified_damage * damage_multiplier
            if damage > 0:
                log_string += damage_type[0].upper() + damage_type[1:] + ": " + str(damage) + " | "
                target.take_damage(damage, damage_type)
        if log:
            print(log_string)
        return damage

    def average_damage(self, target, simulations=100, maximise_lethal_damage=True):
        """
        Returns the average damage of the attack.
        """
        damage_total = 0
        for _ in range(simulations):
            dummy = deepcopy(target)
            dummy_original_hp = dummy.hp_current
            damage = self.attack(dummy, log=False)
            hp_delta = dummy_original_hp - dummy.hp_current
            if dummy.hp_current == 0:
                if  maximise_lethal_damage:
                    damage_total += sum(damage_dice.max() for damage_type, damage_dice in self.damage_profile)
                else:
                    damage_total += damage
            else:
                damage_total += hp_delta

        return damage_total/simulations

class Multiattack:
    """
    A class to represent a multiattack (which can be composed of spells or attacks).

    Attributes:
        name (str): The name of the multiattack.
        attacks (list): A list of attacks.
        uses (int): The number of uses of the multiattack per combat encounter.
    """
    def __init__(self, name, attacks, uses=float("inf")):
        self.name = name
        self.attacks = attacks
        self.uses = uses
            

class Actor:
    """
    A class to represent an actor in the simulation

    Attributes:
        name (str): The name of the actor
        hp_max (int): The maximum health of the actor
        hp_current (int): The current health of the actor
        ac (int): The armor class of the actor
        resistances (list): A list of damage types that the actor is resistant to
        vulnerabilities (list): A list of damage types that the actor is vulnerable to
        attacks (list): A list of multiattacks that the actor can make
        alive (bool): Whether the actor is alive or not
        initiative (int): The initiative of the actor
        distance (int): The distance from the actor to the encounter
        speed (int): The speed of the actor
        mobility (int): The effective "reach" of the actor, increasing range of attacks
    """

    def __init__(self,
            name, 
            hp_max, 
            ac, 
            resistances=[], 
            vulnerabilities=[], 
            attacks=[], 
            initiative=0,
            distance=0,
            speed=30):

        self.name = name
        self.hp_max = hp_max
        self.hp_current = hp_max
        self.ac = ac
        self.resistances = resistances
        self.vulnerabilities = vulnerabilities
        self.attacks = attacks
        self.alive = True
        self.initiative = initiative
        self.distance = distance
        self.speed = speed
        for attack in self.attacks:
            if isinstance(attack, Attack):
                attack = Multiattack(attack.name, [attack])
            for attack in attack.attacks:
                attack.actor = self
        self.mobility = 0

    def __str__(self):
        return self.name + ": " + str(self.hp_current) + "/" + str(self.hp_max)

    def __repr__(self):
        return self.name + ": " + str(self.hp_current) + "/" + str(self.hp_max)

    def __deepcopy__(self, memo):
        ##TODO: actually deepcopy the attacks
        new_actor = Actor(self.name, self.hp_max, self.ac, self.resistances, self.vulnerabilities, self.attacks, self.initiative, self.distance)
        new_actor.hp_current = self.hp_current
        new_actor.alive = self.alive
        new_actor.mobility = self.mobility
        new_actor.distance = self.distance
        return new_actor
        
    def copy(self):
        return deepcopy(self)

    def take_damage(self, damage, damage_type):
        """
        Takes damage from an attack.
        """
        if damage_type in self.resistances:
            damage = Math.floor(damage/2)
        elif damage_type in self.vulnerabilities:
            damage = Math.floor(damage*2)
        self.hp_current -= damage
        if self.hp_current < 0:
            self.hp_current = 0
            self.alive = False

    def roll_initiative(self):
        """
        Return the initiative of the actor.
        """
        return DiceRoll([20], self.initiative).roll()

    def choose_target(self, targets, attack):
        """
        Choose a target for the actor to attack.

        Args:
            targets (list): A list of targets to choose from.

        Returns:
            Character: The chosen target.
        """

        best_target = None
        best_damage = 0
        for target in targets:
            expected_damage = attack.average_damage(target)
            if expected_damage > best_damage:
                best_target = target
                best_damage = expected_damage

        return best_target


    def perform_multiattack(self, multiattack, targets, log=True):
        """
        Perform a multiattack.

        Args:
            multiattack (Multiattack): The multiattack to perform.
            targets (list): The targets to attack.
        """
        if isinstance(multiattack, Attack):
            multiattack = Multiattack("", [multiattack])

        if multiattack.uses <= 0:
            raise Exception("Multiattack has no uses left")

        can_attack = False
        for attack in multiattack.attacks:
            target = self.choose_target(targets, attack)
            if target is not None:
                can_attack = True
                attack.attack(target,log)
        if can_attack:
            multiattack.uses -= 1
        
        return can_attack

    def perform_turn(self, targets, log=True):
        """
        Perform a turn for the actor.

        Args:
            targets (list): The targets to attack.
        """
        if self.alive:
            self.move(self.speed)
            attacked = False
            for multiattack in self.attacks:
                if multiattack.uses > 0:
                    print(self.name + " is performing " + multiattack.name)
                    attacked = self.perform_multiattack(multiattack, targets)
                    break

            if not attacked:
                if log:
                    print("{} has no targets, dashing".format(self.name))
                self.move(self.speed)
        else:
            if log:
                print(self.name + " is dead.")
            return

    def move(self, distance):
        """
        Move the actor.

        Args:
            distance (int): The distance to move.
        """
        self.mobility += distance






        


        




