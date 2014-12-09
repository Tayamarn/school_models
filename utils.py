# -*- coding: UTF-8 -*-
"""
Utilities for my models. You can use them too!

Comments are welcome at max@goldenforests.ru
"""
import random

from errors import ModelError


def percentage_difference(original, copy):
    return 100.0 * abs(original - copy) / original


def quality_by_precision(original, copy, diff_to_quality):
    '''
        If you want your quality to be 20 for difference<=15%,
        10 for difference in (15%, 30%] and 0 otherwise,
        your diff_to_quality should look like ((15, 20), (30, 10))
    '''
    difference = percentage_difference(original, copy)
    for max_difference, quality in diff_to_quality:
        if difference < max_difference:
            return quality
    return 0


def to_int(param):
    try:
        return int(round(to_float(param)))
    except ValueError:
        raise ModelError(
            "Не могу преобразовать {param} в целоое число.".format(
                param=param))


def to_float(param):
    if not param:
        return 0.0
    s = str(param)  # Just in case
    s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        raise ModelError(
            "Не могу преобразовать {param} в число.".format(
                param=param))


def percentage_frame(val, min_perc=5, max_perc=15):
    left_border = (1 - random.randint(
        int(min_perc * 100), int(max_perc * 100)) / 10000.) * val
    right_border = (1 + random.randint(
        int(min_perc * 100), int(max_perc * 100)) / 10000.) * val
    return '{l} - {r}'.format(l=left_border, r=right_border)
