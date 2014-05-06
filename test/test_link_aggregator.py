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
        valid_links = ["/a/b","/a/b/./","http://acme.com:8002/a","https://acme.com:8002/b?q=asd#frag"]
        expected_links = ["http://acme.com:8999/a/b","http://acme.com:8002/a","https://acme.com:8002/b"]

        # This time, we also specify a referrer page
        filtered_links = link_aggregator.filter_update_links(valid_links, normalized_url)
        self.assertListEqual(expected_links,filtered_links)
        self.assertSetEqual(set(expected_links),link_aggregator._links)

        # Second invocation should result in deduplication
        filtered_links = link_aggregator.filter_update_links(valid_links, None)
        self.assertTrue(len(filtered_links) == 0)
        self.assertSetEqual(set(expected_links),link_aggregator._links)

        # None of the invalid links should pass
        invalid_links = ["mailto://user@mail.com","code.acme.com","code.acme.com/b","https://127.122.9.1"]
        filtered_links = link_aggregator.filter_update_links(invalid_links, None)
        self.assertTrue(len(filtered_links) == 0)
        self.assertSetEqual(set(expected_links),link_aggregator._links)

        # A new valid link should pass
        new_valid_links = ["http://acme.com:8999/"]
        filtered_links = link_aggregator.filter_update_links(new_valid_links, None)
        expected_result = ["http://acme.com:8999"]
        self.assertListEqual(expected_result,filtered_links)
        expected_result_set = set(expected_links)
        expected_result_set.update(set(expected_result))
        self.assertSetEqual(expected_result_set,link_aggregator._links)

        self.assertEqual(len(expected_result_set), site_graph.num_nodes())
        for link in expected_result_set:
            self.assertTrue(site_graph.has_vertex(link))

        self.assertEqual(len(expected_links), site_graph.num_edges())
        for link in expected_links:
            self.assertTrue(site_graph.has_edge(normalized_url, link))
