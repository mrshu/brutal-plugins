from brutal.core.plugin import BotPlugin
from pyshorteners.shorteners import Shortener
import feedparser
import hashlib


class RSSPlugin(BotPlugin):
    RSS_MSG_FORMAT = '{0} > {1} > {2}'

    def setup(self, *args, **kwargs):
        self.storage = self.open_storage('rss')
        self.feeds = self.config['feeds']
        self.max_stories = int(self.config.get('max_stories', 5))
        self.update_interval = int(self.config.get('update_interval', 30))
        self.max_link_length = int(self.config.get('max_link_length', 50))
        self.entry_cache_size = int(self.config.get('entry_cache_size', 100))

        self.shortener = Shortener('IsgdShortener')

        for feed in self.feeds:
            if feed not in self.storage:
                self.storage[feed] = []
        self.loop_task(self.update_interval, self.check_feeds, now=False)

    def hash_entry(self, entry):
        """Creates a hash out of the feedparser's Entry. Uses just the title
        and the link as that is what we care about in most cases."""
        return hashlib.sha224("{}{}".format(entry.title,
                                            entry.link)).hexdigest()

    def check_feeds(self):
        """"Periodically checks for new entries in given (configured) feeds."""
        for feed in self.feeds:
            d = feedparser.parse(feed)
            past_entries = self.storage[feed]

            i = 1
            for entry in d.entries:
                hash = self.hash_entry(entry)
                if hash in past_entries:
                    continue

                if i > self.max_stories:
                    break

                self.delay_task(i, self.sender(d, entry))
                i += 1
                past_entries.insert(0, hash)
            self.storage[feed] = past_entries[:self.entry_cache_size]
        return ''

    def sender(self, d, entry):
        """A helper function that takes care of sending the entry that we
        regard as 'new' to proper places. Moreover, it takes care of formatting
        the raw entry into textual representation and shortening the entry
        link if it is too long."""
        link = entry.link
        if len(link) > self.max_link_length:
            link = self.shortener.short(link)

        s = self.RSS_MSG_FORMAT.format(d.feed.title,
                                       entry.title,
                                       link)
        self.msg(s)
