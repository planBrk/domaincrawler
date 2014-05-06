import unittest
import logging

from domaincrawl.link_aggregator import LinkAggregator
from domaincrawl.link_filters import DomainFilter, is_acceptable_url_scheme
from domaincrawl.site_graph import SiteGraph
from domaincrawl.util import URLNormalizer, extract_domain_port


class LinkAggregatorTest(unittest.TestCase):

    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')

    def test_link_dedup(self):
        base_url = "acme.com:8999"
        base_domain, port = extract_domain_port(base_url)
        logger = logging.getLogger()
        url_norm = URLNormalizer(base_domain, port)
        normalized_url = url_norm.normalize_with_domain(base_url)
        logger.debug("Constructed normalized base url : %s"%normalized_url)

        domain_filter = DomainFilter(base_domain, logger)
        site_graph = SiteGraph(logger)
        link_aggregator = LinkAggregator(logger, site_graph, link_mappers=[url_norm.normalize_with_domain], link_filters=[domain_filter.passes, is_acceptable_url_scheme])
        link_aggregator.filter_update_links([], None)
        self.assertSetEqual(expected_set,link_aggregator._links)
