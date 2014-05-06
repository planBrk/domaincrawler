from re import IGNORECASE
from re import compile
import string
from urlparse import urlparse, urlunparse
from robotexclusionrulesparser import RobotExclusionRulesParser
from util import ACCEPTABLE_SCHEMES, WWW_PREFIX, extract_domain_port

ROBOTS_FILE = 'robots.txt'

""" Filters out URL's that do not refer to the base domain extracted from the reference URL.
 The implication of such filtering is that URL's with IP's referred by the same domain
 may get filtered
 """
class DomainFilter:
    def __init__(self, base_domain, logger):
        self._logger = logger
        self._domain_match_regex = compile("^((" + WWW_PREFIX + ")?" + base_domain + ")$", IGNORECASE)

    # The url param is assumed to be a valid url. The caller of this function is expected to
    # ensure that
    def passes(self, url):
        split_url = urlparse(url)
        domain = split_url.hostname
        if (not domain or len(domain) == 0):
            return False
        is_allowed = (self._domain_match_regex.match(domain) is not None)
        self._logger.debug("Result of applying domain filter for url %s : %s"%(str(url), str(is_allowed)))
        return is_allowed

class RobotsURLFilter:
    def __init__(self, url, robots_fetch_timeout, user_agent, logger):
        self._logger = logger
        split_url = urlparse(url)
        split_list = list(split_url)
        split_list[2] = ROBOTS_FILE #The path at index
        robots_txt_url = str(urlunparse(tuple(split_list)))
        robots_filter = RobotExclusionRulesParser()
        logger.debug("Fetching robots filter from path: %s"%robots_txt_url)
        robots_filter.fetch(robots_txt_url, robots_fetch_timeout)
        self._robots_filter = robots_filter
        self._ua = user_agent

    def passes(self, url):
        self._logger.debug("Looking to apply robots filter to URL %s..."%(url))
        is_allowed = self._robots_filter.is_allowed(self._ua, url)
        self._logger.debug("Result of applying robots filter for url %s : %s"%(str(url), str(is_allowed)))
        return is_allowed

def is_acceptable_url_scheme(url):
    split_url = urlparse(url)
    scheme = split_url.scheme
    if scheme:
        scheme = scheme.lower()
    return scheme in ACCEPTABLE_SCHEMES
