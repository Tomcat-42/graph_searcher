import numpy as np
from ..edge import Edge


class Vertex:
    """
    Superclass for vertices of directed and non-directed graphs.

    Each vertex has:
        - ``name``
        - ``label`` an int indicating which graph component contains it
        - ``_edgelist`` a list of edge objects that connect this vertex to others
        - ``coord`` the coordinate in an embedded graph (optional)
    """

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
        """
        Neighbours of a vertex

        ``v.neighbours()`` is a list of neighbours of this vertex.

        .. note:: For a directed graph the neighbours are those on edges leaving this vertex
        """
        return [e.next(self) for e in self._edgelist]

    def neighbors(self):
        """
        Neighbors of a vertex

        ``v.neighbors()`` is a list of neighbors of this vertex.

        .. note:: For a directed graph the neighbours are those on edges leaving this vertex
        """
        return [e.next(self) for e in self._edgelist]

    def isneighbour(self, vertex):
        """
        Test if vertex is a neigbour

        :param vertex: vertex reference
        :type vertex: Vertex subclass
        :return: true if a neighbour
        :rtype: bool

        For a directed graph this is true only if the edge is from ``self`` to
        ``vertex``.
        """
        return vertex in [e.next(self) for e in self._edgelist]

    def incidences(self):
        """
        Neighbours and edges of a vertex

        ``v.incidences()`` is a generator that returns a list of incidences,
        tuples of (vertex, edge) for all neighbours of the vertex ``v``.

        .. note:: For a directed graph the edges are those leaving this vertex
        """
        return [(e.next(self), e) for e in self._edgelist]

    def connect(self, dest, edge=None, cost=None, data=None):
        """
        Connect two vertices with an edge

        :param dest: The vertex to connect to
        :type dest: ``Vertex`` subclass
        :param edge: Use this as the edge object, otherwise a new ``Edge``
                     object is created from the vertices being connected,
                     and the ``cost`` and ``edge`` parameters, defaults to None
        :type edge: ``Edge`` subclass, optional
        :param cost: the cost to traverse this edge, defaults to None
        :type cost: float, optional
        :param data: reference to arbitrary data associated with the edge,
                     defaults to None
        :type data: Any, optional
        :raises TypeError: vertex types are different subclasses
        :return: the edge connecting the vertices
        :rtype: Edge

        ``v1.connect(v2)`` connects vertex ``v1`` to vertex ``v2``.

        .. note::

            - If the vertices subclass ``UVertex`` the edge is undirected, and if
              they subclass ``DVertex`` the edge is directed.
            - Vertices must both be of the same ``Vertex`` subclass

        :seealso: :meth:`Edge`
        """

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

    def edgeto(self, dest):
        """
        Get edge connecting vertex to specific neighbour

        :param dest: a neigbouring vertex
        :type dest: ``Vertex`` subclass
        :raises ValueError: ``dest`` is not a neighbour
        :return: the edge from this vertex to ``dest``
        :rtype: Edge

        .. note::

            - For a directed graph ``dest`` must be at the arrow end of the edge
        """
        for (n, e) in self.incidences():
            if n is dest:
                return e
        raise ValueError("dest is not a neighbour")

    def edges(self):
        """
        All outgoing edges of vertex

        :return: List of all edges leaving this vertex
        :rtype: list of Edge

        .. note::

            - For a directed graph the edges are those leaving this vertex
            - For a non-directed graph the edges are those leaving or entering
                this vertex
        """
        return self._edgelist

    def heuristic_distance(self, v2):
        return self._graph.heuristic(self.coord - v2.coord)

    def distance(self, coord):
        """
        Distance from vertex to point

        :param coord: coordinates of the point
        :type coord: ndarray(n) or Vertex
        :return: distance
        :rtype: float

        Distance is computed according to the graph's metric.

        :seealso: :meth:`metric`
        """
        if isinstance(coord, Vertex):
            coord = coord.coord
        return self._graph.metric(self.coord - coord)

    @property
    def degree(self):
        """
        Degree of vertex

        :return: degree of the vertex
        :rtype: int

        Returns the number of edges connected to the vertex.

        .. note:: For a ``DGraph`` only outgoing edges are considered.

        :seealso: :meth:`edges`
        """
        return len(self.edges())

    @property
    def x(self):
        """
        The x-coordinate of an embedded vertex

        :return: The x-coordinate
        :rtype: float
        """
        return self.coord[0]

    @property
    def y(self):
        """
        The y-coordinate of an embedded vertex

        :return: The y-coordinate
        :rtype: float
        """
        return self.coord[1]

    @property
    def z(self):
        """
        The z-coordinate of an embedded vertex

        :return: The z-coordinate
        :rtype: float
        """
        return self.coord[2]

    def closest(self):
        return self._graph.closest(self.coord)
