from graph_searcher.data_structures.edge import Edge

from .vertex import Vertex


class UndirectedVertex(Vertex):
    """
    Vertex subclass for undirected graphs

    This class can be inherited to provide user objects with graph capability.


    .. inheritance-diagram:: UVertex

    """

    def connect(self, other, **kwargs):

        if isinstance(other, Vertex):
            e = super().connect(other, **kwargs)
        elif isinstance(other, Edge):
            e = super().connect(edge=other)
        else:
            raise TypeError("bad argument")

        # e = super().connect(other, **kwargs)

        self._edgelist.append(e)
        other._edgelist.append(e)
        self._graph._edgelist.add(e)

        return e
