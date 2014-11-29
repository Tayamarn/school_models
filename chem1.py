import random


class Peroxide(object):
    def __init__(self, name, q1, q2, q3):
        self.name = name
        self.impurity_factor = self._random_impurity_factor()
        self.specific_carbon_dioxide_absorption_volume = (
            self._specific_carbon_dioxide_absorption_volume(q1, q2))
        self.specific_oxygen_allocation_volume = (
            self._specific_oxygen_allocation_volume(q3))

    @staticmethod
    def _random_impurity_factor():
        return random.randrange(1, 11) * 0.01

    def _specific_carbon_dioxide_absorption_volume(self, q1, q2):
        return q1 + (q2 * self.impurity_factor)

    def _specific_oxygen_allocation_volume(self, q3):
        return q3 * (1 - self.impurity_factor)
