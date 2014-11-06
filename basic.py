
from brutal.core.plugin import BotPlugin, cmd, event, match, threaded


@cmd
def ping(event):
    """Responds 'pong' to your 'ping'."""

    return 'pong'


@cmd
def echo(event):
    """Echoes back the message it recieves."""
    return ' '.join(event.args)


welcomes = {
    "LordPotato_": "Everybody on your knees and let's praise the mighty Potato!",
    "pepol": "Nazimod sighted, take cover!",
    "mrshu": "Hide yo codes, hide yo wife, nazireviewer is on site!",
    "jn_": "Swiggidy swooty, he's comin' for dat booty!",
    "kalerab" : "Hide your apples, 'cause he's gonna eat 'em!"
}

@event
def auto_welcome(event):
    if event.event_type == 'join':
    	if event.meta['nick'] in welcomes:
            return welcomes[event.meta['nick']]
        else:
            return event.meta['nick'] + ': hi!'
