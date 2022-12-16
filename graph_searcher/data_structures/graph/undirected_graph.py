from ..vertex import DirectedVertex, UndirectedVertex
from .graph import Graph


class UndirectedGraph(Graph):
    """
    Class for undirected graphs

    .. inheritance-diagram:: UGraph
    """

    def add_vertex(self, coord=None, name=None):
        """
        Add vertex to undirected graph

        :param coord: coordinate for an embedded graph, defaults to None
        :type coord: array-like, optional
        :param name: vertex name, defaults to "#i"
        :type name: str, optional
        :return: new vertex
        :rtype: UndirectedVertex

        - ``g.add_vertex()`` creates a new vertex with optional ``coord`` and
          ``name``.
        - ``g.add_vertex(v)`` takes an instance or subclass of UndirectedVertex and adds
          it to the graph
        """
        if isinstance(coord, UndirectedVertex):
            vertex = coord
        else:
            vertex = UndirectedVertex(coord)
        super().add_vertex(vertex, name=name)
        return vertex

    @classmethod
    def vertex_copy(self, vertex):
        return DirectedVertex(coord=vertex.coord, name=vertex.name)

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

            lastlabel = None
            for label in range(self.number_of_vertices):
                assignment = False
                for v in self:
                    # find first vertex with no label
                    if v.label is None:
                        # do BFS
                        q = [v]  # initialize frontier
                        while len(q) > 0:
                            v = q.pop()  # expand v
                            v.label = label
                            for n in v.neighbours():
                                if n.label is None:
                                    q.append(n)
                        lastlabel = label
                        assignment = True
                        break
                if not assignment:
                    break

            self._ncomponents = lastlabel + 1
