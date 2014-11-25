import imhdsk
from brutal.core.plugin import match, cmd, threaded
import codecs
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
