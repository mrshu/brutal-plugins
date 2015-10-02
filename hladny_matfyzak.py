# -*- coding: utf-8 -*-

from brutal.core.plugin import cmd
from datetime import datetime
import hladnymatfyzak


DATE_FORMAT = '%d.%m.%Y'


def validate_date_and_args(args):
    """Validates given date"""
    if len(args) >= 1:
        try:
            valid = datetime.strptime(args[0], DATE_FORMAT)
        except ValueError:
            return None
        return datetime(day=valid.day, month=valid.month, year=valid.year)
    return datetime.today()


def output_meals(meals):
    """Returns string of meals"""
    out = ''
    for i, meal in enumerate(meals, start=1):
        out += '{0}. {1}€ '.format(i, meal)
        out += '\n' if i % 3 == 0 else ''

    return out


@cmd
def horna(event):
    """Meals available in horna

    Examples:
        !horna 24.12.2015
    """
    date_obj = validate_date_and_args(event.args)
    if date_obj is None:
        return 'Invalid date'

    meals = hladnymatfyzak.horna(day=date_obj.day, month=date_obj.month,
                                 year=date_obj.year)
    return output_meals(meals)


@cmd
def dolna(event):
    """Meals available in dolna

    Examples:
        !dolna 24.12.2015
    """
    date_obj = validate_date_and_args(event.args)
    if date_obj is None:
        return 'Invalid date'

    meals = hladnymatfyzak.dolna(day=date_obj.day, month=date_obj.month,
                                 year=date_obj.year)
    return output_meals(meals)


@cmd
def faynfood(event):
    """Meals available in Faynfood

    Examples:
        !faynfood 24.12.2015
    """
    date_obj = validate_date_and_args(event.args)
    if date_obj is None:
        return 'Invalid date'

    meals = hladnymatfyzak.ffood('faynfood', day=date_obj.day,
                                 month=date_obj.month, year=date_obj.year)
    return output_meals(meals)


@cmd
def freefood(event):
    """Meals available in Freefood

    Examples:
        !freefood 24.12.2015
    """
    date_obj = validate_date_and_args(event.args)
    if date_obj is None:
        return 'Invalid date'

    meals = hladnymatfyzak.ffood('freefood', day=date_obj.day,
                                 month=date_obj.month, year=date_obj.year)
    return output_meals(meals)
