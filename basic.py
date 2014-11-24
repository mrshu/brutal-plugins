
from brutal.core.plugin import BotPlugin, cmd, event, match, threaded


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


welcomes = {
    "LordPotato_":
        "Everybody on your knees and let's praise the mighty Potato!",
    "pepol": "Nazimod sighted, take cover!",
    "mrshu": "Hide yo codes, hide yo wife, nazireviewer is on site!",
    "jn_": "Swiggidy swooty, he's comin' for dat booty!",
    "kalerab": "Hide your apples, 'cause he's gonna eat 'em!"
}


@event
def auto_welcome(event):
    if event.event_type == 'join':
        if event.meta['nick'] in welcomes:
            return welcomes[event.meta['nick']]
        else:
            return event.meta['nick'] + ': hi!'


# math functions need to be imported at runtime
from math import *
safe_list = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
             'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot',
             'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin',
             'sinh', 'sqrt', 'tan', 'tanh']
safe_dict = dict([(k, locals().get(k, None)) for k in safe_list])

# abs is a global builtin function and so it is not in locals()
safe_dict['abs'] = abs


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

    return eval(input, {"__builtins__": None}, safe_dict)
