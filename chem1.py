import random

from abstractmodel import AbstractModel


PEROXIDES = [{'name': 'KO2', 'q1': 157.75, 'q2': 80.55, 'q3': 236.62},
             {'name': 'NaO2', 'q1': 203.64, 'q2': 157.7, 'q3': 305.45},
             {'name': 'LiO', 'q1': 486.96, 'q2': 259.71, 'q3': 243.48}]

PEROXIDE_TO_QUALITY = {0: 25, 1: 15, 2: 10}


def percentage_difference(original, copy):
    return 100.0 * abs(original - copy) / original


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


class OxygenRegeneration(AbstractModel):
    def __init__(self, ml, team, logger, output):
        AbstractModel.__init__(self, ml, self.__class__.__name__,
                               team, logger, output)
        self.peroxides = [Peroxide(**p) for p in PEROXIDES]

    def check_peroxide(self, peroxide_name):
        sorted_peroxide_names = [p.name for p in sorted(
            self.peroxides,
            key=lambda p: p.specific_oxygen_allocation_volume,
            reverse=True)]
        return PEROXIDE_TO_QUALITY[sorted_peroxide_names.index(peroxide_name)]

    def check_carbon_dioxide_absorption(self, absorption_volume):
        pass

    def check_oxygen_allocation(self, allocation_volume):
        pass

    def team_arguments(self):
        return {p.name: p.impurity_factor for p in self.peroxides}

    def pre_production(self, input_params, model_params, components):
        '''
            input_params:
                n - number of people in the spaceship
                t - spaceship lifetime, hours
            model_params:
                peroxide_name - name of the chosen peroxide
                carbon_dioxide_absorption - specific carbon dioxide absorption
                                            volume for the chosen peroxide
                oxygen_allocation - specific oxygen allocation volume for
                                    the chosen peroxide
            components:
        '''
        AbstractModel.pre_production(
            self, input_params, model_params, components)
        assert (model_params['peroxide_name'] in
                [p.name for p in self.peroxides])
        # What should I do with this parameter?
        oxygen_volume_required = input_params['n'] * input_params['t'] * 50 # noqa
        quality = 0
        quality += self.check_peroxide(model_params['peroxide_name'])
        quality += self.check_carbon_dioxide_absorption(
            model_params['carbon_dioxide_absorption'])
        quality += self.check_oxygen_allocation(
            model_params['oxygen_allocation'])

        p = ({'durability': input_params['size'] * model_params['density']},
             {'quality': quality})
        self.ml.check_interm_params(self.model, *p)
        return p

    # Don't yet know, what will be going here

    # def production(self, interm_params, hidden_params, components):
    #     AbstractModel.production(
    #         self, interm_params, hidden_params, components)
    #     p = {'durability': interm_params['durability'],
    #          'quality': hidden_params['quality']}
    #     self.ml.check_output_params(self.model, p)
    #     return p
