from brutal.core.plugin import cmd, event, match
import re


@cmd
def ping(event):
    """Responds 'pong' to your 'ping'."""
    return 'pong'


@cmd
def echo(event):
    """Echoes back the message it recieves."""
    return ' '.join(event.args)


@cmd
def sudo(event):
    """Responds 'okay.' to your 'sudo ...' (http://xkcd.com/149/)."""
    return 'okay.'


@cmd
def make(event):
    """Tells user to go make it himself (http://xkcd.com/149/')."""
    return 'what? make it yourself.'


welcomes_db = {
    '#databazy': {
        "lordpotato":
            "Everybody on your knees and let's praise the mighty Potato!",
        "pepol": "Nazimod sighted, take cover!",
        "mrshu": "Hide yo codes, hide yo wife, nazireviewer is on site!",
        "jakubn": "Swiggidy swooty, he's comin' for dat booty!",
        "kalerab": "Hide your apples, 'cause he's gonna eat 'em!"
    }
}


@event
def auto_welcome(event):
    if event.event_type == 'join':
        if event.source_room in welcomes_db:
            welcomes = welcomes_db[event.source_room]
            # .lower() is a temporary fix for differences between lowercase
            # and uppercase name maching
            nick = event.meta['nick'].lower()

            if nick in welcomes:
                return welcomes[nick]
        return event.meta['nick'] + ': hi!'


# math functions need to be imported at runtime
from math import *  # NOQA
safe_list = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
             'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot',
             'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin',
             'sinh', 'sqrt', 'tan', 'tanh']
safe_dict = dict([(k, locals().get(k, None)) for k in safe_list])

# global builtin functions which are not in locals()
safe_dict['abs'] = abs
safe_dict['float'] = float
safe_dict['int'] = int


@cmd(command='eval')
def eval_(event):
    # the name eval_ is used in order to avoid clashing with the built-in eval
    # function which is actually how the eval command is implemented.

    """Evaluates user specified (mathematical) expression.

    Usage:

        !eval [input ...]

    Examples:

        !eval 5**2
        > 25
    """

    input = ' '.join(event.args)
    if len(input) < 1:
        return

    try:
        return eval(input, {"__builtins__": None}, safe_dict)
    except Exception as e:
        return "eval: {0}".format(e)


last_events = {}


@event
def sub_event_catcher(event):
    if event.event_type in ['message', 'cmd']:
        last_events[event.meta['host']] = event


@match(regex=r'^s(.)(.*?)\1(.*?)(?:\1(.+?))?$')
def sub_match(event, sep, pattern, replacement, flags, *args, **kwargs):
    '''Matches any substitute string (as sed would), applies this substitution to
    the user's last message and sents it back to processing.
    '''
    host = event.meta['host']
    if host not in last_events:
        return

    if flags is None:
        flags = ''

    event = last_events[host]
    details = event.raw_details
    flag = 0
    count = 1
    if 'g' in flags:
        count = 0
    if 'i' in flags:
        flag = re.IGNORECASE

    details['meta']['body'] = re.sub(pattern,
                                     replacement,
                                     details['meta']['body'],
                                     count,
                                     flag)

    evt = event.source_bot.build_event(details)
    event.source_bot.new_event(evt)
    return 'Reprocessing: {0}: {1}'.format(details['meta']['nick'],
                                           details['meta']['body'])
