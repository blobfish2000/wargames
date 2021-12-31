import unittest
from model import DiceRoll

class TestDiceRoll(unittest.TestCase):
    def setUp(self):
        self.dice_roll = DiceRoll([6,4],1)

    def test_dice_roll_max(self):
        self.assertEqual(self.dice_roll.max(),11)

    def test_dice_roll_min(self):
        self.assertEqual(self.dice_roll.min(),3)

    def test_dice_roll_avg(self):
        self.assertEqual(self.dice_roll.average(),7)

    def test_dice_roll_monte_carlo(self):
        monte_carlo = [self.dice_roll.roll() for i in range(10000)]
        self.assertTrue(self.dice_roll.max() in monte_carlo)
        self.assertTrue(self.dice_roll.min() in monte_carlo)
        mont_carlo_average = sum(monte_carlo)/len(monte_carlo)
        delta = abs(self.dice_roll.average() - mont_carlo_average)
        self.assertLess(delta,0.1)

    def test_dice_roll_above(self):
        simplified_dice_roll = DiceRoll([10],1)
        probability_half = simplified_dice_roll.probability_above(7)
        expected_probability = 0.5
        delta = abs(probability_half - expected_probability)
        self.assertLess(delta,0.025)
        probability_one = simplified_dice_roll.probability_above(11)
        expected_probability = 0.1
        delta = abs(probability_one - expected_probability)
        self.assertLess(delta,0.025)
        self.assertEqual(simplified_dice_roll.probability_above(12),0)
        self.assertEqual(simplified_dice_roll.probability_above(2),1)

    def test_dice_roll_below(self):
        simplified_dice_roll = DiceRoll([10],1)
        probability_half = simplified_dice_roll.probability_below(6)
        expected_probability = 0.5
        delta = abs(probability_half - expected_probability)
        self.assertLess(delta,0.025)
        probability_one = simplified_dice_roll.probability_below(2)
        expected_probability = 0.1
        delta = abs(probability_one - expected_probability)
        self.assertLess(delta,0.025)
        self.assertEqual(simplified_dice_roll.probability_below(1),0)
        self.assertEqual(simplified_dice_roll.probability_below(11),1)

class TestAttack(unittest.TestCase):
    def setUp(self):

    def test_attack_max(self):
        

if __name__ == '__main__':
    unittest.main()
