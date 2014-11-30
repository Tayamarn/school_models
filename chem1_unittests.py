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


class MockML(object):
    def check_model(self, model):
        pass

    def check_input_params(self, model, input_params):
        pass

    def check_model_params(self, model, model_params):
        pass

    def check_components(self, model, components):
        pass

    def check_interm_params(self, model, interm_params, hidden_params):
        pass


class CheckOxygenRegeneration(unittest.TestCase):
    def setUp(self):
        mock_ml = MockML()
        self.regenerator = chem1.OxygenRegeneration(
            mock_ml, 'foo', 'logger', 'out')

    def test_init(self):
        self.assertEqual(len(self.regenerator.peroxides), 3)
        peroxide_names = [p.name for p in self.regenerator.peroxides]
        for peroxide in chem1.PEROXIDES:
            self.assertIn(peroxide['name'], peroxide_names)

    def test_chosen_peroxide(self):
        name = 'KO2'
        peroxide = self.regenerator.chosen_peroxide(name)
        self.assertEqual(peroxide.name, name)

    def test_check_peroxide(self):
        name = 'NaO2'

        # mock_input_params = {'n': 2, 't': 10}
        # mock_model_params = {
        #     'peroxide_name': 'KO2',
        #     'carbon_dioxide_absorption': 160,
        #     'oxygen_allocation': 200,
        #     'electricity_ammount': 17232000}
        # print(self.regenerator.team_arguments(mock_input_params))
        # print(self.regenerator.pre_production(
        #     mock_input_params, mock_model_params, {}))


if __name__ == '__main__':
    unittest.main()
