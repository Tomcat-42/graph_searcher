import copy
import subprocess
import sys
import tempfile
import webbrowser
from abc import ABC
from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np
from spatialmath.base.graphics import axes_logic

from ..edge import Edge
from ..vertex import DirectedVertex, UndirectedVertex, Vertex


class Graph(ABC):

    def __init__(self, metric="L2", heuristic="L2", verbose=False):
        # adjacency list representation
        self._vertexlist = []
        self._vertexdict = {}
        self._edgelist = set()
        self._verbose = verbose

        self.metric = metric
        self.heuristic = heuristic

    def __str__(self):
        return f"{self.__class__.__name__}: {self.number_of_vertices} {'vertex' if self.number_of_vertices==1 else 'vertices'}, {self.number_of_edges} edge{'s'[:self.number_of_edges^1]}, {self.number_of_components} component{'s'[:self.number_of_components^1]}"

    def __getitem__(self, i):
        """
        Get vertex (superclass method)

        :param i: vertex description
        :type i: int or str
        :return: the referenced vertex
        :rtype: Vertex subclass

        Retrieve a vertex by index or name:

        -``g[i]`` is the i'th vertex in the graph.  This reflects the order of
         addition to the graph.
        -``g[s]`` is vertex named ``s``
        -``g[v]`` is ``v`` where ``v`` is a ``Vertex`` subclass

        This method also supports iteration over the vertices in a graph::

            for v in g:
                print(v)

        will iterate over all the vertices.
        """
        if isinstance(i, int):
            return self._vertexlist[i]
        elif isinstance(i, str):
            return self._vertexdict[i]
        elif isinstance(i, Vertex):
            return i

    def __repr__(self):
        s = []
        for vertex in self:
            ss = f"{vertex.name} at {vertex.coord}"
            if vertex.label is not None:
                ss += " component={vertex.label}"
            s.append(ss)
        return "\n".join(s)

    def __contains__(self, item):
        """
        Test if vertex in graph

        :param item: vertex or name of vertex
        :type item: Vertex subclass or str
        :return: true if vertex exists in the graph
        :rtype: bool

        - ``'name' in graph`` is true if a vertex named ``'name'`` exists in the
          graph.
        - ``v in graph`` is true if the vertex reference ``v`` exists in the
          graph.

        """
        if isinstance(item, str):
            return item in self._vertexdict
        elif isinstance(item, Vertex):
            return item in self._vertexdict.values()

    @classmethod
    def from_dict(cls, d, reverse=False):
        """
        Create graph from parent/child dictionary

        :param d: dictionary that maps from ``Vertex`` subclass to ``Vertex`` subclass
        :type d: dict
        :param reverse: reverse link direction, defaults to False
        :type reverse: bool, optional
        :return: graph
        :rtype: UndirectedGraph or DirectedGraph

        Behaves like a constructor for a ``DirectedGraph`` or ``UndirectedGraph`` from a
        dictionary that maps vertices to parents.  From this information it
        can create a tree graph.

        By default parent vertices are linked their children. If ``reverse`` is
        True then children are linked to their parents.
        """

        g = cls()

        for vertex, parent in d.items():
            if isinstance(vertex, str):
                vertex_name = vertex
            else:
                vertex_name = vertex.name

            if vertex_name in g:
                vertex = g[vertex_name]
            else:
                vertex = g.add_vertex(UndirectedVertex(), name=vertex_name)

            if isinstance(parent, str):
                parent_name = parent
            else:
                parent_name = parent.name
            if parent_name in g:
                parent = g[parent_name]
            else:
                parent = g.add_vertex(UndirectedVertex(), name=parent_name)

            if reverse:
                g.add_edge(vertex, parent)
            else:
                g.add_edge(parent, vertex)

        return g

    @classmethod
    def from_adjacency_matrix(cls, A, coords=None, names=None):
        """
        Create graph from adjacency matrix

        :param A: adjacency matrix
        :type A: ndarray(N,N)
        :param coords: coordinates of vertices, defaults to None
        :type coords: ndarray(N,M), optional
        :param names: names of vertices, defaults to None
        :type names: list(N) of str, optional

        :return: [description]
        :rtype: [type]

        Create a directed or undirected graph where non-zero elements ``A[i,j]``
        correspond to edges from vertex ``i`` to vertex ``j``.

        .. warning:: For undirected graph ``A`` should be symmetric but this
            is not checked.  Only the upper triangular part is used.
        """

        if A.shape[0] != A.shape[1]:
            raise ValueError("Adjacency matrix must be square")
        if names is not None and len(names) != A.shape[0]:
            raise ValueError(
                "length of names must match dimension of adjacency matrix")
        if coords is not None and coords.shape[0] != A.shape[0]:
            raise ValueError(
                "coords must have same number of rows as adjacency matrix")

        g = cls()

        name = None
        coord = None
        for i in range(A.shape[0]):
            if names is not None:
                name = names[i]
            if coords is not None:
                coord = coords[i, :]
            g.add_vertex(name=name, coord=coord)

        if isinstance(g, UndirectedGraph):
            # undirected graph
            for i in range(A.shape[0]):
                for j in range(i + 1, A.shape[1]):
                    if A[i, j] > 0:
                        g[i].connect(g[j], cost=A[i, j])
        else:
            # directed graph
            for i in range(A.shape[0]):
                for j in range(A.shape[1]):
                    if A[i, j] > 0:
                        if i == j:
                            raise ValueError("loops in graph not supported")
                        g[i].connect(g[j], cost=A[i, j])

        return g

    def copy(self):
        """
        Deepcopy of graph

        :param g: A graph
        :type g: PGraph
        :return: deep copy
        :rtype: PGraph
        """
        return copy.deepcopy(self)

    def add_vertex(self, vertex, name=None):
        """
        Add a vertex to the graph (superclass method)

        :param vertex: vertex to add
        :type vertex: Vertex subclass
        :param name: name of vertex
        :type name: str

        ``G.add_vertex(v)`` add vertex ``v`` to the graph ``G``.

        If the vertex has no name and ``name`` is None give it a default name
        ``#N`` where ``N`` is a consecutive integer.

        The vertex is placed into a dictionary with a key equal to its name.
        """
        if name is None:
            name = vertex.name
        if name is None:
            name = f"#{len(self._vertexlist)}"
        vertex.name = name
        self._vertexlist.append(vertex)
        self._vertexdict[vertex.name] = vertex
        if self._verbose:
            print(f"New vertex {vertex.name}: {vertex.coord}")
        vertex._graph = self
        self._connectivitychange = True
        return vertex

    def add_edge(self, v1, v2, **kwargs):
        """
        Add an edge to the graph (superclass method)

        :param v1: first vertex (start if a directed graph)
        :type v1: Vertex subclass
        :param v2: second vertex (end if a directed graph)
        :type v2: Vertex subclass
        :param kwargs: optional arguments to pass to ``Vertex.connect``
        :return: edge
        :rtype: Edge

        Create an edge between a vertex pair and adds it to the graph.

        This is a graph centric way of creating an edge.  The
        alternative is the ``connect`` method of a vertex.

        :seealso: :meth:`Edge.connect` :meth:`Vertex.connect`
        """
        if isinstance(v1, str):
            v1 = self[v1]
        elif not isinstance(v1, Vertex):
            raise TypeError("v1 must be Vertex subclass or string name")
        if isinstance(v2, str):
            v2 = self[v2]
        elif not isinstance(v2, Vertex):
            raise TypeError("v2 must be Vertex subclass or string name")

        if self._verbose:
            print(f"New edge from {v1.name} to {v2.name}")
        return v1.connect(v2, **kwargs)

    def remove(self, x):
        """
        Remove element from graph (superclass method)

        :param x: element to remove from graph
        :type x: Edge or Vertex subclass
        :raises TypeError: unknown type

        The edge or vertex is removed, and all references and lists are
        updated.

        .. warning:: The connectivity of the network may be changed.
        """
        if isinstance(x, Edge):
            # remove an edge

            # remove edge from the edgelist of connected vertices
            x.v1._edgelist.remove(x)
            x.v2._edgelist.remove(x)

            # indicate that connectivity has changed
            x.v1._connectivitychange = True
            x.v2._connectivitychange = True
            self._connectivitychange = True

            # remove references to the vertices
            x.v1 = None
            x.v2 = None

            # remove from list of all edges
            self._edgelist.remove(x)

        elif isinstance(x, Vertex):
            # remove a vertex

            # remove all edges of this vertex
            for edge in copy.copy(x._edgelist):
                self.remove(edge)

            # remove from list and dict of all edges
            self._vertexlist.remove(x)
            del self._vertexdict[x.name]
        else:
            raise TypeError("expecting Edge or Vertex")

    def show(self):
        print("vertices:")
        for v in self._vertexlist:
            print("  " + str(v))
        print("edges:")
        for e in self._edgelist:
            print("  " + str(e))

    @property
    def number_of_vertices(self):
        """
        Number of vertices

        :return: Number of vertices
        :rtype: int
        """
        return len(self._vertexdict)

    @property
    def number_of_edges(self):
        """
        Number of edges

        :return: Number of vertices
        :rtype: int
        """
        return len(self._edgelist)

    @property
    def number_of_components(self):
        """
        Number of components

        :return: Number of components
        :rtype: int

        .. note::

            - Components are labeled from 0 to ``g.nc-1``.
            - A graph coloring algorithm is run if the graph connectivity
              has changed.

        .. note:: A lazy approach is used, and if a connectivity changing
            operation has been performed since the last call, the graph
            coloring algorithm is run which is potentially expensive for
            a large graph.
        """
        self._graphcolor()
        return self._ncomponents

    def _metricfunc(self, metric):

        def L1(v):
            return np.linalg.norm(v, 1)

        def L2(v):
            return np.linalg.norm(v)

        def SE2(v):
            # wrap angle to range [-pi, pi)
            v[2] = (v[2] + np.pi) % (2 * np.pi) - np.pi
            return np.linalg.norm(v)

        if callable(metric):
            return metric
        elif isinstance(metric, str):
            if metric == "L1":
                return L1
            elif metric == "L2":
                return L2
            elif metric == "SE2":
                return SE2
        else:
            raise ValueError("unknown metric")

    @property
    def metric(self):
        """
        Get the distance metric for graph

        :return: distance metric
        :rtype: callable

        This is a function of a vector and returns a scalar.
        """
        return self._metric

    @metric.setter
    def metric(self, metric):
        r"""
        Set the distance metric for graph

        :param metric: distance metric
        :type metric: callable or str

        This is a function of a vector and returns a scalar.  It can be
        user defined function or a string:

        - 'L1' is the norm :math:`L_1 = \Sigma_i | v_i |`
        - 'L2' is the norm :math:`L_2 = \sqrt{ \Sigma_i v_i^2}`
        - 'SE2' is a mixed norm for vectors :math:`(x, y, \theta)` and
            is :math:`\sqrt{x^2 + y^2 + \bar{\theta}^2}` where :math:`\bar{\theta}`
            is :math:`\theta` wrapped to the interval :math:`[-\pi, \pi)`

        The metric is used by :meth:`closest` and :meth:`distance`
        """
        self._metric = self._metricfunc(metric)

    @property
    def heuristic(self):
        """
        Get the heuristic distance metric for graph

        :return: heuristic distance metric
        :rtype: callable

        This is a function of a vector and returns a scalar.
        """
        return self._heuristic

    @heuristic.setter
    def heuristic(self, heuristic):
        r"""
        Set the heuristic distance metric for graph

        :param metric: heuristic distance metric
        :type metric: callable or str

        This is a function of a vector and returns a scalar.  It can be
        user defined function or a string:

        - 'L1' is the norm :math:`L_1 = \Sigma_i | v_i |`
        - 'L2' is the norm :math:`L_2 = \sqrt{ \Sigma_i v_i^2}`
        - 'SE2' is a mixed norm for vectors :math:`(x, y, \theta)` and
            is :math:`\sqrt{x^2 + y^2 + \bar{\theta}^2}` where :math:`\bar{\theta}`
            is :math:`\theta` wrapped to the interval :math:`[-\pi, \pi)`

        The heuristic distance is only used by the A* planner :meth:`path_Astar`.
        """
        self._heuristic = self._metricfunc(heuristic)

    def closest(self, coord):
        """
        Vertex closest to point

        :param coord: coordinates of a point
        :type coord: ndarray(n)
        :return: closest vertex
        :rtype: Vertex subclass

        Returns the vertex closest to the given point. Distance is computed
        according to the graph's metric.

        :seealso: :meth:`metric`
        """
        min_dist = np.Inf
        min_which = None

        for vertex in self:
            d = self.metric(vertex.coord - coord)
            if d < min_dist:
                min_dist = d
                min_which = vertex

        return min_which, min_dist

    def edges(self):
        """
        Get all edges in graph (superclass method)

        :return: All edges in the graph
        :rtype: list of Edge references

        We can iterate over all edges in the graph by::

            for e in g.edges():
                print(e)

        .. note:: The ``edges()`` of a Vertex is a list of all edges connected
            to that vertex.

        :seealso: :meth:`Vertex.edges`
        """
        return self._edgelist

    def plot(
        self,
        colorcomponents=True,
        force2d=False,
        vopt={},
        eopt={},
        text={},
        block=False,
        grid=True,
        ax=None,
    ):
        """
        Plot the graph

        :param vopt: vertex format, defaults to 12pt o-marker
        :type vopt: dict, optional
        :param eopt: edge format, defaults to None
        :type eopt: dict, optional
        :param text: text label format, defaults to None
        :type text: False or dict, optional
        :param colorcomponents: color vertices and edges by component, defaults to None
        :type color: bool, optional
        :param block: block until figure is dismissed, defaults to True
        :type block: bool, optional

        The graph is plotted using matplotlib.

        If ``colorcomponents`` is True then each component is assigned a unique
        color.  ``vertex`` and ``edge`` cannot include a color keyword.

        If ``text`` is a dict it is used to format text labels for the vertices
        which are the vertex names.  If ``text`` is None default formatting is
        used.  If ``text`` is False no labels are added.
        """
        vopt = {**dict(marker="o", markersize=12), **vopt}
        eopt = {**dict(linewidth=3), **eopt}

        if colorcomponents:
            color = plt.cm.coolwarm(
                np.linspace(0, 1, self.number_of_components))

        if len(self[0].coord) == 2 or force2d:
            # 2D plotting
            if ax is None:
                ax = axes_logic(ax, 2)
            for c in range(self.number_of_components):
                # for each component
                for vertex in self.component(c):
                    if text is not False:
                        ax.text(vertex.x, vertex.y, "  " + vertex.name, **text)
                    if colorcomponents:
                        ax.plot(vertex.x, vertex.y, color=color[c, :], **vopt)
                        for v in vertex.neighbours():
                            ax.plot(
                                [vertex.x, v.x],
                                [vertex.y, v.y],
                                color=color[c, :],
                                **eopt,
                            )
                    else:
                        ax.plot(vertex.x, vertex.y, **vopt)
                        for v in vertex.neighbours():
                            ax.plot([vertex.x, v.x], [vertex.y, v.y], **eopt)
        else:
            # 3D or higher plotting, just do (x, y, z)
            if ax is None:
                ax = axes_logic(ax, 3)
            for c in range(self.number_of_components):
                # for each component
                for vertex in self.component(c):
                    if text is not False:
                        ax.text(vertex.x, vertex.y, vertex.z,
                                "  " + vertex.name, **text)
                    if colorcomponents:
                        ax.plot(
                            vertex.x,
                            vertex.y,
                            vertex.z,
                            **{
                                **dict(color=color[c, :]),
                                **vopt
                            },
                        )
                        for v in vertex.neighbours():
                            ax.plot(
                                [vertex.x, v.x],
                                [vertex.y, v.y],
                                [vertex.z, v.z],
                                **{
                                    **dict(color=color[c, :]),
                                    **eopt
                                },
                            )
                    else:
                        ax.plot(vertex.x, vertex.y, **vopt)
                        for v in vertex.neighbours():
                            ax.plot(
                                [vertex.x, v.x],
                                [vertex.y, v.y],
                                [vertex.z, v.z],
                                **eopt,
                            )
        # if nc > 1:
        #     # add a colorbar
        #     plt.colorbar()
        ax.grid(grid)
        plt.show(block=block)

    def highlight_path(self, path, block=False, **kwargs):
        """
        Highlight a path through the graph

        :param path: [description]
        :type path: [type]
        :param block: [description], defaults to True
        :type block: bool, optional

        The vertices and edges along the path are overwritten with a different
        size/width and color.

        :seealso: :meth:`highlight_vertex` :meth:`highlight_edge`
        """
        for i in range(len(path)):
            if i < len(path) - 1:
                e = path[i].edgeto(path[i + 1])
                self.highlight_edge(e, **kwargs)
            self.highlight_vertex(path[i], **kwargs)
        plt.show(block=block)

    def highlight_edge(self, edge, scale=2, color="r", alpha=0.5):
        """
        Highlight an edge in the graph

        :param edge: The edge to highlight
        :type edge: Edge subclass
        :param scale: Overwrite with a line this much bigger than the original,
                      defaults to 1.5
        :type scale: float, optional
        :param color: Overwrite with a line in this color, defaults to 'r'
        :type color: str, optional
        """
        p1 = edge.v1
        p2 = edge.v2
        plt.plot([p1.x, p2.x], [p1.y, p2.y],
                 color=color,
                 linewidth=3 * scale,
                 alpha=alpha)

    def highlight_vertex(self, vertex, scale=2, color="r", alpha=0.5):
        """
        Highlight a vertex in the graph

        :param edge: The vertex to highlight
        :type edge: Vertex subclass
        :param scale: Overwrite with a line this much bigger than the original,
                      defaults to 1.5
        :type scale: float, optional
        :param color: Overwrite with a line in this color, defaults to 'r'
        :type color: str, optional
        """
        if isinstance(vertex, Iterable):
            for n in vertex:
                if isinstance(n, str):
                    n = self[n]
                plt.plot(n.x,
                         n.y,
                         "o",
                         color=color,
                         markersize=12 * scale,
                         alpha=alpha)
        else:
            plt.plot(vertex.x,
                     vertex.y,
                     "o",
                     color=color,
                     markersize=12 * scale,
                     alpha=alpha)

    def dotfile(self, filename=None, direction=None):
        """
        Export graph as a GraphViz dot file

        :param filename: filename to save graph to, defaults to None
        :type filename: str, optional

        ``g.dotfile()`` creates the specified file which contains the
        `GraphViz <https://graphviz.org>`_ code to represent the embedded graph.  By default output
        is to the console.

        .. note::

            - The graph is undirected if it is a subclass of ``UndirectedGraph``
            - The graph is directed if it is a subclass of ``DirectedGraph``
            - Use ``neato`` rather than dot to get the embedded layout

        .. note:: If ``filename`` is a file object then the file will *not*
            be closed after the GraphViz model is written.

        :seealso: :func:`showgraph`
        """

        if filename is None:
            f = sys.stdout
        elif isinstance(filename, str):
            f = open(filename, "w")
        else:
            f = filename

        if isinstance(self, DirectedGraph):
            print("digraph {", file=f)
        else:
            print("graph {", file=f)

        if direction is not None:
            print(f"rankdir = {direction}", file=f)

        # add the vertices including name and position
        for vertex in self:
            if vertex.coord is None:
                print('  "{:s}"'.format(vertex.name), file=f)
            else:
                print(
                    '  "{:s}" [pos="{:.5g},{:.5g}"]'.format(
                        vertex.name, vertex.coord[0], vertex.coord[1]),
                    file=f,
                )
        print(file=f)
        # add the edges
        for e in self.edges():
            if isinstance(self, DirectedGraph):
                print('  "{:s}" -> "{:s}"'.format(e.v1.name, e.v2.name),
                      file=f)
            else:
                print('  "{:s}" -- "{:s}"'.format(e.v1.name, e.v2.name),
                      file=f)

        print("}", file=f)

        if filename is None or isinstance(filename, str):
            f.close()  # noqa

    def showgraph(self, **kwargs):
        """
        Display graph in a browser tab

        :param kwargs: arguments passed to :meth:`dotfile`

        ``g.showgraph()`` renders and displays the graph in a browser tab.  The
        graph is exported in `GraphViz <https://graphviz.org>`_ format, rendered to
        PDF using ``dot`` and then displayed in a browser tab.

        :seealso: :func:`dotfile`
        """
        # create the temporary dotfile
        dotfile = tempfile.TemporaryFile(mode="w")
        self.dotfile(dotfile, **kwargs)

        # rewind the dot file, create PDF file in the filesystem, run dot
        dotfile.seek(0)
        pdffile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        result = subprocess.run("dot -Tpdf",
                                shell=True,
                                stdin=dotfile,
                                stdout=pdffile)

        if result.returncode == 0:
            # dot ran happily
            # open the PDF file in browser (hopefully portable), then cleanup
            webbrowser.open(f"file://{pdffile.name}")
            # time.sleep(1)
            # os.remove(pdffile.name)

    def iscyclic(self):
        pass

    def average_degree(self):
        r"""
        Average degree of the graph

        :return: average degree
        :rtype: float

        Average degree is :math:`2 E / N` for an undirected graph and
        :math:`E / N` for a directed graph where :math:`E` is the total number of
        edges and :math:`N` is the number of vertices.

        """
        if isinstance(self, DirectedGraph):
            return len(self.edges()) / self.n
        elif isinstance(self, UndirectedGraph):
            return 2 * len(self.edges()) / self.n

    # --------------------------------------------------------------------------- #

    # MATRIX REPRESENTATIONS

    def Laplacian(self):
        """
        Laplacian matrix for the graph

        :return: Laplacian matrix
        :rtype: NumPy ndarray

        ``g.Laplacian()`` is the Laplacian matrix (NxN) of the graph where N
        is the number of vertices.

        .. note::

            - Laplacian is always positive-semidefinite.
            - Laplacian has at least one zero eigenvalue.
            - The number of zero-valued eigenvalues is the number of connected
                components in the graph.

        :seealso: :meth:`adjacency` :meth:`incidence` :meth:`degree`
        """
        return self.degree() - (self.adjacency() > 0)

    def connectivity(self, vertices=None):
        """
        Graph connectivity

        :return: a list with the number of edges per vertex
        :rtype: list

        The average vertex connectivity is::

            mean(g.connectivity())

        and the minimum vertex connectivity is::

            min(g.connectivity())
        """

        c = []
        if vertices is None:
            vertices = self
        for n in vertices:
            c.append(len(n._edgelist))
        return c

    def degree(self):
        """
        Degree matrix of graph

        :return: degree matrix
        :rtype: ndarray(N,N)

        This is a diagonal matrix  where element ``[i,i]`` is the number
        of edges connected to vertex id ``i``.

        :seealso: :meth:`adjacency` :meth:`incidence` :meth:`laplacian`
        """

        return np.diag(self.connectivity())

    def adjacency(self):
        """
        Adjacency matrix of graph

        :returns: adjacency matrix
        :rtype: ndarray(N,N)

        The elements of the adjacency matrix ``[i,j]`` are 1 if vertex ``i`` is
        connected to vertex ``j``, else 0.

        .. note::

            - vertices are numbered in their order of creation. A vertex index
              can be resolved to a vertex reference by ``graph[i]``.
            - for an undirected graph the matrix is symmetric
            - Eigenvalues of ``A`` are real and are known as the spectrum of the graph.
            - The element ``A[i,j]`` can be considered the number of walks of length one
              edge from vertex ``i`` to vertex ``j`` (either zero or one).
            - If ``Ak = A ** k`` the element ``Ak[i,j]`` is the number of
              walks of length ``k`` from vertex ``i`` to vertex ``j``.

        :seealso: :meth:`Laplacian` :meth:`incidence` :meth:`degree`
        """
        # create a dict mapping vertex to an id
        vdict = {}
        for i, vert in enumerate(self):
            vdict[vert] = i

        A = np.zeros((self.number_of_vertices, self.number_of_vertices))
        for vertex in self:
            for n in vertex.neighbours():
                A[vdict[vertex], vdict[n]] = 1
        return A

    def incidence(self):
        """
        Incidence matrix of graph

        :returns: incidence matrix
        :rtype: ndarray(n,ne)

        The elements of the incidence matrix ``I[i,j]`` are 1 if vertex ``i`` is
        connected to edge ``j``, else 0.

        .. note::

            - vertices are numbered in their order of creation. A vertex index
              can be resolved to a vertex reference by ``graph[i]``.
            - edges are numbered in the order they appear in ``graph.edges()``.

        :seealso: :meth:`Laplacian` :meth:`adjacency` :meth:`degree`
        """
        edges = self.edges()
        I = np.zeros((self.number_of_vertices, len(edges)))

        # create a dict mapping edge to an id
        edict = {}
        for i, edge in enumerate(edges):
            edict[edge] = i

        for i, vertex in enumerate(self):
            for i, e in enumerate(vertex.edges()):
                I[i, edict[e]] = 1

        return I

    def distance(self):
        """
        Distance matrix of graph

        :return: distance matrix
        :rtype: ndarray(n,n)

        The elements of the distance matrix ``D[i,j]`` is the edge cost of moving
        from vertex ``i`` to vertex ``j``. It is zero if the vertices are not
        connected.
        """
        # create a dict mapping vertex to an id
        vdict = {}
        for i, vert in enumerate(self):
            vdict[vert] = i

        A = np.zeros((self.number_of_vertices, self.number_of_vertices))
        for v1 in self:
            for v2, edge in v1.incidences():
                A[vdict[v1], vdict[v2]] = edge.cost
        return A

    # GRAPH COMPONENTS

    def component(self, c):
        """
        All vertices in specified graph component

        ``graph.component(c)`` is a list of all vertices in graph component ``c``.
        """
        self._graphcolor()  # ensure labels are uptodate
        return [v for v in self if v.label == c]

    def samecomponent(self, v1, v2):
        """
        Test if vertices belong to same graph component

        :param v1: vertex
        :type v1: Vertex subclass
        :param v2: vertex
        :type v2: Vertex subclass
        :return: true if vertices belong to same graph component
        :rtype: bool

        Test whether vertices belong to the same component.  For a:

        - directed graph this implies a path between them
        - undirected graph there is not necessarily a path between them
        """
        self._graphcolor()  # ensure labels are uptodate

        return v1.label == v2.label

    # def remove(self, v):
    #     # remove edges from neighbour's edge list
    #     for e in v.edges():
    #         next = e.next(v)
    #         next._edgelist.remove(e)
    #         next._connectivitychange = True

    #     # remove references from the graph
    #     self._vertexlist.remove(v)
    #     for key, value in self._vertexdict.items():
    #         if value is v:
    #             del self._vertexdict[key]
    #             break

    #     v._edgelist = []  # remove all references to edges
    # --------------------------------------------------------------------------- #

    def path_BFS(self, S, G, verbose=False, summary=False):
        """
        Breadth-first search for path

        :param S: start vertex
        :type S: Vertex subclass
        :param G: goal vertex
        :type G: Vertex subclass
        :return: list of vertices from S to G inclusive, path length
        :rtype: list of Vertex subclass, float

        Returns a list of vertices that form a path from vertex ``S`` to
        vertex ``G`` if possible, otherwise return None.

        """
        if isinstance(S, str):
            S = self[S]
        elif not isinstance(S, Vertex):
            raise TypeError("start must be Vertex subclass or string name")
        if isinstance(G, str):
            G = self[G]
        elif not isinstance(S, Vertex):
            raise TypeError("goal must be Vertex subclass or string name")

        # we use lists not sets since the order is instructive in verbose
        # mode, really need ordered sets...
        frontier = [S]
        explored = []
        parent = {}
        done = False

        while frontier:
            if verbose:
                print()
                print("FRONTIER:", ", ".join([v.name for v in frontier]))
                print("EXPLORED:", ", ".join([v.name for v in explored]))

            x = frontier.pop(0)
            if verbose:
                print("   expand", x.name)

            # expand the vertex
            for n in x.neighbours():
                if n is G:
                    if verbose:
                        print("     goal", n.name, "reached")
                    parent[n] = x
                    done = True
                    break
                if n not in frontier and n not in explored:
                    # add it to the frontier
                    frontier.append(n)
                    if verbose:
                        print("      add", n.name, "to the frontier")
                    parent[n] = x
            if done:
                break
            explored.append(x)
            if verbose:
                print("     move", x.name, "to the explored list")
        else:
            # no path
            return None

        # reconstruct the path from start to goal
        x = G
        path = [x]
        length = 0

        while x is not S:
            p = parent[x]
            length += x.edgeto(p).cost
            path.insert(0, p)
            x = p

        if summary or verbose:
            print(
                f"{len(explored)} vertices explored, {len(frontier)} remaining on the frontier"
            )

        return path, length

    def path_UCS(self, S, G, verbose=False, summary=False):
        """
        Uniform cost search for path

        :param S: start vertex
        :type S: Vertex subclass
        :param G: goal vertex
        :type G: Vertex subclass
        :return: list of vertices from S to G inclusive, path length, tree
        :rtype: list of Vertex subclass, float, dict

        Returns a list of vertices that form a path from vertex ``S`` to
        vertex ``G`` if possible, otherwise return None.

        The search tree is returned as dict that maps a vertex to its parent.

        The heuristic is the distance metric of the graph, which defaults to
        Euclidean distance.
        """
        if isinstance(S, str):
            S = self[S]
        elif not isinstance(S, Vertex):
            raise TypeError("start must be Vertex subclass or string name")
        if isinstance(G, str):
            G = self[G]
        elif not isinstance(S, Vertex):
            raise TypeError("goal must be Vertex subclass or string name")

        frontier = [S]
        explored = []
        parent = {}
        f = {S: 0}  # evaluation function

        while frontier:
            if verbose:
                print()
                print("FRONTIER:",
                      ", ".join([f"{v.name}({f[v]:.0f})" for v in frontier]))
                print("EXPLORED:", ", ".join([v.name for v in explored]))

            i = np.argmin([f[n] for n in frontier])  # minimum f in frontier
            x = frontier.pop(i)
            if verbose:
                print("   expand", x.name)
            if x is G:
                break
            # expand the vertex
            for n, e in x.incidences():
                fnew = f[x] + e.cost
                if n not in frontier and n not in explored:
                    # add it to the frontier
                    parent[n] = x
                    f[n] = fnew
                    frontier.append(n)
                    if verbose:
                        print("      add", n.name, "to the frontier")

                elif n in frontier:
                    # neighbour is already in the frontier
                    # cost of path via x is lower that previous, reparent it
                    if fnew < f[n]:
                        if verbose:
                            print(
                                f" reparent {n.name}: cost {fnew} via {x.name} is less than cost {f[n]} via {parent[n].name}, change parent from {parent[n].name} to {x.name} "
                            )
                        f[n] = fnew
                        parent[n] = x

            explored.append(x)
            if verbose:
                print("     move", x.name, "to the explored list")
        else:
            # no path
            return None

        # reconstruct the path from start to goal
        x = G
        path = [x]
        length = 0

        while x is not S:
            p = parent[x]
            length += p.edgeto(x).cost
            path.insert(0, p)
            x = p

        parent_names = {}
        for v, p in parent.items():
            parent_names[v.name] = p.name

        if summary or verbose:
            print(
                f"{len(explored)} vertices explored, {len(frontier)} remaining on the frontier"
            )

        return path, length, parent_names

    def path_Astar(self, S, G, verbose=False, summary=False):
        """
        A* search for path

        :param S: start vertex
        :type S: Vertex subclass
        :param G: goal vertex
        :type G: Vertex subclass
        :return: list of vertices from S to G inclusive, path length, tree
        :rtype: list of Vertex subclass, float, dict

        Returns a list of vertices that form a path from vertex ``S`` to
        vertex ``G`` if possible, otherwise return None.

        The search tree is returned as dict that maps a vertex to its parent.

        The heuristic is the distance metric of the graph, which defaults to
        Euclidean distance.

        :seealso: :meth:`heuristic`
        """
        if isinstance(S, str):
            S = self[S]
        elif not isinstance(S, Vertex):
            raise TypeError("start must be Vertex subclass or string name")
        if isinstance(G, str):
            G = self[G]
        elif not isinstance(S, Vertex):
            raise TypeError("goal must be Vertex subclass or string name")

        frontier = [S]
        explored = []
        parent = {}
        g = {S: 0}  # cost to come
        f = {S: 0}  # evaluation function

        while frontier:
            if verbose:
                print()
                print("FRONTIER:",
                      ", ".join([f"{v.name}({f[v]:.0f})" for v in frontier]))
                print("EXPLORED:", ", ".join([v.name for v in explored]))

            i = np.argmin([f[n] for n in frontier])  # minimum f in frontier
            x = frontier.pop(i)
            if verbose:
                print("   expand", x.name)
            if x is G:
                break
            # expand the vertex
            for n, e in x.incidences():
                if n not in frontier and n not in explored:
                    # add it to the frontier
                    frontier.append(n)
                    parent[n] = x
                    g[n] = g[x] + e.cost  # update cost to come
                    f[n] = g[n] + n.heuristic_distance(G)  # heuristic
                    if verbose:
                        print("      add", n.name, "to the frontier")
                elif n in frontier:
                    # neighbour is already in the frontier
                    gnew = g[x] + e.cost
                    if gnew < g[n]:
                        # cost of path via x is lower that previous, reparent it
                        if verbose:
                            print(
                                f" reparent {n.name}: cost {gnew} via {x.name} is less than cost {g[n]} via {parent[n].name}, change parent from {parent[n].name} to {x.name} "
                            )
                        g[n] = gnew
                        f[n] = g[n] + n.heuristic_distance(G)  # heuristic

                        parent[n] = x  # reparent

            explored.append(x)
            if verbose:
                print("     move", x.name, "to the explored list")

        else:
            # no path
            return None

        # reconstruct the path from start to goal
        x = G
        path = [x]
        length = 0

        while x is not S:
            p = parent[x]
            length += p.edgeto(x).cost
            path.insert(0, p)
            x = p

        parent_names = {}
        for v, p in parent.items():
            parent_names[v.name] = p.name

        if summary or verbose:
            print(
                f"{len(explored)} vertices explored, {len(frontier)} remaining on the frontier"
            )

        return path, length, parent_names
