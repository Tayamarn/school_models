import random

from abstractmodel import AbstractModel
from errors import ModelError
import utils


PEROXIDES = [{'name': 'KO2', 'q1': 157.75, 'q2': 80.55, 'q3': 236.62},
             {'name': 'NaO2', 'q1': 203.64, 'q2': 157.7, 'q3': 305.45},
             {'name': 'LiO', 'q1': 486.96, 'q2': 259.71, 'q3': 243.48}]

PEROXIDE_TO_QUALITY = {0: 25, 1: 15, 2: 10}
DIFFERENCE_TO_QUALITY = [(5, 25), (10, 20), (20, 15), (25, 10), (50, 5)]


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
    ELECTRICITY_NEEDED = 17232

    def __init__(self, ml, team, logger, output):
        AbstractModel.__init__(self, ml, self.__class__.__name__,
                               team, logger, output)
        self.peroxides = [Peroxide(**p) for p in PEROXIDES]

    def chosen_peroxide(self, peroxide_name):
        return filter(lambda p: p.name == peroxide_name, self.peroxides)[0]

    def check_peroxide(self, peroxide_name):
        sorted_peroxide_names = [p.name for p in sorted(
            self.peroxides,
            key=lambda p: p.specific_oxygen_allocation_volume,
            reverse=True)]
        return PEROXIDE_TO_QUALITY[sorted_peroxide_names.index(peroxide_name)]

    @staticmethod
    def oxygen_volume(men_count, time_hours):
        return 50 * men_count * time_hours

    def check_carbon_dioxide_absorption(self, the_peroxide, absorption_volume):
        return utils.quality_by_precision(
            the_peroxide.specific_carbon_dioxide_absorption_volume,
            absorption_volume,
            DIFFERENCE_TO_QUALITY)

    def check_oxygen_allocation(self, the_peroxide, allocation_volume):
        return utils.quality_by_precision(
            the_peroxide.specific_oxygen_allocation_volume,
            allocation_volume,
            DIFFERENCE_TO_QUALITY)

    def check_electricity_amount(self, computed_amount, player_amount):
        return utils.quality_by_precision(
            computed_amount, player_amount, DIFFERENCE_TO_QUALITY)

    def validate_input_params(self, input_params):
        return {
            'n': utils.to_int(input_params['n']),
            't': utils.to_float(input_params['t'])
        }

    def validate_model_params(self, model_params):
        if utils.to_float(
                model_params['carbon_dioxide_absorption']) < 0:
            raise ModelError(
                "Рассчетное значение удельного поглощения углекислого газа"
                " не может быть ниже 0.")
        if utils.to_float(
                model_params['oxygen_allocation']) < 0:
            raise ModelError(
                "Рассчетное значение удельного выделения кислорода"
                " не может быть ниже 0.")
        if utils.to_float(
                model_params['electricity_amount']) < 0:
            raise ModelError(
                "Рассчетное значение необходимой электроэнергии"
                " не может быть ниже 0.")

        return {
            'peroxide_name': model_params['peroxide_name'],
            'carbon_dioxide_absorption': utils.to_float(
                model_params['carbon_dioxide_absorption']),
            'oxygen_allocation': utils.to_float(
                model_params['oxygen_allocation']),
            'electricity_amount': utils.to_float(
                model_params['electricity_amount'])
        }

    def team_arguments(self, input_params):
        AbstractModel.team_arguments(self, input_params)
        clean_input_params = self.validate_input_params(input_params)
        peroxide_impurities = {p.name: p.impurity_factor
                               for p in self.peroxides}
        oxygen_volume_required = self.oxygen_volume(
            clean_input_params['n'], clean_input_params['t'])
        return {'peroxide_impurities': peroxide_impurities,
                'oxygen_volume_required': oxygen_volume_required}

    def pre_production(self, input_params, model_params, components):
        '''
            input_params:
                n - number of people in the platform
                t - platform lifetime, hours
            model_params:
                peroxide_name - name of the chosen peroxide
                carbon_dioxide_absorption - specific carbon dioxide absorption
                        volume for the chosen peroxide
                oxygen_allocation - specific oxygen allocation volume for
                        the chosen peroxide
                electricity_amount - amount of electricity needed to get the
                        required oxygen by electrolysis
            components:
        '''
        AbstractModel.pre_production(
            self, input_params, model_params, components)

        clean_input_params = self.validate_input_params(input_params)
        clean_model_params = self.validate_model_params(model_params)

        the_peroxide = self.chosen_peroxide(
            clean_model_params['peroxide_name'])
        oxygen_volume_required = self.oxygen_volume(  # noqa
            clean_input_params['n'], clean_input_params['t'])
        quality = self.check_peroxide(clean_model_params['peroxide_name'])
        quality += self.check_carbon_dioxide_absorption(
            the_peroxide, clean_model_params['carbon_dioxide_absorption'])
        quality += self.check_oxygen_allocation(
            the_peroxide, clean_model_params['oxygen_allocation'])
        quality += self.check_electricity_amount(
            self.ELECTRICITY_NEEDED,
            clean_model_params['electricity_amount'])

        oxygen_allocation_text = ' '.join(
            ['Полученное при испытаниях удельное выделение кислорода:',
             utils.percentage_frame(
                 the_peroxide.specific_oxygen_allocation_volume)])
        carbon_dioxide_absorption_text = ' '.join(
            ['Полученное при испытаниях удельное поглощение углекислого газа:',
             utils.percentage_frame(
                 the_peroxide.specific_carbon_dioxide_absorption_volume)])

        interm_params = (
            {'real_oxygen_allocation': oxygen_allocation_text,
             'real_carbon_dioxide_absorption': carbon_dioxide_absorption_text},
            {'quality': quality})

        self.ml.check_interm_params(self.model, *interm_params)
        return interm_params

    def production(self, input_params, interm_params,
                   hidden_params, components):
        AbstractModel.production(
            self, input_params, interm_params, hidden_params, components)
        output_params = {'quality': hidden_params['quality']}
        self.ml.check_output_params(self.model, output_params)
        return output_params
