
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
        return "{0}'s karma level is: {1}".format(event.meta['nick'], 
                                                  karmas[event.meta['nick']])
    
    user = event.args[0]

    if user not in karmas:
        karmas[user] = 0
    return "{0}'s karma level is: {1}".format(user, karmas[user])


@match(regex=r'^;;$')
def karma_top(event):
    top5 = ""
    c = 1
    karmees = sorted([(value,key) for (key,value) in karmas.items()], 
                                                                  reverse=True)

    for k, v in karmees:
        if c > 5:
            break
        top5 += "{0}. {1} with {2}\n".format(c, v, k)
        c += 1

    return top5
