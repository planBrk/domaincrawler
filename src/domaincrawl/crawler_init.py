import argparse
from threading import Event
from domaincrawl.link_aggregator import LinkAggregator
from domaincrawl.orchestrator import CrawlOrchestrator
from domaincrawl import conf
from concurrent.futures import ThreadPoolExecutor
from logging import config
from domaincrawl.page_fetcher import PageFetcher
from domaincrawl.site_graph import SiteGraph
from linkextractor import extract_links
from util import URLNormalizer, extract_domain_port
from link_filters import DomainFilter, RobotsURLFilter, is_acceptable_url_scheme
import logging

def init_crawler():
    parser = argparse.ArgumentParser(description='Start crawling a domain')
    parser.add_argument('--alt_conf_path', required=False, help='Path to a python config (without sections) that may be used to override config defaults')
    parser.add_argument('--log_conf', required=True, help='The location of the logging configuration file in the python logging config format')
    parser.add_argument('--url', required=True, help='The base url with the domain name (and not the IP) of the site to be crawled')
    input = vars(parser.parse_args())
    base_url = input['url']
    base_domain, port = extract_domain_port(base_url)
    conf_path = input.get('alt_conf_path', None)
    configuration = None
    if conf_path is None:
        configuration = conf.get_default()
    else:
        configuration = conf.from_file(conf_path)

    config.fileConfig(input['log_conf'])
    logger = logging.getLogger(configuration.logger_name)

    logger.debug("Base domain : %s"%base_domain)

    executor = ThreadPoolExecutor(max_workers=configuration.max_parser_workers)
    termination_cond_var = Event()
    url_norm = URLNormalizer(base_domain, port)
    normalized_url = url_norm.normalize_with_domain(base_url)
    logger.debug("Constructed normalized base url : %s"%normalized_url)
    robots_fetch_timeout = configuration.connect_timeout + configuration.response_timeout
    robots_filter = RobotsURLFilter(normalized_url, robots_fetch_timeout, configuration.user_agent, logger)

    domain_filter = DomainFilter(base_domain, logger)
    site_graph = SiteGraph(logger)
    link_aggregator = LinkAggregator(logger, site_graph, link_mappers=[url_norm.normalize_with_domain], link_filters=[domain_filter.passes, robots_filter.passes,is_acceptable_url_scheme])

    page_fetcher = PageFetcher(configuration, logger)
    orchestrator = CrawlOrchestrator(executor, logger, termination_cond_var, extract_links, link_aggregator, page_fetcher.fetch_page)
    page_fetcher.set_fetch_result_handler(orchestrator.handle_page_fetch_result)

    logger.info("Initiating crawl...")
    page_fetcher.fetch_page(normalized_url)
    termination_cond_var.wait()
    logger.info("Crawl complete. Shutting down...")
    page_fetcher.shutdown()
    logger.info("Site graph:")
    logger.info(site_graph.stringize())

if __name__ == "__main__":
    init_crawler()