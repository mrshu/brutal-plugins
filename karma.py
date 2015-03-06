from brutal.core.plugin import BotPlugin, cmd, match


class Karma(BotPlugin):
    def setup(self, *args, **kwargs):
        self.karmas = self.open_storage('karma')

    @match(regex=r'^([a-zA-Z0-9_]+)((:?\+)+)$')
    def karma_inc(self, event, name, pluses, *args):
        if name == event.meta['nick']:
            return 'Not in this universe, maggot!'
        else:
            if name not in self.karmas:
                self.karmas[name] = 0
            self.karmas[name] += len(pluses)//2

    @match(regex=r'^([a-zA-Z0-9_]+)((:?\-)+)$')
    def karma_dec(self, event, name, minuses, *args):
        if name == event.meta['nick']:
            return 'Not in this universe, maggot!'
        else:
            if name not in self.karmas:
                self.karmas[name] = 0
            self.karmas[name] -= len(minuses)//2

    @cmd
    def karma(self, event):
        """Get karma points for a given user."""
        args = event.args

        if len(args) < 1:
            user = event.meta['nick']
        else:
            user = event.args[0]

        if user not in self.karmas:
            self.karmas[user] = 0

        return "{0}'s karma level is: {1}".format(user, self.karmas[user])

    @cmd
    def top_karma(self, event):
        """Get 5 people with most karma points."""
        output = ""
        inverted = [(value, key) for (key, value) in self.karmas.items()]
        karmees = sorted(inverted, reverse=True)
        # Takes top 5 or less if len(karmees) < 5
        karmees = karmees[:5]

        for pos, (k, v) in enumerate(karmees, start=1):
            output += "{0}. {1} with {2}\n".format(pos, v, k)

        return output
