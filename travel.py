import imhdsk
import cpsk
from brutal.core.plugin import match, cmd, threaded
import codecs
import datetime
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def rootify(word):
    """Return probable root of the word."""

    if len(word) <= 5:
        return word

    w = word[::-1]
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    for x in range(len(word)):
        if w[x] in vowels and x != 0:
            return word[:-x-1]


@threaded
@match(regex='.*bus (?:z|zo) (.*?) (:?do|na) (.+?)(?:\s|$)')
def mhd_match(event, f, t, *args, **kwargs):
    f = f
    t = args[0]

    if f == t:
        return "Not in this universe."

    time = ''
    date = ''
    if len(args) >= 3:
        time = args[2]
    if len(args) >= 4:
        date = args[3]

    f = imhdsk.clear_stop(imhdsk.suggest(rootify(f.split(' ')[0]))[0]['name'])
    t = imhdsk.clear_stop(imhdsk.suggest(rootify(t.split(' ')[0]))[0]['name'])

    r = imhdsk.routes(f, t, time=time, date=date)

    out = r[0].__repr__()
    out = unicode(out.strip(codecs.BOM_UTF8), 'utf-8')
    return out.encode('utf-8')


@threaded
@cmd
def mhd(event):
    """Get the next BA MHD from A to B by running !mhd A B"""

    args = event.args

    if len(args) < 2:
        return

    args = list(args)

    if '-' in args:
        a = ' '.join(args)
        args = map(lambda x: x.strip(), a.split('-'))

    f = args[0]
    t = args[1]

    if f == t:
        return "Not in this universe."

    time = ''
    date = ''
    if len(args) >= 3:
        time = args[2]
    if len(args) >= 4:
        date = args[3]

    r = imhdsk.routes(f, t, time=time, date=date)
    if len(r) == 0:
        return

    out = r[0].__repr__()
    out = unicode(out.strip(codecs.BOM_UTF8), 'utf-8')
    return out.encode('utf-8')


@threaded
@match(regex=r'(?:.*\s+|)(?:bus|vlak|spoj)\sz\s([A-Za-z\s]+)\sdo\s([A-Za-z\s]+)(?:.*\s+|)')
def cpsk_match(event, departure, dest, *args):
    """Searches for bus or train info in Slovakia.

    Examples:
        bus z BA do TO
        najblizsi vlak z Topolcany do Prievidza
        spoj z KE do Trencin
        zajtra bus z TO do Jacovce
        pozajtra o 20:30 bus z TO do BA
    """
    msg = event.meta['body']

    date = ''
    if 'zajtra' in msg:
        date = (datetime.date.today() + datetime.timedelta(days=1)) \
                    .strftime("%d.%m.%Y")
    elif 'pozajtra' in msg:
        date = (datetime.date.today() + datetime.timedelta(days=2)) \
                    .strftime("%d.%m.%Y")

    time_match = re.search("([0-9]+:[0-9]+)", msg)
    time = ''
    if time_match is not None:
        time = msg[time_match.start():time_match.end()]

    vehicle = 'vlakbus'
    if 'vlak' in msg:
        vehicle = 'vlak'
    elif 'bus' in msg:
        vehicle = 'bus'

    routes = cpsk.get_routes(departure, dest, vehicle=vehicle,
                                 time=time, date=date)

    return routes[0].__repr__()


def get_line(event, vehicle):
    """Searches for bus/train based on given vehicle argument"""
    args = event.args

    if len(args) < 2:
        return

    if '-' in args:
        a = ' '.join(args)
        args = map(lambda x: x.strip(), a.split('-'))

    dep = args[0]
    dest = args[1]

    time = args[2] if len(args) > 2 else ''
    date = args[3] if len(args) > 3 else ''

    if dep == dest:
        return "You joker"

    r = cpsk.get_routes(dep, dest, vehicle=vehicle, time=time, date=date)
    return r[0].__repr__() if len(r) else "Nothing found"


@threaded
@cmd
def bus(event):
    """Command for bus lines.

    Examples:
        !bus BA TO
    """

    return get_line(event, 'bus')


@threaded
@cmd
def vlak(event):
    """Command for train lines.

    Examples:
        !vlak Kosice Bratislava

    """
    return get_line(event, 'vlak')
