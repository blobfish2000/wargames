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
        monte_carlo = [self.dice_roll.roll() for i in range(1000)]
        self.assertTrue(self.dice_roll.max() in monte_carlo)
        self.assertTrue(self.dice_roll.min() in monte_carlo)
        mont_carlo_average = sum(monte_carlo)/len(monte_carlo)
        delta = abs(self.dice_roll.average() - mont_carlo_average)
        self.assertLess(delta,0.1)


        

if __name__ == '__main__':
    unittest.main()
