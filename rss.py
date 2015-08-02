from brutal.core.plugin import BotPlugin
from pyshorteners.shorteners import Shortener
import feedparser


class RSSPlugin(BotPlugin):
    RSS_MSG_FORMAT = '{0} > {1} > {2}'

    def setup(self, *args, **kwargs):
        self.storage = self.open_storage('rss')
        self.feeds = self.config['feeds']
        self.max_stories = int(self.config.get('max_stories', 5))
        self.update_interval = int(self.config.get('update_interval', 30))
        self.max_link_length = int(self.config.get('max_link_length', 50))

        self.shortener = Shortener('IsgdShortener')

        for feed in self.feeds:
            if feed not in self.storage:
                self.storage[feed] = ''
        self.loop_task(self.update_interval, self.check_feeds, now=False)

    def check_feeds(self):
        for feed in self.feeds:
            d = feedparser.parse(feed)
            last_id = self.storage[feed]
            first_id = None

            for i, entry in enumerate(d.entries, start=1):
                if first_id is None:
                    first_id = entry.id

                if entry.id == last_id:
                    break

                if i > self.max_stories:
                    break

                self.delay_task(i, self.sender(d, entry))
            self.storage[feed] = first_id
        return ''

    def sender(self, d, entry):
        link = entry.link
        if len(link) > self.max_link_length:
            link = self.shortener.short(link)

        s = self.RSS_MSG_FORMAT.format(d.feed.title,
                                       entry.title,
                                       link)
        self.msg(s)
