from brutal.core.plugin import BotPlugin, cmd, event
from time import strftime, gmtime


class LastSeen(BotPlugin):
    def setup(self, *args, **kwargs):
        self.seen = self.open_storage('last_seen')

    @event
    def seen_evt(self, event):
        events = ['quit', 'part', 'kick', 'join', 'rename', 'topic', 'message']
        if event.event_type in events:
            nick = event.meta['nick']
            self.seen[nick] = (event.event_type, gmtime())

    @cmd
    def last_seen(self, event):
        """
        Returns when was given user last seen.

        Example: !last_seen <user>
        """
        args = event.args
        if len(args) < 1:
            return "Name argument missing."
        user = args[0]

        if user not in self.seen:
            return "This user was never here."

        evt, time = self.seen[user]
        time = strftime("%H:%M %d.%m.%Y", time)
        return "{0} was last seen: {1} GMT({2})".format(user, time, evt)
