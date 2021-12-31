import random
import math

DAMAGE_TYPES = [
    "acid",
    "bludgeoning",
    "cold",
    "fire",
    "force",
    "lightning",
    "necrotic",
    "piercing",
    "poison",
    "psychic",
    "radiant",
    "slashing",
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
        damage_type (str): The type of damage the attack deals.
        damage_dice (DiceRoll): The dice rolled for damage.
        attack_roll (DiceRoll): The dice rolled for the attack.
        save_dc (int): The DC for the saving throw.
        save_ability (str): The ability used for the saving throw.
        actor (Character): The character performing the attack.
    """

    def __init__(self, name, damage_type, damage_dice, actor, attack_roll=None, save_dc=None):
        self.name = name
        if damage_type not in DAMAGE_TYPES:
            raise ValueError("Invalid damage type.")
        self.damage_type = damage_type
        self.damage_dice = damage_dice
        self.actor = actor
        self.attack_roll = attack_roll
        self.save_dc = save_dc

        

    def __str__(self):
        return self.name + ": " + str(self.damage_dice)

    def __repr__(self):
        return self.name + ": " + str(self.damage_dice)

    def attack(self, target):
        """
        Performs the attack.
        """
        log_string = self.actor.name + " attacks " + target.name + " with " + self.name + ":\n"
        if self.attack_roll is not None:
            roll = self.attack_roll.roll()
            if roll >= target.ac:
                log_string += " Rolls " + str(roll) + " >= " + str(target.ac) + ": Hit\n"
                damage = self.damage_dice.roll()
                log_string += " Damage: " + str(damage)
                target.take_damage(damage, self.damage_type)
            else:
                log_string += " Rolls " + str(self.attack_roll) + " < " + str(target.ac) + ": Miss"
        elif self.save_dc is not None:
            target_save = target.saves[self.save_ability].roll()
            if self.save_dc >= target_save:
                log_string += " Rolls " + str(target_save) + " >= " + str(self.save_dc) + ": Save\n"
                damage = Math.floor(self.damage_dice.roll()/2)
                log_string += " Damage: " + damage
                target.take_damage(damage, self.damage_type)
            else:
                log_string += " Rolls " + str(target_save) + " < " + str(self.save_dc) + ": Fails\n"
                damage = self.damage_dice.roll()
                log_string += " Damage: " + damage
                target.take_damage(damage, self.damage_type)
        else:
            log_string += " Damage: " + str(self.damage_dice)
            target.take_damage(self.damage_dice.roll(), self.damage_type)
        log_string += "\n" + target.name + " has " + str(target.hp_current) + " HP left."
        print(log_string)



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
        attacks (list): A list of attacks that the actor can make
        alive (bool): Whether the actor is alive or not
        initiative (int): The initiative of the actor
    """

    def __init__(self,
            name, 
            hp_max, 
            ac, 
            resistances=[], 
            vulnerabilities=[], 
            attacks=[], 
            initiative=0):

        self.name = name
        self.hp_max = hp_max
        self.hp_current = hp_max
        self.ac = ac
        self.resistances = resistances
        self.vulnerabilities = vulnerabilities
        self.attacks = attacks
        self.alive = True
        self.initiative = initiative

    def __str__(self):
        return self.name + ": " + str(self.hp_current) + "/" + str(self.hp_max)

    def __repr__(self):
        return self.name + ": " + str(self.hp_current) + "/" + str(self.hp_max)

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


        




