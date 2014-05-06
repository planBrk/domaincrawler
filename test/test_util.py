import unittest
import logging

from domaincrawl.util import extract_domain_port, URLNormalizer, _is_valid_domain


class UtilTest(unittest.TestCase):

    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')

    def test_domain_extraction(self):
        test_expectation = {'httPs://www.foo.co.nz':("foo.co.nz", None),
                             ' hTTp://www.acme.com:899/kjbk ':("acme.com",899),
                            'http://bar.org:80/?q=sds+asa#frag':("bar.org",None),
                            'www.acme.com':("acme.com",None),
                            'acme.com:9004':("acme.com",9004)}

        for input, expected_result in test_expectation.items():
            actual_result = extract_domain_port(input)
            self.assertTupleEqual(actual_result, expected_result)

        invalid_scheme_urls = ["htt://foo.com", "mailto://user@host.com", "__SD@  "]
        for url in  invalid_scheme_urls:
            self.assertRaisesRegexp(ValueError,"scheme must be http or https",extract_domain_port,url)

        empty_urls = ["", None,"    "]
        for url in empty_urls:
            self.assertRaisesRegexp(ValueError,"cannot be null",extract_domain_port,url)

        null_or_empty_domains = ["http:///a","http://:9/bar"]
        for url in null_or_empty_domains:
            self.assertRaisesRegexp(ValueError,"Null or empty domain",extract_domain_port,url)

        invalid_domain_urls = ["https://www.__)2.com",
                               "http://lkjhhjjhhhlkjhhjjhhhlkjhhjjhhhlkjhhjjhhhlkjhhjjhhhlkjhhjjhhhlkjhhjjhhh."
                               + "lkjhhjjhhhlkjhhjjhhhlkjhhjjhhhlkjhhjjhhhlkjhhjjhhhlkjhhjjhhhlkjhhjjhhh.com"]
        for url in invalid_domain_urls:
            self.assertRaisesRegexp(ValueError,"Invalid domain provided",extract_domain_port,url)

    def test_norm_with_domain(self):
        normalizer = URLNormalizer("acme.com", 80)
        test_expectation = {'www.acme.com':"http://acme.com",
                            'www.acme.com:80/b':"http://acme.com/b",
                            'acme.com:80/':"http://acme.com",
                             ' hTTp://www.acme.com:80/kjbk ':'http://www.acme.com/kjbk',
                             ' /a/b ':'http://acme.com/a/b',
                             ' /page.htm ':'http://acme.com/page.htm',
                             'acme.com/a/b ':'http://acme.com/a/b',
                            'http://bar.org:80/?q=sds+asa#frag':"http://bar.org"}
        for input, expectation in test_expectation.items():
            logging.debug("Testing normalization of url: %s"%input)
            self.assertEqual(expectation, normalizer.normalize_with_domain(input))

    def test_domain_validation(self):
        valid_domains = ['acme.com', 'www.acm2e.com','acme.','localhost']
        invalid_domains = ['http://www.acme.com','acm..','....','acme.com:80','acme:80','http://acme',
                           '-acme.com', 'acme.com-','', '   ', None]
        for domain in valid_domains:
            logging.debug("Testing valid domain : %s"%domain)
            self.assertTrue(_is_valid_domain(domain))

        for domain in invalid_domains:
            logging.debug("Testing invalid domain: %s"%domain)
            self.assertFalse(_is_valid_domain(domain))
