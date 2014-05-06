from urlparse import urlparse
from collections import namedtuple
from threading import Thread
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest

from util import invoke_callback


PageFetchResult = namedtuple('PageFetchResult',['status','body','path','error','response_code'])

class PageFetcher:
    def __init__(self, config, logger):
        # TODO: Addtnl params to HTTPRequest need to be moved out & made configurable
        self._connect_timeout = config.connect_timeout
        self._response_timeout = config.response_timeout
        self._max_page_size = config.max_page_charlen
        self._max_redirects = config.max_redirects
        self._logger = logger
        self._fetch_result_handler = None
        io_loop_forker = Thread(target=IOLoop.instance().start)
        io_loop_forker.start()

    def set_fetch_result_handler(self, fetch_result_handler):
        if (self._fetch_result_handler is None):
            self._fetch_result_handler = fetch_result_handler

    def fetch_page(self, url):
        if self._fetch_result_handler is None:
            raise AttributeError("The fetch_result_handler attribute needs to be set before PageFetcher can be used")
        request = HTTPRequest(url, connect_timeout=self._connect_timeout, request_timeout=self._response_timeout, follow_redirects=True, max_redirects=self._max_redirects, validate_cert=False)
        http_client = AsyncHTTPClient()
        self._logger.debug("Initiating HTTP request to url %s "%(str(request.url)))
        http_client.fetch(request, self._page_fetch_callback)

    def _page_fetch_callback(self, response):
        is_fetch_successful = False
        response_code = None
        response_body = None
        error = response.error
        parsed_req_url = urlparse(response.request.url)
        req_url_path = parsed_req_url
        request_url_path = None
        self._logger.info("Received callback after fetching URL: %s"% str(response.request.url))
        if error is not None:
            self._logger.warn("Encountered error fetching page %s ." % req_url_path)
            invoke_callback(self._fetch_result_handler, self._logger, PageFetchResult(is_fetch_successful, response_body, request_url_path, error, response_code))
            return
        response_code = response.code
        self._logger.debug("Proceeding to read response code")
        self._logger.debug("Received response %d fetching page %s ." % (response_code, req_url_path))
        if response_code == 200:
            request_url_path = response.request.url
            self._logger.debug("Configured max page size %d, response body size %d ." % (self._max_page_size, len(response.body)))
            if len(response.body) <= self._max_page_size:
                is_fetch_successful = True
                response_body = response.body
                self._logger.debug("Successfully looked up body for the url")
        fetch_result = PageFetchResult(is_fetch_successful, response_body, request_url_path, error, response_code)
        invoke_callback(self._fetch_result_handler, self._logger, fetch_result)

    def shutdown(self):
        self._logger.debug("Stopping IOLoop")
        IOLoop.instance().stop()