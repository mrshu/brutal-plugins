import imhdsk
from brutal.core.plugin import match, cmd, threaded
import codecs
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


@threaded
@cmd
def mhd(event):
    args = event.args

    if len(args) < 2:
        return

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
