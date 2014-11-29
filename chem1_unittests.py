import unittest

import chem1


class MockPeroxide(chem1.Peroxide):
    @staticmethod
    def _random_impurity_factor():
        return 0.01


class CheckPeroxide(unittest.TestCase):
    def setUp(self):
        self.test_peroxide = MockPeroxide('foo', 157.75, 80.55, 236.62)

    def test_creation(self):
        self.assertEqual(self.test_peroxide.name, 'foo')
        self.assertEqual(self.test_peroxide.impurity_factor, 0.01)
        self.assertAlmostEqual(
            self.test_peroxide.specific_carbon_dioxide_absorption_volume,
            158.5555)
        self.assertAlmostEqual(
            self.test_peroxide.specific_oxygen_allocation_volume, 234.2538)

    def test_random_impurity(self):
        for _ in xrange(1000):
            f = chem1.Peroxide._random_impurity_factor()
            ok_factors = [0.01, 0.02, 0.03, 0.04, 0.05,
                          0.06, 0.07, 0.08, 0.09, 0.1]
            self.assertIn(f, ok_factors)

    def test_absorption(self):
        self.assertAlmostEqual(
            self.test_peroxide._specific_carbon_dioxide_absorption_volume(
                1, 20), 1.2)

    def test_allocation(self):
        self.assertAlmostEqual(
            self.test_peroxide._specific_oxygen_allocation_volume(25), 24.75)


if __name__ == '__main__':
    unittest.main()
