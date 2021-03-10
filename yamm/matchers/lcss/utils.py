import functools as ft
from itertools import groupby
from operator import itemgetter
from typing import List, Callable, Any


def forward_merge(merge_list: List, condition: Callable[[Any], bool]) -> List:
    """
    Helper function to merge items in a list by adding them to the next eligible element.
    This merge moves left to right.

    For example, given the list:

    [1, 2, 3, 4, 5]

    And the condition, x < 3, the function yields:

    >>> forward_merge([1,2,3,4,5], lambda x: x < 3)
    >>> [6, 4, 5]

    :param merge_list: the list to merge
    :param condition: the merge condition

    :return: a list of the merged items
    """
    items = []

    def _flatten(ml):
        return ft.reduce(lambda acc, x: acc + x, ml)

    merge_items = []
    merge_index = None
    for i, item in enumerate(merge_list):
        if condition(item):
            merge_items.append(item)
        elif merge_items:
            # we found a large item and have short items to merge
            merge_items.append(item)
            items.append(_flatten(merge_items))
            merge_items = []
            merge_index = i
        else:
            items.append(item)

    if merge_items and not merge_index:
        # we got to the end but still have merge items;
        items.append(_flatten(merge_items))
    else:
        for item in merge_items:
            items.append(item)

    return items


def reverse_merge(merge_list: List, condition: Callable[[Any], bool]) -> List:
    """
    Helper function to merge items in a list by adding them to the next eligible element.
    This merge moves right to left.

    For example, given the list:

    [1, 2, 3, 4, 5]

    And the condition, x < 3, the function yields:

    >>> list(reverse_merge([1,2,3,4,5], lambda x: x < 3))
    >>> [3, 3, 4, 5]

    :param merge_list: the list to merge
    :param condition: the merge condition

    :return: a generator of the merged items
    """
    items = []

    def _flatten(ml):
        return ft.reduce(lambda acc, x: x + acc, ml)

    merge_items = []
    merge_index = None
    for i in reversed(range(len(merge_list))):
        item = merge_list[i]
        if condition(item):
            merge_items.append(item)
        elif merge_items:
            # we found a large item and have short items to merge
            merge_items.append(item)
            items.append(_flatten(merge_items))
            merge_items = []
            merge_index = i
        else:
            items.append(item)

    if merge_items and not merge_index:
        # we got to the end but still have merge items;
        items.append(_flatten(merge_items))
    else:
        for item in merge_items:
            items.append(item)

    return items


def merge(merge_list: List, condition: Callable[[Any], bool]) -> List:
    f_merge = forward_merge(merge_list, condition)

    if any(map(condition, f_merge)):
        return reverse_merge(f_merge, condition)
    else:
        return f_merge


def compress(cp):
    for k, g in groupby(enumerate(cp), lambda x: x[0] - x[1].trace_index):
        all_cps = list(map(itemgetter(1), g))
        yield all_cps[int(len(all_cps) / 2)]
