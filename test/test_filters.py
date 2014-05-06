import unittest
import logging

from domaincrawl.link_filters import DomainFilter, is_acceptable_url_scheme


class FilterTest(unittest.TestCase):

    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')

    def test_domain_filter(self):
        base_domain = "acme.com"
        accepted_urls = ['http://acme.com:8999/foo/bar','http://www.acme.com/bar/baz',
                              'http://user@www.acme.com/bar/baz', "http://www.acme.com:9007",
                              "https://www.acme.com:80"]
        rejected_urls = ['http://acmea.com:8999/foo/bar','http://www.acm.com/bar/baz',
                              '/bar/baz', 'http://www.mail.acme.com:8999/foo/bar',
                              'http://soap.acme.com/foo/bar','://acme.com:8999/foo/bar',
                              'http:///bar/baz', 'http://user@/bar/baz', 'http://:9007/foo',
                              '','/']
        filter = DomainFilter(base_domain, logging.getLogger())
        for url in accepted_urls:
            logging.debug("Testing positive case of domain filtering with url %s"%url)
            self.assertTrue(filter.passes(url))

        for url in rejected_urls:
            logging.debug("Testing negative case of domain filtering with url %s"%url)
            self.assertFalse(filter.passes(url))

    def test_url_scheme_filter(self):
        accepted_urls = ['http://acme.com:8999/foo/bar','hTTp://www.acme.com/bar/baz',
                              'https://user@www.acme.com/bar/baz', 'http:///bar/baz']
        rejected_urls = ['://acmea.com:8999/foo/bar','httpd://www.acm.com/bar/baz',
                              '/bar/baz', 'www.mail.acme.com:8999/foo/bar',
                              'ftp://soap.acme.com/foo/bar','','/']
        for url in accepted_urls:
            logging.debug("Testing positive case of scheme filtering with url %s"%url)
            self.assertTrue(is_acceptable_url_scheme(url))

        for url in rejected_urls:
            logging.debug("Testing negative case of scheme filtering with url %s"%url)
            self.assertFalse(is_acceptable_url_scheme(url))
