from pygraph.classes.digraph import digraph

class SiteGraph:

    def __init__(self, logger):
        self._logger = logger
        self._graph = digraph()

    def add_link(self, src, dest, src_node_attrs=[], dest_node_attrs = [], edge_attrs=[]):

        if not self._graph.has_node(dest):
            self._graph.add_node(dest, dest_node_attrs)

        if not src:
            if not self._graph.has_node(src):
                self._graph.add_node(src, src_node_attrs)

        if not self._graph.has_edge(tuple([src, dest])):
            self._graph.add_edge(tuple([src, dest]), 1, "", edge_attrs)

    def stringize(self):
        return str(self._graph)