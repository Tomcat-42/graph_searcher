import copy
from abc import ABC
from collections.abc import Iterable
from typing import Dict

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from celluloid import Camera

from ..edge import Edge
from ..vertex import Vertex

mpl.rcParams["toolbar"] = "None"
mpl.rc("lines", linewidth=0.1)
plt.rcParams["figure.autolayout"] = True
# change resolution for saved figure

plt.style.use(["dark_background"])
plt.rcParams.update({
    "lines.color": "white",
    "patch.edgecolor": "white",
    "text.color": "#ffffff",
    "axes.facecolor": "white",
    "axes.edgecolor": "lightgray",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "grid.color": "lightgray",
    "figure.facecolor": "black",
    "figure.edgecolor": "black",
    "savefig.facecolor": "black",
    "savefig.edgecolor": "black",
})

fig, ax = plt.subplots()
fig.tight_layout()
plt.margins(0.01)


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

            x.v1 = None
            x.v2 = None

            self._edgelist.remove(x)

        elif isinstance(x, Vertex):
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
        self.label_components()
        return self._ncomponents

    def closest(self, coord):
        min_dist = np.Inf
        min_which = None

        for vertex in self:
            d = vertex.coord - coord
            if d < min_dist:
                min_dist = d
                min_which = vertex

        return min_which, min_dist

    def edges(self):
        return self._edgelist

    def plot(
        self,
        colorcomponents=True,
        vopt={},
        eopt={},
        text={},
    ):
        vopt = {**dict(marker="o", markersize=6), **vopt}
        eopt = {**dict(linewidth=0.5), **eopt}

        # 2D plotting
        for c in range(self.number_of_components):
            # for each component
            for vertex in self.component(c):
                if text is not False:
                    plt.text(
                        vertex.x,
                        vertex.y,
                        "   " + r"$\bf{" + vertex.name + r"}$",
                        **text,
                    )
                if colorcomponents:
                    plt.plot(vertex.x, vertex.y, **vopt)
                    for v in vertex.neighbours():
                        plt.plot(
                            [vertex.x, v.x],
                            [vertex.y, v.y],
                            **eopt,
                        )
                        e = vertex.edgeto(v)
                        plt.text(
                            (vertex.x + v.x) / 2,
                            (vertex.y + v.y) / 2,
                            r"$\it{" + f"{e.cost:.1f}" + r"}$",
                            **text,
                        )
                else:
                    # plot all edges, with the cost as text between them
                    plt.plot(vertex.x, vertex.y, **vopt)
                    for v in vertex.neighbours():
                        plt.plot([vertex.x, v.x], [vertex.y, v.y], **eopt)
        plt.axis("off")

    def highlight_path(
        self,
        path,
        explored,
        parents,
        interval=1000,
        title="Searching",
        repeat=False,
        output="",
        **kwargs,
    ):
        camera = Camera(fig)

        plt.suptitle(title)

        for i in range(len(explored)):
            self.plot(vopt={"color": "red"}, eopt={"color": "red"})

            for j in range(i + 1):
                try:
                    e = explored[j].edgeto(parents[explored[j]])
                    self.highlight_edge(e, color="yellow", **kwargs)
                except KeyError:
                    pass
                self.highlight_vertex(explored[j], color="yellow", **kwargs)

            try:
                e = explored[i].edgeto(parents[explored[i]])
                ax.text(
                    0,
                    0,
                    "Total explored = " + r"$\bf{" + str(i) + r"}$" +
                    "\nGoing from " + r"$\bf{" + parents[explored[i]].name +
                    r"}$" + " to " + r"$\bf{" + explored[i].name + r"}$" +
                    " with cost " + r"$\bf{" + str(e.cost) + r"}$",
                    transform=ax.transAxes,
                )
                self.highlight_edge(e, color="yellow", **kwargs)
            except KeyError:
                pass
            camera.snap()

        cost = 0
        for i in range(len(path)):
            self.plot(vopt={"color": "red"}, eopt={"color": "red"})
            for j in range(i + 1):
                try:
                    e = path[j].edgeto(parents[path[j]])
                    self.highlight_edge(e, **kwargs, color="green")
                except KeyError:
                    pass
                self.highlight_vertex(path[j], **kwargs, color="green")

            try:
                e = path[i].edgeto(parents[path[i]])
                cost += e.cost
                ax.text(
                    0,
                    0,
                    f"Total cost = " + r"$\bf{" + str(cost) + r"}$" +
                    f"\nPath = " + r"$\bf{" +
                    f"{', '.join([v.name for v in path[:i+1]])}" + r"}$",
                    transform=ax.transAxes,
                )
            except KeyError:
                pass
            camera.snap()

        animation = camera.animate(interval=interval,
                                   repeat=repeat,
                                   blit=True,
                                   repeat_delay=interval)

        # if output is not empty string, save animation
        if output != "":
            fig.set_size_inches(19.2, 10.8)
            plt.rcParams["figure.dpi"] = 480
            animation.save(output)
        else:
            fig.tight_layout()
            plt.show()

    def highlight_edge(self, edge, scale=1, color="r", alpha=0.5):
        p1 = edge.v1
        p2 = edge.v2
        plt.plot([p1.x, p2.x], [p1.y, p2.y],
                 color=color,
                 linewidth=0.5 * scale,
                 alpha=alpha)

    def highlight_vertex(self, vertex, scale=1, color="r", alpha=0.5):
        if isinstance(vertex, Iterable):
            for n in vertex:
                if isinstance(n, str):
                    n = self[n]
                plt.plot(n.x,
                         n.y,
                         "o",
                         color=color,
                         markersize=6 * scale,
                         alpha=alpha)
        else:
            plt.plot(vertex.x,
                     vertex.y,
                     "o",
                     color=color,
                     markersize=6 * scale,
                     alpha=alpha)

    def label_components(self):
        if self._connectivitychange or any(
            [n._connectivitychange for n in self]):

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
        self.label_components()  # ensure labels are uptodate
        return [v for v in self if v.label == c]

    def samecomponent(self, v1, v2):
        self.label_components()

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
        parents = {}
        done = False

        while frontier:
            x = frontier.pop(0)
            explored.append(x)
            # expand the vertex
            for n in x.neighbours():
                if n is G:
                    parents[n] = x
                    explored.append(n)
                    done = True
                    break
                if n not in frontier and n not in explored:
                    # add it to the frontier
                    frontier.append(n)
                    parents[n] = x
            if done:
                break
        else:
            return None

        # reconstruct the path from start to goal
        x = G
        path = [x]
        length = 0

        while x is not S:
            p = parents[x]
            length += x.edgeto(p).cost
            path.insert(0, p)
            x = p

        return explored, parents, path, length

    def path_sma(self, S, G, B=0):
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
        parents = {}
        g = {S: 0}  # cost to come
        f = {S: 0}  # evaluation function

        while frontier:
            i = np.argmin([f[n] for n in frontier])  # minimum f in frontier
            x = frontier.pop(i)
            explored.append(x)

            if x is G:
                break

            if B > 0 and len(frontier) > B:
                return explored, parents, [], 0

            # expand the vertex
            for n, e in x.incidences():
                if n not in frontier and n not in explored:
                    # add it to the frontier
                    frontier.append(n)
                    parents[n] = x
                    g[n] = g[x] + e.cost  # update cost to come
                    f[n] = g[n] + n.heuristic_distance(G)  # heuristic
                elif n in frontier:
                    # neighbour is already in the frontier
                    gnew = g[x] + e.cost
                    if gnew < g[n]:
                        # cost of path via x is lower that previous, reparent it
                        g[n] = gnew
                        f[n] = g[n] + n.heuristic_distance(G)  # heuristic

                        parents[n] = x  # reparent

            # explored.append(x)

        else:
            return None

        # reconstruct the path from start to goal
        x = G
        path = [x]
        length = 0

        while x is not S:
            p = parents[x]
            length += p.edgeto(x).cost
            path.insert(0, p)
            x = p

        return explored, parents, path, length
