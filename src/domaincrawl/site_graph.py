from pygraph.classes.digraph import digraph

class SiteGraph:

    def __init__(self, logger):
        self._logger = logger
        self._graph = digraph()

    def add_link(self, src, dest, src_node_attrs=[], dest_node_attrs = [], edge_attrs=[]):

        if not dest:
            self._logger.warn("Got null destination page to add to graph. Ignoring...")
            return

        if not self._graph.has_node(dest):
            self._graph.add_node(dest, dest_node_attrs)

        if src:
            if not self._graph.has_node(src):
                self._graph.add_node(src, src_node_attrs)
            if not self._graph.has_edge(tuple([src, dest])):
                self._graph.add_edge(tuple([src, dest]), 1, "", edge_attrs)

    def stringize(self):
        return str(self._graph)

    def has_vertex(self, node_str):
        return self._graph.has_node(node_str)

    def has_edge(self, src, dest):
        return self._graph.has_edge((src, dest))

    def num_nodes(self):
        return len(self._graph.nodes())

    def num_edges(self):
        return len(self._graph.edges())