import random

from abstractmodel import AbstractModel
import utils

# For reference
# OXIDIZERS = ('oxygen', 'nitric oxide')
# FUELS = ('hydrazine', 'DMH', 'hydrogen', 'ammonia', 'methane', 'kerosene')
FUEL_RECIPES = (
    ('oxygen', 'hydrazine', 8146.72, 15), ('oxygen', 'DMH', 9315.64, 25),
    ('oxygen', 'hydrogen', 12641.78, 30), ('oxygen', 'ammonia', 6902.4, 10),
    ('oxygen', 'methane', 9707, 28), ('oxygen', 'kerosene', 9498.8, 26),
    ('nitric oxide', 'hydrazine', 6727.3, 10),
    ('nitric oxide', 'DMH', 7234.8, 13))
RATE_AND_RADICALS = (
    (0.2349, 0.56), (0.4355, 0.7), (0.1284, 0.45), (0.0683, 0.325),
    (0.3646, 0.65), (0.2522, 0.6), (0.1457, 0.47), (0.5686, 0.75))


class BlendedFuel(object):
    def __init__(self, oxidizer, fuel, combustion_heat, quality,
                 rate_constant, radicals_amount):
        self.oxidizer = oxidizer
        self.fuel = fuel
        self.combustion_heat = combustion_heat
        self.quality = quality
        self.rate_constant = rate_constant
        self.radicals_amount = radicals_amount


class RocketFuel(AbstractModel):
    def __init__(self, ml, team, logger, output):
        AbstractModel.__init__(self, ml, self.__class__.__name__,
                               team, logger, output)
        random.shuffle(RATE_AND_RADICALS)
        random_recipe_mix = map(lambda x: x[0] + x[1],
                                zip(FUEL_RECIPES, RATE_AND_RADICALS))
        self.fuel_types = [BlendedFuel(*r) for r in random_recipe_mix]

    def chosen_blend(self, oxidizer, fuel):
        return filter(lambda f: f.oxidizer == oxidizer and f.fuel == fuel,
                      self.fuel_types)[0]

    def check_heat(self, the_blend, heat):
        QUALITY = [(5, 40), (10, 30), (20, 15)]
        return utils.quality_by_precision(
            the_blend.combustion_heat, heat, QUALITY)

    def check_radicals(self, the_blend, radicals):
        QUALITY = [(5, 30), (10, 25), (20, 20), (25, 15), (50, 5)]
        return utils.quality_by_precision(
            the_blend.radicals_amount, radicals, QUALITY)

    def team_arguments(self, input_params):
        return {(f.oxidizer, f.fuel): f.rate_constant for f in self.fuel_types}

    def pre_production(self, input_params, model_params, components):
        """
            model_params:
                oxidizer - one of oxidizers
                fuel - one of fuels
                combustion_heat - calculated by players
                radicals_amount - calculated by players
        """
        AbstractModel.pre_production(
            self, input_params, model_params, components)
        assert (model_params['oxidizer'], model_params['fuel']) in FUEL_RECIPES

        the_blend = self.chosen_blend(
            model_params['oxidizer'], model_params['fuel'])
        quality = the_blend.quality
        quality += self.check_heat(the_blend, model_params['combustion_heat'])
        quality += self.check_radicals(
            the_blend, model_params['radicals_amount'])
        interm_params = ({'quality': quality},
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
