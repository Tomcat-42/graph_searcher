from .vertex import Vertex


class DirectedVertex(Vertex):
    """
    Vertex subclass for directed graphs

    This class can be inherited to provide user objects with graph capability.

    .. inheritance-diagram:: DVertex

    """

    def connect(self, other, **kwargs):
        if isinstance(other, Vertex):
            e = super().connect(other, **kwargs)
        elif isinstance(other, Edge):
            e = super().connect(edge=other)
        else:
            raise TypeError("bad argument")

        self._edgelist.append(e)
        return e

    def remove(self):
        self._edgelist = None  # remove all references to edges
