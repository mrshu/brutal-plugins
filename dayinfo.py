# -*- coding: utf-8 -*-

from brutal.core.plugin import cmd
from datetime import datetime
from calendar import isleap

from pynameday.slovakia import Slovakia as sknameday
from workalendar.europe import Slovakia as skholiday


DATE_FORMAT = '%d.%m.%Y'


INTERNATIONAL_DAY = {
    '1': {'27': 'International Day of Commemoration in Memory of the Victims \
                 of the Holocaust'},

    '2': {'4': 'World Cancer Day',
          '8': 'Day of Safer Internet',
          '11': 'World Day of the Sick',
          '14': 'World Valentine Day',
          '15': 'World Single’s Day',
          '21': 'International Mother Language Day'},

    '3': {'8': 'International Women’s Day',
          '14': 'Pi Day',
          '20': 'International Day of Happiness',
          '28': 'Day of Teachers'},

    '4': {'11': 'Daffodil Day - the day of the fight against cancer',
          '22': 'International Mother Earth Day'},

    '5': {'15': 'International Family Day',
          '17': 'World Telecommunication and Information Society Day'},

    '6': {'1': 'International Children’s Day',
          '21': 'Day of flowers'},

    '7': {'8': 'Day of Videogames',
          '30': 'International Day of Friendship'},

    '8': {'13': 'International Lefthanders Day'},

    '9': {'13': 'International Day of Programmers',
          '19': 'Day of Software Freedom'},

    '10': {'5': 'World Teachers’ Day',
           '20': 'International Day of Trees'},

    '11': {'2': 'All Souls Day',
           '17': 'International Students Day',
           '30': 'Day of Computer Safety'},

    '12': {'10': 'Human Rights Day'}
}


if isleap(datetime.today().year):
    del INTERNATIONAL_DAY['8']['13']
    INTERNATIONAL_DAY['8']['12'] = 'International Day of Programmers'


def formatter(string, prefix=''):
    """Format data"""
    if string:
        return ', {0}{1}'.format(prefix, string)
    return ''


@cmd
def dayinfo(event):
    """Informs you about current day

    Examples:
        !dayinfo
        !dayinfo 24.12.2015
    """
    args = event.args
    if len(args) == 1:
        try:
            today = datetime.strptime(event.args[0], DATE_FORMAT)
        except ValueError:
            return 'Not a valid date'
    else:
        today = datetime.today()

    day = today.day
    month = today.month

    names = sknameday()
    name = formatter(names.get_nameday(month=month, day=day),
                     prefix='Nameday: ')

    hols = skholiday()
    filtered = filter(lambda x: x[0] == today, hols.holidays(today.year))

    try:
        hol = formatter(filtered[0][1])
    except IndexError:
        hol = ''

    try:
        intday = formatter(INTERNATIONAL_DAY[str(month)][str(day)])
    except KeyError:
        intday = ''

    curr_date = today.strftime('%A %d.%m.%Y')

    return '{0}{1}{2}{3}'.format(curr_date, name, hol, intday)
