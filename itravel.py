import json
import math
import random
# import re

from abstractmodel import AbstractModel
from errors import ModelError
import utils


POINT_OF_INTEREST = [83, -15, 36]
P1 = [20, 64, -95]
P2 = [73, 28, -41]

MATRIXES = {
    2: [
        [[ .87,  .50], [-.50,  .87]],   # noqa
        [[-.50,  .87], [-.87, -.50]]],  # noqa
    3: [
        [[ .13,  .78, -.61], [ .93,  .13,  .35], [ .35, -.61, -.71]],  # noqa
        [[-.92,  .18,  .35], [-.31, -.88, -.35], [ .25, -.43,  .87]],  # noqa
        [[ .53, -.81,  .25], [ .81,  .40, -.43], [ .25,  .43,  .87]],  # noqa
        [[-.44, -.79, -.43], [-.66, -.05,  .75], [-.61,  .61, -.50]],  # noqa
        [[-.05,  .79,  .61], [-.66,  .44, -.61], [-.75, -.43,  .50]]]  # noqa
}
CAPACITORS = {
    'tourist': '2000-4000',
    'professional': '4000-8000',
    'scientific': '8000-15000',
    'geodesic': '15000-20000'
}


def rnd_vector(dim):
    return [random.randint(-100, 100) for _ in xrange(dim)]


