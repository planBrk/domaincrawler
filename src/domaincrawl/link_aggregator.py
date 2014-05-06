class LinkAggregator:

    def __init__(self, logger,site_graph, link_mappers, link_filters):
        self._link_mappers = link_mappers
        self._link_filters = link_filters
        self._logger = logger
        self._links = set()
        self._site_graph = site_graph

    def filter_update_links(self, links, parent_path):
        self._logger.info("Processing %d links obtained from path %s "%(len(links), parent_path))
        transformed_links = links
        transformed_links = self.apply_maps(self._link_mappers,transformed_links)
        self._logger.debug("Transformed links: %s"%str(transformed_links))
        filtered_links = transformed_links
        filtered_links = self.apply_filters(self._link_filters, filtered_links)
        unique_links = []
        self._logger.debug("Filtered links: %s"%str(filtered_links))
        for link in filtered_links:
            self._site_graph.add_link(parent_path, link)
            if link not in self._links:
                self._links.add(link)
                unique_links.append(link)
        self._logger.debug("From %d filtered links, found & returning %d unique links "%(len(filtered_links),len(unique_links)))
        return  unique_links

    def apply_maps(self, link_mappers, links):
        transformed_links = []
        for link in links:
            transformed_link = link
            try:
                for mapper in link_mappers:
                    transformed_link = mapper(transformed_link)
                transformed_links.append(transformed_link)
            except:
                self._logger.warn("Encountered error transforming link %s . Dropping it..."%link)

    def apply_filters(self, link_filters, links):
        filtered_links = []
        for link in links:
            passes = True
            try:
                for filter in link_filters:
                    passes &= filter(link)
                    if not passes : break
                if passes:
                    filtered_links.append(link)
            except:
                self._logger.warn("Encountered error filtering link %s . Dropping it..."%link)


