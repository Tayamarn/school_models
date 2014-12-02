"""
Utilities for my models. You can use them too!

Comments are welcome at max@goldenforests.ru
"""


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
