from readability.readability import Document
import requests
import re

from brutal.core.plugin import match, threaded

# the [^\s\x0f] at the end fixes IRC coloring issue,
# see https://github.com/mrshu/brutal-plugins/issues/38
URL_REGEX = '.*((:?https?|ftp)://[^\s/$.?#].[^\s\x0f]*).*'
TAG_RE = re.compile(r'<[^>]+>')
WHITESPACE_RE = re.compile(r'\s\s+')


@threaded
@match(regex=URL_REGEX)
def url_matcher(event, url, *args, **kwargs):
    r = requests.head(url)
    # files that are too big cause trouble. Let's just ignore them.
    if r.headers['content-length'] > 5e6:
        return

    html = requests.get(url).text
    readable_article = Document(html).summary().encode("utf-8")
    readable_article = TAG_RE.sub('', readable_article)
    readable_article = WHITESPACE_RE.sub(' ', readable_article)
    readable_article = readable_article.replace('\n', ' ')
    readable_article = readable_article.replace('&#13;', '')

    if len(readable_article) > 75:
        readable_article = readable_article[:75] + '...'

    readable_title = Document(html).short_title().encode("utf-8")

    return "> " + url + " > " + readable_title + " > " + readable_article
