from abstractmodel import AbstractModel
# from errors import ModelError
# import utils


class ITravel(AbstractModel):
    def __init__(self, ml, team, logger, output):
        AbstractModel.__init__(self, ml, self.__class__.__name__,
                               team, logger, output)

    def team_arguments(self, input_params):
        AbstractModel.team_arguments(self, input_params)

        return {}

    def pre_production(self, input_params, model_params, components):
        '''
            input_params:

            model_params:

            components:

        '''
        AbstractModel.pre_production(
            self, input_params, model_params, components)

        # clean_input_params = self.validate_input_params(input_params)
        # clean_model_params = self.validate_model_params(model_params)
        # clean_components = self.validate_components(components)

        quality = 0

        interm_params = (
            {},
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
