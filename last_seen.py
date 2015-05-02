from brutal.core.plugin import BotPlugin, cmd, event
from datetime import datetime


class LastSeen(BotPlugin):
    def setup(self, *args, **kwargs):
        self.seen = self.open_storage('last_seen')

    @event
    def seen_evt(self, event):
        events = ['quit', 'part', 'kick', 'join', 'rename', 'topic', 'message']
        if event.event_type in events:
            nick = event.meta['nick']
            self.seen[nick] = (event.event_type, datetime.utcnow())

    @cmd
    def last_seen(self, event):
        """Return last activity and its time of given user.

        Examples:
            !last_seen <user>
        """
        args = event.args
        if len(args) < 1:
            return 'Nick not specified. (usage: {0}last_seen <nick>)'.format(
                    event.source_bot.command_token)
        user = args[0]

        if user not in self.seen:
            return 'We have not seen {0} yet.'.format(user)

        evt, time = self.seen[user]
        diff_time = datetime.utcnow() - time

        if diff_time.days == 0:
            hours = diff_time.seconds // 3600
            minutes = (diff_time.seconds - (hours * 3600)) // 60

            min_format = 'minute' if minutes == 1 else 'minutes'
            if hours > 0:
                hour_format = 'hour' if hours == 1 else 'hours'
                msg = '{0} {1} and {2} {3}'.format(hours, hour_format,
                                                   minutes, min_format)
            elif minutes > 0:
                msg = '{0} {1}'.format(minutes, min_format)
            else:
                msg = 'less than a minute'
            return '{0} was last seen {1} ago ({2})'.format(user, msg, evt)

        time = time.strftime('%d.%m.%Y %H:%M')
        return '{0} was last seen at {1} UTC ({2})'.format(user, time, evt)
