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


TRAVEL_REGEX = r'(?:mhd|bus|vlak|spoj)\s(?:z|zo)\s([A-Za-z\s]+)' \
    '\s(?:na|do)\s([A-Za-z\s]+)([0-9]+:[0-9]+)?(\s[0-9.]+)?'


@threaded
@match(regex=TRAVEL_REGEX)
def line_match(event, f, t, time=None, date=None, *args):
    """Search for mhd in BA or bus/train lines in Slovakia

    Examples:
        bus z mlyny na hlst
        vlak z BA do TO
        bus z BA do LM 18:00 20.12.2014
        spoj zo Zochova no mlyny
    """
    msg = event.meta["body"]

    if f == t:
        return "Not in this universe."

    time = '' if time is None else time
    date = '' if date is None else date

    if ("zajtra" in msg or "pozajtra" in msg) and date is not '':
        if "pozajtra" in msg:
            delta = 2
        elif "zajtra" in msg:
            delta = 1
        date = (datetime.date.today() + datetime.timedelta(days=delta)) \
            .strftime("%d.%m.%Y")

    vehicle = "vlakbus"
    if "bus" in msg:
        vehicle = "bus"
    elif "vlak" in msg:
        vehicle = "vlak"

    r = cpsk.get_routes(f, t, vehicle=vehicle, time=time, date=date)
    if not len(r):
        f = imhdsk.clear_stop(imhdsk.suggest(
                                rootify(f.split(' ')[0]))[0]['name'])
        t = imhdsk.clear_stop(imhdsk.suggest(
                                rootify(t.split(' ')[0]))[0]['name'])

        r = imhdsk.routes(f, t, time=time, date=date)

    out = r[0].__repr__() if len(r) else "Nothing found"
    out = unicode(out.strip(codecs.BOM_UTF8), 'utf-8')
    return out.encode('utf-8')


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
    """Search for next bus line from A to B

    Examples:
        !bus BA TO
        !bus Kosice - Bratislava - 19:00 - 20.12.2014
    """

    return get_line(event, 'bus')


@threaded
@cmd
def vlak(event):
    """Search for next train line from A to B

    Examples:
        !vlak Kosice Bratislava
        !vlak Kosice - Bratislava - 19:00 - 20.12.2014
    """
    return get_line(event, 'vlak')
