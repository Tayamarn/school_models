# -----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# STEM Engine simulator
#
# Abstract model interface
#
# Author: Alexey Fedoseev <aleksey@fedoseev.net>, 2014
# -----------------------------------------------------------------------------


class AbstractModel:
    def __init__(self, ml, model, team, logger, output):
        '''
        Parameters:
            ml	model loader instance
            model	model name
            team	the unique team name
                logger	model logger
                output  model output file
        '''
        self.ml = ml
        self.model = model
        self.logger = logger
        self.ml.check_model(model)
        self.team = team
        self.output = output

    def team_specific_num(self):
        return hash(self.team)

    def team_arguments(self):
        '''
        Run the simulation arguments
        Random or based on team_specific_num
            dict
                    {'x': 1, 'y': 2}
        '''
        return {}

    def pre_production(self, input_params, model_params, components):
        '''
        Run the pre-production simulation
        Arguments:
            dict
                    {'arg1': 1, 'arg2': 2}
            dict
                    {'arg1': 1, 'arg2': 2}
            dict
                    {'component1': {'arg1': 1, 'arg2': 2},
                         'component2': {'arg3': 3, 'arg4': 4}}
        Return value:
            list of two dicts (intermediate, hidden intermediate)
                    ({'param1': 1, 'param2': 2},
                 {'quality': 0.2})
        Possible exceptions:
                ModelError - possible calculation errors
            CriticalError - unpredicted

        '''
        self.ml.check_input_params(self.model, input_params)
        self.ml.check_model_params(self.model, model_params)
        self.ml.check_components(self.model, components)

    def production(self, interm_params, hidden_params, components):
        '''
        Run the production simulation
        Arguments:
            dict
                    {'a1': 1, 'a2': 2}
            dict
                    {'a3': 3, 'quality': 0.1}
            dict
                    {'component1': {'arg1': 1, 'arg2': 2},
                         'component2': {'arg3': 3, 'arg4': 4}}
        Return value:
            dict
                    {'param1': 1, 'param2': 2, 'quality': 0.2}
        Possible exceptions:
                ModelError - possible calculation errors
            CriticalError - unpredicted

        '''
        self.ml.check_interm_params(self.model, interm_params, hidden_params)
        self.ml.check_components(self.model, components)
