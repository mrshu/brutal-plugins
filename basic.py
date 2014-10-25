
from brutal.core.plugin import BotPlugin, cmd, event, match, threaded


@cmd
def ping(event):
    return 'pong'


@cmd
def echo(event):
    return ' '.join(event.args)


@event
def auto_welcome(event):
    if event.event_type == 'join':
        return event.meta['nick'] + ': hi!'
