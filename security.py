# -*- coding: UTF-8 -*-

import random

import numpy

from abstractmodel import AbstractModel
from errors import ModelError
import utils


S_MATRIXES = map(numpy.matrix, (
    ' .13,  .78, -.61;  .93,  .13,  .35;  .35, -.61, -.71',
    '-.92,  .18,  .35; -.31, -.88, -.35;  .25, -.43,  .87',
    ' .53, -.81,  .25;  .81,  .40, -.43;  .25,  .43,  .87',
    '-.44, -.79, -.43; -.66, -.05,  .75; -.61,  .61, -.50',
    '-.05,  .79,  .61; -.66,  .44, -.61; -.75, -.43,  .50'))
ROTATIONS = (
    (30, 135, 60), (210, 330, 45), (150, 30, 210),
    (225, 120, 30), (120, 300, 45))
U_DOMAINS = ('[90;180]', '[270;360]', '[0;90]', '[90;180]', '[270;360]')
ROTATION_PACKS = zip(S_MATRIXES, ROTATIONS, U_DOMAINS)
ROTATION_PACKS = [{
    's_matrix': rp[0],
    'rotation_angles': rp[1],
    'u_domain': rp[2]}
    for rp in ROTATION_PACKS]


def random_vect(left=-100, right=100):
    rnd_vect = [random.randint(left, right) for _ in range(3)]
    return numpy.matrix(rnd_vect).T


class Package(object):
    def __init__(self, rotation_pack, real_points=None):
        self.rotation_pack = rotation_pack

        if real_points is None:
            self.real_points = [random_vect() for _ in range(3)]
        else:
            self.real_points = real_points
        self.cypher_points = self._cypher_points()
        self.crooked_cyphers = self._crooked_cyphers()

    def _cypher_points(self):
        return map(lambda x: self.rotation_pack['s_matrix'] * x,
                   self.real_points)

    def _crooked_cyphers(self):
        crooked_cyphers = random_vect(-10000, 10000) / 100.
        return crooked_cyphers


