import string
from urlparse import urlparse, urlunparse, urlsplit
import sys
from re import compile, IGNORECASE
from urlnorm.urlnorm import norm, norms
from traceback import format_exc

USER_INFO_DOMAIN_SEPARATOR = '@'
HOST_PORT_SEPARATOR = ':'
HTTP = 'http'
HTTPS = 'https'
ACCEPTABLE_SCHEMES = frozenset([HTTP, HTTPS])
WWW_PREFIX = 'www.'
DOMAIN_REGEX = "(?!-)[A-Z\d-]{1,63}(?<!-)$"
DOMAIN_MATCHER = compile(DOMAIN_REGEX, IGNORECASE)
HTTP_DEFAULT_PORT = 80
SCHEME_SEPARATOR = '://'
PATH_SEPARATOR = '/'


def is_empty(some_str):
    return (not some_str) or len(some_str.strip()) == 0

class URLNormalizer:

    def __init__(self, host, port):
        if port and port != HTTP_DEFAULT_PORT:
            self._netloc = host + HOST_PORT_SEPARATOR + str(port)
        else:
            self._netloc = host

    def normalize_with_domain(self, raw_url):
        if (raw_url is None):
            return None

        normalized_web_url = web_domain_to_scheme_url(raw_url)
        normalized_url = norms(normalized_web_url)
        url_components = urlparse(normalized_url)
        split_url = list(url_components[0:3]) #We remove the query params & fragment from the URL
        split_url.extend(['','',''])
        is_scheme_empty = is_empty(url_components.scheme)
        if is_scheme_empty:
            split_url[0] = HTTP
        is_netloc_empty = is_empty(url_components.netloc)
        if is_netloc_empty and (is_scheme_empty or (split_url[0] in ACCEPTABLE_SCHEMES)):
            split_url[1] = self._netloc
        path = split_url[2]
        if path.endswith(PATH_SEPARATOR):
            split_url[2] = path[0:len(path) - 1]
        url_with_domain = urlunparse(tuple(split_url))
        return url_with_domain

def extract_domain_port(reference_url):
    if is_empty(reference_url):
        raise ValueError("Input URL for domain extraction cannot be null")
    trimmed_url = reference_url.strip().lower()
    trimmed_url = web_domain_to_scheme_url(trimmed_url)
    raw_split_url = urlparse(trimmed_url)
    scheme = raw_split_url.scheme
    if not (scheme is None or scheme.strip().lower() in ACCEPTABLE_SCHEMES):
        raise ValueError("The URL scheme must be http or https")
    domain = raw_split_url.hostname
    if is_empty(domain):
        raise ValueError("Null or empty domain. Expected domain to be specified in the URL tuple %s "%str(raw_split_url))

    normalized_split_url = urlsplit(norms(trimmed_url))
    port = normalized_split_url.port
    if (port == HTTP_DEFAULT_PORT):
        port = None
    domain = normalized_split_url.hostname
    if domain.startswith(WWW_PREFIX):
        domain = domain[len(WWW_PREFIX):]
    if not _is_valid_domain(domain):
        raise ValueError("Invalid domain provided in the URL")
    return domain, port

def web_domain_to_scheme_url(raw_url):
    """
    Ensures that URL's without the scheme that contain web domain address of the
    form acme.com or www.acme.com are normalized to http://acme.com.
    If the url already has a scheme present, it is returned as is.
    """
    raw_url_lc = raw_url.strip().lower()
    if (raw_url_lc.startswith(WWW_PREFIX)):
        raw_url_lc = raw_url_lc[len(WWW_PREFIX):]
    elif (raw_url_lc.find(SCHEME_SEPARATOR) != -1):
        scheme = raw_url_lc.partition(SCHEME_SEPARATOR)[0]
        if is_empty(scheme):
            raw_url_lc = HTTP + SCHEME_SEPARATOR + raw_url_lc
        else:
            return raw_url_lc

    raw_url_sans_path = raw_url_lc
    if (raw_url_sans_path.find(PATH_SEPARATOR) != -1):
        raw_url_sans_path = raw_url_sans_path.partition(PATH_SEPARATOR)[0]

    raw_url_sans_port = raw_url_sans_path
    if (raw_url_sans_port.find(HOST_PORT_SEPARATOR) != -1):
        raw_url_sans_port = raw_url_sans_port.rpartition(HOST_PORT_SEPARATOR)[0]
    if _is_valid_domain(raw_url_sans_port):
        raw_url_lc = HTTP + SCHEME_SEPARATOR + raw_url_lc
    return raw_url_lc

def _is_valid_domain(domain):
    """
    Test if the given string is a valid domain.
    Note that this implies only the host portion of the domain without the port of a preceding scheme prefix
    .
    """
    if not domain or len(domain) > 255:
        return False
    if (domain.endswith(".")):
        domain = domain.rpartition(".")[0]
    return all(DOMAIN_MATCHER.match(sub_domain) for sub_domain in domain.split("."))

def invoke_callback(func, logger, *args):
    try:
        func(*args)
    except:
        logger.error("Error invoking callback with page response %s", str(sys.exc_info()))
        print format_exc()