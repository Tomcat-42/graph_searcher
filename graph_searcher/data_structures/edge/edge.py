from __future__ import annotations


class Edge:

    def __init__(self, v1: "Vertex", v2: "Vertex", cost: float, data: dict):
        self.v1 = v1
        self.v2 = v2
        self.cost = cost
        self.data = data

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Edge{{{self.v1} -- {self.v2}, cost={self.cost:.4g}}}"

    def connect(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

        v1.connect(v2, edge=self)

    def get_next_vertex(self, vertex):
        return self.v2 if self.v1 is vertex else self.v1

    @property
    def get_vertexes(self):
        return (self.v1, self.v2)
