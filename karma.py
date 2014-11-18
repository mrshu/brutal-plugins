
from brutal.core.plugin import cmd, match
import collections

karmas = collections.Counter()


@match(regex=r'^([a-zA-Z0-9_]+)((:?\+)+)$')
def karma_inc(event, name, pluses, *args):
    if name == event.meta['nick']:
        return 'Not in this universe, maggot!'
    else:
        karmas[name] += len(pluses)//2


@match(regex=r'^([a-zA-Z0-9_]+)((:?\-)+)$')
def karma_dec(event, name, minuses, *args):
    if name == event.meta['nick']:
        return 'Not in this universe, maggot!'
    else:
        karmas[name] -= len(minuses)//2


@cmd
def karma(event):
    """Returns karma points for a given user."""
    args = event.args

    if len(args) < 1:
        user = event.meta['nick']
    else:
        user = event.args[0]

    if user not in karmas:
        karmas[user] = 0

    return "{0}'s karma level is: {1}".format(user, karmas[user])


@cmd
def top_karma(event):
    """Returns 5 people with most karma points."""
    output = ""
    karmees = sorted([(value, key) for (key, value) in karmas.items()],
                     reverse=True)
    # Takes top 5 or less if len(karmees) < 5
    karmees = karmees[:5]

    for pos, (k, v) in enumerate(karmees, start=1):
        output += "{0}. {1} with {2}\n".format(pos, v, k)

    return output
