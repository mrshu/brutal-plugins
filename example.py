"""
Examples of brutal plugins. Primarily used for testing.
"""

import time
from brutal.core.plugin import BotPlugin, cmd, event, match, threaded


@cmd
def pingni_ma(event):
    print (event.meta)
    return '{1}: pong, got {0!r}'.format(vars(event), event.meta['nick'])


@cmd
def testargs(event):
    return 'you passed in args: {0!r}'.format(event.args)


# @event(thread=True)
def sleepevent(event):
    time.sleep(7)
    return 'SOOOOOO sleepy'


@cmd(thread=True)
def sleep(event):
    time.sleep(5)
    return 'im sleepy...'


@event
def test_event_parser(event):
    print ('EVENT!!! {0!r}'.format(event),
           event.event_type,
           isinstance(event.meta, dict),
           'body' in event.meta)


@match(regex=r'^hi$')
def matcher(event):
    return 'Hello to you!'


@match(regex=r'^sieg$')
def nazi(event):
    return 'hiel!' # "hiel" so we dont go to jail


class TestPlugin(BotPlugin):

    def setup(self, *args, **kwargs):
        # print(self.log)
        self.log.debug('SETUP CALLED')

        self.log.debug('config: {0!r}'.format(self.config))

        self.storage = self.open_storage('test')

        self.counter = 0
        # self.loop_task(5, self.test_loop, now=False)
        # self.delay_task(10, self.future_task)

    def future_task(self):
        self.log.info('testing future task')
        return 'future!'

    @threaded
    def test_loop(self):
        self.log.info('testing looping task')
        return 'loop!'

    def say_hi(self, event=None):
        self.msg('from say_hi: {0!r}'.format(event), event=event)
        return 'hi'

    @threaded
    def say_delayed_hi(self, event=None):
        self.msg('from say_hi_threaded, sleeping for 5: {0!r}'.format(event),
                 event=event)
        time.sleep(5)
        return 'even more delayed hi'

    @cmd
    def runlater(self, event):
        self.delay_task(5, self.say_hi, event=event)
        self.delay_task(5, self.say_delayed_hi, event=event)
        return 'will say hi in 5 seconds'

    @cmd
    def count(self, event):
        self.counter += 1
        return 'count {1!r} from class! got {0!r}'.format(event, self.counter)

    @cmd(thread=True)
    def inlinemsg(self, event):
        self.msg('sleeping for 5 seconds!', event=event)
        time.sleep(5)
        return 'done sleeping!'

    @cmd
    def setter(self, event):
        if len(event.args) >= 2:
            self.storage[event.args[0]] = event.args[1]

    @cmd
    def getter(self, event):
        if len(event.args) >= 1:
            return self.storage[event.args[0]]

    @cmd(thread=True)
    def notify(self, event):
        args = event.args

        if len(args) < 2:
            return 'Sorry sir, I don\'t understand,' \
                   ' you gave me too few arguments'

        seconds = int(args[0])
        text = ' '.join(args[1:])

        def sender(x):
            def t():
                self.msg('Sir, I am notifying you as requested: {0}'.format(x),
                         event=event)
            return t

        self.delay_task(seconds, sender(text))

        return 'Will notify you in {0!r} seconds.'.format(seconds)
