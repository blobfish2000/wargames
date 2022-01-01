from model import *
from simulation import *


def main():
    ipqi = Actor("Ipqi-Ishtar Ei-amen-nef-neb-oui",103,18, distance=60)
    ipqi_longbow = Attack("Longbow",
            [
                ("piercing-magic", DiceRoll([8],5)),
                ("piercing-magic", DiceRoll([6,6,6],0))
                ],
            ipqi,
            attack_roll = 5, attack_range = 150,
            advantage = 1)
    ipqi_multi_attack = Multiattack(
            "Longbow Multiattack",
            [ipqi_longbow, ipqi_longbow, ipqi_longbow]
            )
    ipqi.attacks = [ipqi_multi_attack]

    rot_troll = Actor("Rot-Troll",138,16, distance=0, speed=30)
    rot_troll_bite = Attack("Bite",
            [
                ("piercing", DiceRoll([6],4)),
                ("necrotic", DiceRoll([10,10,10],0))
                ],
            rot_troll,
            attack_roll = 8, attack_range = 5)
    rot_troll_claws = Attack("Claws",
            [
                ("slashing", DiceRoll([6,6],4)),
                ("necrotic", DiceRoll([10],0))
                ],
            rot_troll,
            attack_roll = 8, attack_range = 5)
    rot_troll_aura = Attack("Aura",
            [
                ("necrotic", DiceRoll([10,10],0))
                ],
            rot_troll,
            attack_range = 5)
    rot_troll_multi_attack = Multiattack(
            "Bite, 2x Claws (with Aura)",
            [rot_troll_bite, rot_troll_aura, rot_troll_claws, rot_troll_claws]
            )
    rot_troll.attacks = [rot_troll_multi_attack]

    encounter = Encounter([ipqi], [rot_troll])
    result = encounter.monte_carlo_simulation(iterations=100)
    print("Ipqi wins {} percent of the time".format(result*100))
    



    


    


if __name__ == '__main__':
    main()
