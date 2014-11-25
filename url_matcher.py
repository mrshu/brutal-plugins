from readability.readability import Document
import requests
import re

from brutal.core.plugin import match, threaded

URL_REGEX = '.*((:?https?|ftp)://[^\s/$.?#].[^\s]*).*'
TAG_RE = re.compile(r'<[^>]+>')
WHITESPACE_RE = re.compile(r'\s\s+')


@threaded
@match(regex=URL_REGEX)
def url_matcher(event, url, *args, **kwargs):
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
