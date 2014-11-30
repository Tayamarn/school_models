from abstractmodel import AbstractModel


OXIDIZERS = ('oxygen', 'nitric oxide')
FUELS = ('hydrazine', 'DMH', 'hydrogen', 'ammonia', 'methane', 'kerosene')
RATE_AND_RADICALS = (
    (0.2349, 0.56), (0.4355, 0.7), (0.1284, 0.45), (0.0683, 0.325),
    (0.3646, 0.65), (0.2522, 0.6), (0.1457, 0.47), (0.5686, 0.75))


class BlendedFuel(object):
    def __init__(self, oxidizer, fuel, rate_constant, radicals_amount):
        pass


class RocketFuel(AbstractModel):
    def __init__(self, ml, team, logger, output):
        AbstractModel.__init__(self, ml, self.__class__.__name__,
                               team, logger, output)

    def team_arguments(self, input_params):
        return {}

    def pre_production(self, input_params, model_params, components):
        AbstractModel.pre_production(
            self, input_params, model_params, components)
        quality = 0
        interm_params = ({},
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
