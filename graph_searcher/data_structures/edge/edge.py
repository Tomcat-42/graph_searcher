class Edge:
    """
    Edge class

    Is used to represent directed directed and undirected edges.

    Each edge has:
    - ``cost`` cost of traversing this edge, required for planning methods
    - ``data`` reference to arbitrary data associated with the edge
    - ``v1`` first vertex, start vertex for a directed edge
    - ``v2`` second vertex, end vertex for a directed edge

    .. note::

        - An undirected graph is created by having a single edge object in the
          edgelist of _each_ vertex.
        - This class can be inherited to provide user objects with graph capability.
        - Inheritance is an alternative to providing arbitrary user data.

    An Edge points to a pair of vertices.  At ``connect`` time the vertices
    get references back to the Edge object.

    ``graph.add_edge(v1, v2)`` calls ``v1.connect(v2)``
    """

    def __init__(self, v1=None, v2=None, cost=None, data=None):
        """
        Create an edge object

        :param v1: start of the edge, defaults to None
        :type v1: Vertex subclass, optional
        :param v2: end of the edge, defaults to None
        :type v2: Vertex subclass, optional
        :param cost: edge cost, defaults to None
        :type cost: any, optional
        :param data: edge data, defaults to None
        :type data: any, optional

        Creates an edge but does not connect it to the vertices or add it to the
        graph.

        If vertices are given, and have associated coordinates, the edge cost
        will be computed according to the distance measure associated with the
        graph.

        ``data`` is a way of associating any object with the edge, its value
        can be found as the ``.data`` attribute of the edge.  An alternative
        approach is to subclass the ``Edge`` class.

        .. note:: To compute edge cost from the vertices, the vertices must have
            been added to the graph.

        :seealso: :meth:`Edge.connect` :meth:`Vertex.connect`
        """
        self.v1 = v1
        self.v2 = v2

        self.data = data

        # try to compute edge cost as metric distance if not given
        if cost is not None:
            self.cost = cost
        elif not (v1 is None or v1.coord is None or v2 is None
                  or v2.coord is None):
            self.cost = v1._graph.metric(v1.coord - v2.coord)
        else:
            self.cost = None

    def __repr__(self):
        return str(self)

    def __str__(self):

        s = f"Edge{{{self.v1} -- {self.v2}, cost={self.cost:.4g}}}"
        if self.data is not None:
            s += f" data={self.data}"
        return s

    def connect(self, v1, v2):
        """
        Add edge to the graph

        :param v1: start of the edge
        :type v1: Vertex subclass
        :param v2: end of the edge
        :type v2: Vertex subclass

        The edge is added to the graph and connects vertices ``v1`` and ``v2``.

        .. note:: The vertices must already be added to the graph.
        """

        if v1._graph is None:
            raise ValueError("vertex v1 does not belong to a graph")
        if v2._graph is None:
            raise ValueError("vertex v2 does not belong to a graph")
        if not v1._graph is v2._graph:
            raise ValueError("vertices must belong to the same graph")

        # connect edge to its vertices
        self.v1 = v1
        self.v2 = v2

        # tell the vertices to add edge to their edgelists as appropriate for
        # DGraph or UGraph
        v1.connect(v2, edge=self)

    def next(self, vertex):
        """
        Return other end of an edge

        :param vertex: one vertex on the edge
        :type vertex: Vertex subclass
        :raises ValueError: ``vertex`` is not on the edge
        :return: the other vertex on the edge
        :rtype: Vertex subclass

        ``e.next(v1)`` is the vertex at the other end of edge ``e``, ie. the
        vertex that is not ``v1``.
        """

        if self.v1 is vertex:
            return self.v2
        elif self.v2 is vertex:
            return self.v1
        else:
            raise ValueError("shouldnt happen")

    def vertices(self):
        raise DeprecationWarning("use endpoints instead")

    @property
    def endpoints(self):
        return [self.v1, self.v2]

    # def remove(self):
    #     """
    #     Remove edge from graph

    #     ``e.remove()`` removes ``e`` from the graph, but does not delete the
    #     edge object.
    #     """
    #     # remove this edge from the edge list of both end vertices
    #     if self in self.v1._edgelist:
    #         self.v1._edgelist.remove(self)
    #     if self in self.v2._edgelist:
    #         self.v2._edgelist.remove(self)

    #     # indicate that connectivity has changed
    #     self.v1._connectivitychange = True
    #     self.v2._connectivitychange = True

    #     # remove references to the vertices
    #     self.v1 = None
    #     self.v2 = None