class Security(AbstractModel):
    def __init__(self, ml, team, logger, output):
        AbstractModel.__init__(self, ml, self.__class__.__name__,
                               team, logger, output)

    def validate_input_params(self, input_params):
        if input_params['error_control'] not in ('True', 'False'):
            raise ModelError(
                'Что-то пошло не так с галочкой модуля '
                'контроля критических помех.')
        return {'error_control': input_params['error_control'] == 'True'}

    def team_arguments_without_control(self, first_package):
        return {
            'user_point': str(first_package.real_points[0]),
            'first_key': str(first_package.real_points[1]),
            'second_key': str(first_package.real_points[2]),
            'cyphered_user_point': str(first_package.cypher_points[0]),
            'first_cyphered_key': str(first_package.cypher_points[1]),
            'second_cyphered_key': str(first_package.cypher_points[2]),
            'u_domain': first_package.rotation_pack['u_domain'],
            # 'rotation_agnles': first_package.rotation_pack['rotation_angles'],  # noqa
        }

    def team_arguments_with_control(self, first_package, second_package):
        first_package_args = self.team_arguments_without_control(first_package)

        second_package_args = {
            'user_point': str(second_package.real_points[0]),
            'first_key': str(second_package.real_points[1]),
            'second_key': str(second_package.real_points[2]),
            'cyphered_user_point': str(second_package.crooked_cyphers[0]),
            'first_cyphered_key': str(second_package.crooked_cyphers[1]),
            'second_cyphered_key': str(second_package.crooked_cyphers[2]),
            'u_domain': second_package.rotation_pack['u_domain']}

        return {'first_package': first_package_args,
                'second_package': second_package_args}

    def team_arguments(self, input_params):
        AbstractModel.team_arguments(self, input_params)

        random.seed(self.team_specific_num)
        rotation_packs = ROTATION_PACKS[:]
        random.shuffle(rotation_packs)
        first_rotation_pack, second_rotation_pack = rotation_packs[:2]
        random.seed()

        first_package = Package(first_rotation_pack)

        points = [random_vect() for _ in range(2)]
        points.append(points[random.randint(0, 1)] * random.randint(2, 5))
        second_package = Package(
            second_rotation_pack, real_points=points)

        clean_input_params = self.validate_input_params(input_params)
        if clean_input_params['error_control']:
            return self.team_arguments_with_control(
                first_package, second_package)
        return self.team_arguments_without_control(first_package)

    def _max_angle_diff(self, first_angles, second_angles):
        max_angle_diff = max(map(
            lambda x: abs(x[0] - x[1]), zip(first_angles, second_angles)))
        if max_angle_diff < 11:
            work_correctness = 'OK'
        else:
            work_correctness = 'Not enough'

        return max_angle_diff, work_correctness

    def pre_production_without_control(self, model_params):
        '''
            model_params:
                psi - in degrees
                u - in degrees
                phi - in degrees
        '''
        clean_model_params = {}
        for key, val in model_params.items():
            if key == 'single_solution':
                clean_model_params[key] = (val == 'True')
            elif key in ('psi', 'u', 'phi'):
                clean_model_params[key] = utils.to_float(val)
            elif key == 'u_domain':
                pass
            else:
                clean_model_params[key] = numpy.matrix(val).T

        player_angles = [
            clean_model_params['psi'],
            clean_model_params['u'],
            clean_model_params['phi']]

        random.seed(self.team_specific_num)
        rotation_packs = ROTATION_PACKS[:]
        first_rotation_pack, second_rotation_pack = random.shuffle(
            rotation_packs)[:2]
        random.seed()
        real_points = [
            clean_model_params['user_point'],
            clean_model_params['first_key'],
            clean_model_params['second_key']]
        first_package = Package(first_rotation_pack, real_points=real_points)

        max_angle_diff, work_correctness = self._max_angle_diff(
            player_angles, first_package.rotation_pack['rotation_angles'])

        quality = 100 - 10 * max_angle_diff

        if quality < 0:
            quality = 0

        interm_params = (
            {
                'critical_error_handling': 'low',
                'work_correctness': work_correctness},
            {'quality': quality})

        return interm_params

    def pre_production_with_control(self, model_params):
        '''
            model_params:
                first_package:
                    psi - in degrees
                    u - in degrees
                    phi - in degrees
                    single_solution - True / False
                second_package:
                    psi - in degrees
                    u - in degrees
                    phi - in degrees
                    single_solution - True / False
        '''
        clean_model_params = {'first_package': {}, 'second_package': {}}
        for pack_name, pack_dict in clean_model_params.items():
            for key, val in model_params[pack_name].items():
                if key == 'single_solution':
                    pack_dict[key] = (val == 'True')
                elif key in ('psi', 'u', 'phi'):
                    pack_dict[key] = utils.to_float(val)
                elif key == 'u_domain':
                    pass
                else:
                    pack_dict[key] = numpy.matrix(val).T

        first_pack_answers = clean_model_params['first_package']
        second_pack_answers = clean_model_params['second_package']

        if not first_pack_answers['single_solution']:
            return (
                {'critical_error_handling': 'low',
                 'work_correctness': 'Not enough'},
                {'quality': 0})

        if (first_pack_answers['single_solution'] and
                not second_pack_answers['single_solution']):
            short_model_params = model_params['first_package']
            short_model_params.pop('single_solution')
            answer = self.pre_production_without_control(short_model_params)
            if answer['work_correctness'] == 'OK':
                answer['critical_error_handling'] = 'high'
            return answer

        random.seed(self.team_specific_num)
        rotation_packs = ROTATION_PACKS[:]
        first_rotation_pack, second_rotation_pack = random.shuffle(
            rotation_packs)[:2]
        random.seed()
        first_real_points = [
            clean_model_params['first_package']['user_point'],
            clean_model_params['first_package']['first_key'],
            clean_model_params['first_package']['second_key']]
        second_real_points = [
            clean_model_params['second_package']['user_point'],
            clean_model_params['second_package']['first_key'],
            clean_model_params['second_package']['second_key']]
        first_package = Package(first_rotation_pack,
                                real_points=first_real_points)
        second_package = Package(second_rotation_pack,
                                 real_points=second_real_points)

        player_angles = [
            first_pack_answers['psi'],
            first_pack_answers['u'],
            first_pack_answers['phi'],
            second_pack_answers['psi'],
            second_pack_answers['u'],
            second_pack_answers['phi']]

        computed_angles = (
            first_package.rotation_pack['rotation_angles'] +
            second_package.rotation_pack['rotation_angles'])

        max_angle_diff, work_correctness = self._max_angle_diff(
            player_angles, computed_angles)

        quality = 100 - 10 * max_angle_diff

        if max_angle_diff < 11:
            critical_error_handling = 'high'
            quality += 15
        else:
            critical_error_handling = 'low'

        if quality > 100:
            quality = 100
        if quality < 0:
            quality = 0

        open_interm_params = {
            'critical_error_handling': critical_error_handling,
            'work_correctness': work_correctness}
        if max_angle_diff < 11:
            open_interm_params['super-bonus'] = True

        return (open_interm_params, {'quality': quality})

    def pre_production(self, input_params, model_params, components):
        '''
            input_params:
                error_control - ('True', 'False')
            model_params are described in related functions
            no components
        '''
        AbstractModel.pre_production(
            self, input_params, model_params, components)
        clean_input_params = self.validate_input_params(input_params)  # noqa

        if clean_input_params['error_control']:
            interm_params = self.pre_production_with_control(model_params)
        else:
            interm_params = self.pre_production_without_control(model_params)

        self.ml.check_interm_params(self.model, *interm_params)
        return interm_params

    def production(self, input_params, interm_params,
                   hidden_params, components):
        AbstractModel.production(
            self, input_params, interm_params, hidden_params, components)
        output_params = {
            'critical_error_handling':
            interm_params['critical_error_handling'],
            'quality': hidden_params['quality']}
        self.ml.check_output_params(self.model, output_params)
        return output_params
