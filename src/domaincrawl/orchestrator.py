from collections import namedtuple
from threading import RLock

PageFetchResult = namedtuple('PageFetchResult',['status','body','path','error','response_code'])

class CrawlOrchestrator:

    def __init__(self, executor, logger, termination_cond_var, extract_links, link_aggregator, fetch_page):
        self._link_aggregator = link_aggregator
        self._logger = logger
        self._extract_links = extract_links
        self._executor = executor
        self._fetch_page = fetch_page
        self._termination_cond = termination_cond_var
        self._inflight_futures = {}
        self._lock = RLock()
        self._inflight_page_fetches = 0

    def init_crawl(self, url):
        self._logger.info("Initiating crawl with base url %s", url)
        self._lookup_links([url], None)

# PageFetchResult = namedtuple('PageFetchResult',['status','body','path','error','response_code'])
    def handle_page_fetch_result(self, fetch_result):
        with self._lock:
            try:
                self._inflight_page_fetches -= 1
                self._logger.info("Processing page fetch response for path: %s "%fetch_result.path)
                if fetch_result.status:
                    self._logger.debug("Submitting job to extract links for page successfully extracted at path: %s "%fetch_result.path)
                    future = self._executor.submit(self._extract_links,fetch_result.path, fetch_result.body, self._logger)
                    self._inflight_futures[future] = fetch_result.path
                    future.add_done_callback(self._page_parse_callback)
            finally:
                self._notify_if_complete()

    def _page_parse_callback(self, future):
        with self._lock:
            try:
                path = self._inflight_futures.pop(future, None)
                exception = future.exception()
                if exception is not None:
                    self._logger.debug("Encountered exception %s encountered parsing contents of page at path %s"%(str(exception),path))
                else:
                    links = future.result()
                    self._lookup_links(links, path)
            finally:
                self._notify_if_complete()

    def _lookup_links(self, links, path):
        with self._lock:
            filtered_links = self._link_aggregator.filter_update_links(links, path)
            self._logger.debug(
                "Obtained filtered links of size %d from raw links of size %d . Initiating lookups if any." % (
                len(filtered_links), len(links)))
            for link in filtered_links:
                self._fetch_page(link)
                self._inflight_page_fetches += 1
                self._logger.debug("Inflight page fetches: %d" % self._inflight_page_fetches)

    def _notify_if_complete(self):
        if (len(self._inflight_futures) == 0 and self._inflight_page_fetches == 0):
            self._logger.info("Site crawl completed. Notifying listener")
            self._termination_cond.set()

