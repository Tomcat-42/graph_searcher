import copy
from abc import ABC
from collections.abc import Iterable
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from spatialmath.base.graphics import axes_logic

from ..edge import Edge
from ..vertex import Vertex


class Graph(ABC):

    def __init__(self, nodes: Dict | None = None, edges: Dict | None = None):
        self._vertexlist = []
        self._vertexdict = {}
        self._edgelist = set()

        # Add vertices and nodes
        if nodes:
            for name, coord_info in nodes.items():
                self.add_vertex(name=name, coord=coord_info["utm"])

        if edges:
            for edge in edges:
                self.add_edge(edge["start"],
                              edge["end"],
                              cost=edge["distance"])

    def __str__(self):
        return f"{self.__class__.__name__}: {self.number_of_vertices} {'vertex' if self.number_of_vertices==1 else 'vertices'}, {self.number_of_edges} edge{'s'[:self.number_of_edges^1]}, {self.number_of_components} component{'s'[:self.number_of_components^1]}"

    def __getitem__(self, i):
        if isinstance(i, int):
            return self._vertexlist[i]
        elif isinstance(i, str):
            return self._vertexdict[i]
        elif isinstance(i, Vertex):
            return i

    def add_vertex(self, coord=None, name=None):
        vertex = Vertex(coord)

        name = name if name else f"#{len(self._vertexlist)}"
        vertex.name = name
        self._vertexlist.append(vertex)
        self._vertexdict[vertex.name] = vertex
        vertex._graph = self
        self._connectivitychange = True
        return vertex

    def add_edge(self, v1, v2, **kwargs):
        if isinstance(v1, str):
            v1 = self[v1]
        elif not isinstance(v1, Vertex):
            raise TypeError("v1 must be Vertex subclass or string name")
        if isinstance(v2, str):
            v2 = self[v2]
        elif not isinstance(v2, Vertex):
            raise TypeError("v2 must be Vertex subclass or string name")

        return v1.connect(v2, **kwargs)

    def remove(self, x):
        if isinstance(x, Edge):
            x.v1._edgelist.remove(x)
            x.v2._edgelist.remove(x)
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

    @property
    def number_of_vertices(self):
        return len(self._vertexdict)

    @property
    def number_of_edges(self):
        return len(self._edgelist)

    @property
    def number_of_components(self):
        self._graphcolor()
        return self._ncomponents

    def closest(self, coord):
        min_dist = np.Inf
        min_which = None

        for vertex in self:
            d = self.metric(vertex.coord - coord)
            if d < min_dist:
                min_dist = d
                min_which = vertex

        return min_which, min_dist

    def edges(self):
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
        ax.grid(grid)
        plt.show(block=block)

    def highlight_path(self, path, block=False, **kwargs):
        for i in range(len(path)):
            if i < len(path) - 1:
                e = path[i].edgeto(path[i + 1])
                self.highlight_edge(e, **kwargs)
            self.highlight_vertex(path[i], **kwargs)
        plt.show(block=block)

    def highlight_edge(self, edge, scale=2, color="r", alpha=0.5):
        p1 = edge.v1
        p2 = edge.v2
        plt.plot([p1.x, p2.x], [p1.y, p2.y],
                 color=color,
                 linewidth=3 * scale,
                 alpha=alpha)

    def highlight_vertex(self, vertex, scale=2, color="r", alpha=0.5):
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

    def component(self, c):
        self._graphcolor()  # ensure labels are uptodate
        return [v for v in self if v.label == c]

    def samecomponent(self, v1, v2):
        self._graphcolor()

        return v1.label == v2.label

    def path_bfs(self, S, G):
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
        done = False

        while frontier:
            x = frontier.pop(0)

            # expand the vertex
            for n in x.neighbours():
                if n is G:
                    parent[n] = x
                    done = True
                    break
                if n not in frontier and n not in explored:
                    # add it to the frontier
                    frontier.append(n)
                    parent[n] = x
            if done:
                break
            explored.append(x)
        else:
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

        return path, length

    def path_sma(self, S, G):
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
            i = np.argmin([f[n] for n in frontier])  # minimum f in frontier
            x = frontier.pop(i)
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
                elif n in frontier:
                    # neighbour is already in the frontier
                    gnew = g[x] + e.cost
                    if gnew < g[n]:
                        # cost of path via x is lower that previous, reparent it
                        g[n] = gnew
                        f[n] = g[n] + n.heuristic_distance(G)  # heuristic

                        parent[n] = x  # reparent

            explored.append(x)

        else:
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

        return path, length, parent_names
