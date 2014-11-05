
from brutal.core.plugin import BotPlugin, cmd, event, match, threaded


@cmd
def ping(event):
    """Responds 'pong' to your 'ping'."""

    return 'pong'


@cmd
def echo(event):
    """Echoes back the message it recieves."""
    return ' '.join(event.args)


@event
def auto_welcome(event):
    welcomes = {
        'LordPotato_': 'All praise the mighty LordPotato_!',
        'pepol': 'Nazimod sighted, take cover!',
        'mrshu': 'Nazireviewer is here, hide your code!',
        'jn_': 'Swiggidy swooty, Im comin for dat booty!'
    }
    if event.event_type == 'join':
    	if event.meta['nick'] in welcomes['nick']:
            return welcomes['nick']
