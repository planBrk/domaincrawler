from HTMLParser import HTMLParser

def extract_links(path, html, logger):
    extractor = HREFExtractor(logger)
    extractor.feed(html)
    return extractor.links()


def get_href(attrs):
    for attr, value in attrs:
        if attr == 'href':
            return value
    return None


class HREFExtractor(HTMLParser):

    def __init__(self, logger):
        HTMLParser.__init__(self)
        self._links = set()
        self._logger = logger

    def handle_starttag(self, tag, attrs):
        if 'a' == tag:
            self._logger.debug("Encountered an anchor tag. Attrs %s"%str(attrs))
            link = get_href(attrs)
            if link is not None:
                if not link in self._links:
                    self._links.add(link)

    def links(self):
        return self._links