class ITravel(AbstractModel):
    def __init__(self, ml, team, logger, output):
        AbstractModel.__init__(self, ml, self.__class__.__name__,
                               team, logger, output)

    def validate_input_params(self, input_params):
        clean_input_params = {}
        if input_params['dimensions'] in ('2D', '3D'):
            clean_input_params['dimensions'] = input_params['dimensions']
        else:
            raise ModelError(
                'Неверный пространственный охват, '
                'обратитесь к техническому специалисту.')

        if input_params['device_class'] in CAPACITORS.keys():
            clean_input_params['device_class'] = input_params['device_class']
        else:
            raise ModelError(
                'Неверный пользовательский класс, '
                'обратитесь к техническому специалисту.')

        return clean_input_params

    def validate_model_params(model_params, input_params):
        clean_model_params = {}

        vector_length = utils.to_float(model_params['vector_length'])
        if vector_length > 0:
            clean_model_params['vector_length'] = vector_length
        else:
            raise ModelError('Длина вектора не может быть ниже 0.')

        clean_model_params['alpha_x'] = utils.to_float(
            model_params['alpha_x'])
        clean_model_params['beta_y'] = utils.to_float(
            model_params['beta_y'])
        if input_params['dimensions'] == '3D':
            clean_model_params['gamma_z'] = utils.to_float(
                model_params['gamma_z'])

        # Not needed, but can be useful if power_capacity of a component is
        # a single integer, not an interval
        # if model_params['power_capacity'] in CAPACITORS.values():
        #     clean_model_params['power_capacity'] = map(
        #         int,
        #         re.match(
        #             '(\d+)-(\d+)', model_params['power_capacity']).groups())

        team_args = ('base_station', 'point_of_interest', 'p1', 'p2',
                     'center_shift', 'matrix')
        for name in team_args:
            clean_model_params[name] = json.loads(model_params[name])

        return clean_model_params

    def validate_components(self, components, input_params):
        clean_components = {}
        if not components['critical_errors_control'] == 'True':
            raise ModelError(
                'Ваша система должна включать модуль '
                'контроля критических помех.')

        clean_components['security_quality'] = utils.to_int(
            components['security_quality'])
        clean_components['capacitor_quality'] = utils.to_int(
            components['capacitor_quality'])

        clean_components['right_capacitor'] = (
            CAPACITORS[input_params['device_class']] ==
            components['power_capacity'])

        return clean_components

    def team_arguments(self, input_params):
        AbstractModel.team_arguments(self, input_params)

        clean_input_params = self.validate_input_params(input_params)

        if clean_input_params['dimensions'] == '2D':
            dim = 2
        else:
            dim = 3

        base_station = rnd_vector(dim)
        point_of_interest = POINT_OF_INTEREST[:dim]
        p1 = P1[:dim]
        p2 = P2[:dim]
        center_shift = rnd_vector(dim)
        matrix = random.choice(MATRIXES[dim])

        return {
            'base_station': str(base_station),
            'point_of_interest': str(point_of_interest),
            'p1': str(p1),
            'p2': str(p2),
            'center_shift': str(center_shift),
            'matrix': str(matrix)}

    def compute_2d(self, model_params):
        navigator_coords = [
            53 + model_params['base_station'][0],
            -36 + model_params['base_station'][1]]

        transformed_navi = [
            navigator_coords[0] * model_params['matrix'][0][0] +
            navigator_coords[1] * model_params['matrix'][0][1] +
            model_params['center_shift'][0],

            navigator_coords[0] * model_params['matrix'][1][0] +
            navigator_coords[1] * model_params['matrix'][1][1] +
            model_params['center_shift'][1]]

        vector_length = (
            ((model_params['point_of_interest'][0] -
              transformed_navi[0]) ** 2 +
             (model_params['point_of_interest'][1] -
              transformed_navi[1]) ** 2) ** .5)

        alpha_x = math.acos(
            (model_params['point_of_interest'][0] -
             transformed_navi[0]) / vector_length)
        alpha_x = math.degrees(alpha_x)

        return vector_length

    def compute_3d(self, model_params):
        navigator_coords = [
            53 + model_params['base_station'][0],
            -36 + model_params['base_station'][1],
            54 + model_params['base_station'][2]]

        transformed_navi = [
            navigator_coords[0] * model_params['matrix'][0][0] +
            navigator_coords[1] * model_params['matrix'][0][1] +
            navigator_coords[2] * model_params['matrix'][0][2] +
            model_params['center_shift'][0],

            navigator_coords[0] * model_params['matrix'][1][0] +
            navigator_coords[1] * model_params['matrix'][1][1] +
            navigator_coords[2] * model_params['matrix'][1][2] +
            model_params['center_shift'][1],

            navigator_coords[0] * model_params['matrix'][2][0] +
            navigator_coords[1] * model_params['matrix'][2][1] +
            navigator_coords[2] * model_params['matrix'][2][2] +
            model_params['center_shift'][2]]

        vector_length = (
            ((model_params['point_of_interest'][0] -
              transformed_navi[0]) ** 2 +
             (model_params['point_of_interest'][1] -
              transformed_navi[1]) ** 2 +
             (model_params['point_of_interest'][2] -
              transformed_navi[2]) ** 2) ** .5)

        alpha_x = math.acos(
            (model_params['point_of_interest'][0] -
             transformed_navi[0]) / vector_length)
        beta_y = math.acos(
            (model_params['point_of_interest'][1] -
             transformed_navi[1]) / vector_length)
        gamma_z = math.acos(
            (model_params['point_of_interest'][2] -
             transformed_navi[2]) / vector_length)
        alpha_x = math.degrees(alpha_x)
        beta_y = math.degrees(beta_y)
        gamma_z = math.degrees(gamma_z)

        return vector_length

    def pre_production(self, input_params, model_params, components):
        '''
            input_params:
                dimensions
                device_class
            model_params:
                vector_length
                alpha_x
                beta_y
                gamma_z
            components:
                critical_errors_control - must be True
                security_quality
                power_capacity
                capacitor_quality
        '''
        AbstractModel.pre_production(
            self, input_params, model_params, components)

        clean_input_params = self.validate_input_params(input_params)
        clean_model_params = self.validate_model_params(
            model_params, input_params)
        clean_components = self.validate_components(components, input_params)

        if clean_input_params['dimensions'] == '2D':
            vector_length = self.compute_2d(clean_model_params)
        else:
            vector_length = self.compute_3d(clean_model_params)

        length_diff = abs(vector_length - model_params['vector_length'])
        quality_base = (
            100 - length_diff * 10 + clean_components['security_quality'] +
            clean_components['capacitor_quality'])
        if not clean_components['right_capacitor']:
            quality_base -= 20

        quality = quality_base / 2

        if length_diff < 2:
            accuracy_text = 'В рамках стандартов.'
        else:
            accuracy_text = 'Низкая.'

        interm_params = (
            {'accuracy': accuracy_text},
            {'quality': quality})

        self.ml.check_interm_params(self.model, *interm_params)
        return interm_params

    def production(self, input_params, interm_params,
                   hidden_params, components):
        AbstractModel.production(
            self, input_params, interm_params, hidden_params, components)
        clean_input_params = self.validate_input_params(input_params)
        if clean_input_params['dimensions'] == '2D':
            coverage_text = 'Только поверхность Земли.'
        else:
            coverage_text = (
                'Все среды, до верхней границы атмосферы включительно.')
        output_params = {
            'quality': hidden_params['quality'],
            'coverage': coverage_text,
            'device_class': clean_input_params['device_class']}
        self.ml.check_output_params(self.model, output_params)
        return output_params
