import math
import random

from abstractmodel import AbstractModel
from errors import ModelError
import utils


class GlobalNav(AbstractModel):
    def __init__(self, ml, team, logger, output):
        AbstractModel.__init__(self, ml, self.__class__.__name__,
                               team, logger, output)

    def validate_input_params(self, input_params):
        revolution_period = utils.to_int(input_params['revolution_period'])
        if revolution_period <= 0:
            raise ModelError('Период обращения должен быть больше 0.')

        orbital_inclination = utils.to_int(input_params['orbital_inclination'])
        if not 0 < orbital_inclination < 90:
            raise ModelError(
                'Наклонение орбиты должно лежать в пределах [0;90].')

        return {
            'revolution_period': revolution_period,
            'orbital_inclination': orbital_inclination}

    def validate_model_params(self, model_params):
        orbit_radius = utils.to_float(model_params['orbit_radius'])
        if orbit_radius <= 0:
            raise ModelError('Проектный радиус орбиты должен быть больше 0.')

        pos_crit_accel = utils.to_float(model_params['pos_crit_accel'])
        if pos_crit_accel <= 0:
            raise ModelError(
                'Критическое нормальное положительное ускорение '
                'должно быть больше 0.')

        neg_crit_accel = utils.to_float(model_params['neg_crit_accel'])
        if neg_crit_accel <= 0:
            raise ModelError(
                'Критическое нормальное отрицательное ускорение '
                'должно быть больше 0.')

        permissible_variation = utils.to_int('model_params')

        return {
            'orbit_radius': orbit_radius,
            'pos_crit_accel': pos_crit_accel,
            'neg_crit_accel': neg_crit_accel,
            'permissible_variation': permissible_variation}

    def validate_components(self, components):
        if not components['critical_errors_control'] == 'True':
            raise ModelError(
                'Ваша система должна включать модуль '
                'контроля критических помех.')

        security_quality = utils.to_int(components['security_quality'])
        return {'security_quality': security_quality}

    def team_arguments(self, input_params):
        AbstractModel.team_arguments(self, input_params)
        self.permissible_variation = random.randint(2, 10)
        return {'permissible_variation': self.permissible_variation}

    def pre_production(self, input_params, model_params, components):
        '''
            input_params:
                revolution_period - in minutes
                orbital_inclination - degrees

            model_params:
                orbit_radius - kilometers
                pos_crit_accel
                neg_crit_accel
                permissible_variation - from team_arguments

            components:
                critical_errors_control - must be True
                security_quality
        '''
        AbstractModel.pre_production(
            self, input_params, model_params, components)
        clean_input_params = self.validate_input_params(input_params)
        clean_model_params = self.validate_model_params(model_params)
        clean_components = self.validate_components(components)

        orbit_radius = 21.7 * (
            (clean_input_params['revolution_period'] * 60) ** (2. / 3.))
        if orbit_radius < 150:
            orbit_radius_text = (
                'Из-за высокого сопротивления атмосферы орбита непригодна.')
        elif abs(orbit_radius - clean_model_params['orbit_radius']) > 50:
            orbit_radius_text = (
                'Не согласуется с периодом обращения.')
        else:
            orbit_radius_text = (
                'Согласуется с периодом обращения.')

        crit_acceleration = (39.82 * 10000 / (orbit_radius ** 2)) * 1.05
        pos_crit_accel = crit_acceleration * (
            1. - clean_model_params['permissible_variation'] / 100.)
        neg_crit_accel = crit_acceleration * (
            1. + clean_model_params['permissible_variation'] / 100.)

        coverage = (
            clean_input_params['orbital_inclination'] +
            math.degrees(math.acos(6400. / orbit_radius)))
        if coverage < 90:
            coverage_text = '[0;{}]'.format(coverage)
        else:
            coverage_text = 'Вся Земля.'

        quality = (
            100 -
            (abs(pos_crit_accel - clean_model_params['pos_crit_accel']) /
                pos_crit_accel * 100) -
            (abs(neg_crit_accel - clean_model_params['neg_crit_accel']) /
                neg_crit_accel * 100) +
            clean_components['security_quality']) / 2.

        if quality < 0:
            quality = 0

        interm_params = (
            {
                'coverage': coverage_text,
                'orbit_radius_text': orbit_radius_text},
            {
                'quality': quality,
                'revolution_period': clean_input_params['revolution_period']})

        self.ml.check_interm_params(self.model, *interm_params)
        return interm_params

    def production(self, input_params, interm_params,
                   hidden_params, components):
        AbstractModel.production(
            self, input_params, interm_params, hidden_params, components)
        output_params = {
            'quality': hidden_params['quality'],
            'revolution_period': hidden_params['revolution_period']}
        self.ml.check_output_params(self.model, output_params)
        return output_params
