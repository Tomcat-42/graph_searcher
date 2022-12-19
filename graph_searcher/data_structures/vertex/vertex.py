import numpy as np

from graph_searcher.data_structures.edge import Edge


class Vertex:

    def __init__(self, coord=None, name=None):
        self._edgelist = []
        if coord is None:
            self.coord = None
        else:
            self.coord = np.r_[coord]
        self.name = name
        self.label = None
        self._connectivitychange = True
        self._edgelist = []
        self._graph = None  # reference to owning graph
        # print('Vertex init', type(self))

    def __str__(self):
        return f"[{self.name:s}]"

    def __repr__(self):
        if self.coord is None:
            coord = "?"
        else:
            coord = ", ".join([f"{x:.4g}" for x in self.coord])
        return f"{self.__class__.__name__}[{self.name:s}, coord=({coord})]"

    def copy(self, cls=None):
        if cls is not None:
            return cls.vertex_copy(self)
        else:
            return self.__class__(coord=self.coord, name=self.name)

    def neighbours(self):
        return [e.get_next_vertex(self) for e in self._edgelist]

    def isneighbour(self, vertex):
        return vertex in [e.get_next_vertex(self) for e in self._edgelist]

    def incidences(self):
        return [(e.get_next_vertex(self), e) for e in self._edgelist]

    def _connect(self, dest, edge=None, cost=None, data=None):

        if not dest.__class__.__bases__[0] is self.__class__.__bases__[0]:
            raise TypeError("must connect vertices of same type")
        elif isinstance(edge, Edge):
            e = edge
        else:
            e = Edge(self, dest, cost=cost, data=data)

        self._graph._edgelist.add(e)
        self._graph._connectivitychange = True
        self._connectivitychange = True

        return e

    def connect(self, other, **kwargs):

        if isinstance(other, Vertex):
            e = self._connect(other, **kwargs)
        elif isinstance(other, Edge):
            e = self._connect(edge=other)
        else:
            raise TypeError("bad argument")

        # e = super().connect(other, **kwargs)

        self._edgelist.append(e)
        other._edgelist.append(e)
        self._graph._edgelist.add(e)

        return e

    def edgeto(self, dest):
        for (n, e) in self.incidences():
            if n is dest:
                return e
        raise ValueError("dest is not a neighbour")

    def edges(self):
        return self._edgelist

    def heuristic_distance(self, v2):
        return np.linalg.norm(self.coord - v2.coord, 1)

    def distance(self, coord):
        if isinstance(coord, Vertex):
            coord = coord.coord
        return np.linalg.norm(self.coord - coord, 1)

    @property
    def degree(self):
        return len(self.edges())

    @property
    def x(self):
        return self.coord[0]

    @property
    def y(self):
        return self.coord[1]

    @property
    def z(self):
        return self.coord[2]

    def closest(self):
        return self._graph.closest(self.coord)
