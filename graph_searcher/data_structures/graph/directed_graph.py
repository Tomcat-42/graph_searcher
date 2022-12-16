from .graph import Graph

class DirectedGraph(Graph):
    """
    Class for directed graphs

    .. inheritance-diagram:: DGraph
    """

    def add_vertex(self, coord=None, name=None):
        """
        Add vertex to directed graph

        :param coord: coordinate for an embedded graph, defaults to None
        :type coord: array-like, optional
        :param name: vertex name, defaults to "#i"
        :type name: str, optional
        :return: new vertex
        :rtype: DVertex

        - ``g.add_vertex()`` creates a new vertex with optional ``coord`` and
          ``name``.
        - ``g.add_vertex(v)`` takes an instance or subclass of DVertex and adds
          it to the graph
        """
        if isinstance(coord, Vertex):
            vertex = coord
        else:
            vertex = DVertex(coord=coord, name=name)
        super().add_vertex(vertex, name=name)
        return vertex

    @classmethod
    def vertex_copy(self, vertex):
        return DVertex(coord=vertex.coord, name=vertex.name)

    def _graphcolor(self):
        """
        Color the graph

        Performs a depth-first labeling operation, assigning the ``label``
        attribute of every vertex with a sequential integer starting from 0.

        This method checks the ``_connectivitychange`` attribute of all vertices
        and if any are True it will perform the coloring operation. This flag
        is set True by any operation that adds or removes a vertex or edge.

        :seealso: :meth:`nc`
        """
        if self._connectivitychange or any(
            [n._connectivitychange for n in self]):

            # color the graph

            # clear all the labels
            for vertex in self:
                vertex.label = None
                vertex._connectivitychange = False

            # initial labeling pass
            merge = {}
            nextlabel = 1
            for v in self:
                if v.label is None:
                    # no label, try to inherit one from a neighbour
                    for n in v.neighbours():
                        if n.label is not None:
                            # neighbour has a label
                            v.label = n.label
                            break

                if v.label is None:
                    # still not labeled, assign a new label
                    v.label = nextlabel
                    nextlabel += 1

                # now look for clashes
                for n in v.neighbours():
                    if n.label is None:
                        # neighbour has no label, give it this one
                        n.label = v.label
                    elif v.label != n.label:
                        # label clash, note it for merging
                        merge[n.label] = v.label

            # merge labels and find unique labels
            unique = set()
            for v in self:
                while v.label in merge:
                    v.label = merge[v.label]
                unique.add(v.label)

            final = {u: i for i, u in enumerate(unique)}
            for v in self:
                v.label = final[v.label]

        self._ncomponents = len(unique)
