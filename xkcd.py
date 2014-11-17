"""
XKCD brutal plugins.

Provides basic commands for showing xkcd info in IRC.
"""

from brutal.core.plugin import BotPlugin, cmd
import json
import urllib


SLEEP_TIME = 3600


def get_xkcd_metadata(num=None):
    """Returns data about xkcd number 'num', or latest."""
    site_url = 'http://xkcd.com/'
    json_filename = 'info.0.json'
    if num:
        comic_selector = '{}/'.format(num)
    else:
        comic_selector = ''
    url = site_url + comic_selector + json_filename
    data = urllib.urlopen(url).read()
    data = json.loads(data)
    data['url'] = 'http://xkcd.com/' + str(data['num'])
    return data


def format_xkcd(comic_data):
    """Returns info about xkcd 'num'."""
    xkcd_info = 'xkcd #{}: {} | {}'.format(comic_data['num'],
                                           comic_data['title'],
                                           comic_data['url'])
    return xkcd_info


class XKCDPlugin(BotPlugin):
    """XKCD plugin class."""

    def setup(self, *args, **kwargs):
        self.latest = get_xkcd_metadata()

    @cmd
    def xkcd(self, event):
        """Shows details of requested xkcd.

        Args:
            If no argument is given, data of latest xkcd is given.

            If a number is given, shows data for corresponding xkcd, or n-th
            latest, if number is non-positive.

            If argument is non-numeric, or contains more than one number,
            a full-text search over explainxkcd database is performed,
            returning first found comic, if any.
        """
        args = event.args
        if len(args) < 1:
            return format_xkcd(self.latest)
        try:
            num = int(args[0])
        except ValueError:
            return "Be patient! We're getting there!"
        if num > self.latest['num']:
            return 'not yet released!'
        if num <= 0:
            # Since 'num' is negative, this basically takes num-th latest
            # comic. It's the same as self.latest['num'] - abs(num).
            num = self.latest['num'] + num
            if num <= 0:
                return 'somebody wants to go back in time way too far!'
        return format_xkcd(get_xkcd_metadata(num))
