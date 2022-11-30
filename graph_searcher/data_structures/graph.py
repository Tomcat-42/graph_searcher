from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class GraphType(Enum):
    DIRECTED = 0
    UNDIRECTED = 1


# A Graph class that can hold a graph with any number of nodes and edges, with any data type


class Graph:

    def __init__(
        self,
        vertices: int = 100,
        graph_type: GraphType = GraphType.UNDIRECTED,
        weighted: bool = False,
    ):
        self.__vertices = vertices
        self.__graph_type = graph_type
        self.__weighted = weighted

        self.__adjacency_matrix = np.zeros((self.__vertices, self.__vertices),
                                           dtype=np.int32)
        self.__visited = np.zeros(self.__vertices, dtype=bool)

        self.__nodes: Dict[int, Any] = {}
        self.__edges: Dict[int, List[Tuple[int, Any]]] = defaultdict(list)

    def add_edge(self, vertex1, vertex2, weight=1):

        self.__adjacency_matrix[vertex1][vertex2] = weight

        if self.__graph_type == GraphType.UNDIRECTED:
            self.__adjacency_matrix[vertex2][vertex1] = weight

    def del_edge(self, vertex1, vertex2):

        self.__adjacency_matrix[vertex1][vertex2] = 0

        if self.__graph_type == GraphType.UNDIRECTED:
            self.__adjacency_matrix[vertex2][vertex1] = 0

    def exists_edge(self, vertex1, vertex2):
        return self.__adjacency_matrix[vertex1][vertex2] != 0

    def num_vertices(self):
        return len(self.__adjacency_matrix.nonzero()[0])

    def num_edges(self):
        return len(self.__adjacency_matrix.nonzero()[0]) // 2

    def __str__(self):
        return f"""Graph(

graph_type={self.__graph_type},
weighted={self.__weighted},
visited={self.__visited},
vertices={self.__vertices},
adjacency_matrix={self.__adjacency_matrix},

        )"""

    def __repr__(self):
        return f"""Graph(

graph_type={self.__graph_type},
weighted={self.__weighted},
visited={self.__visited},
vertices={self.__vertices},
adjacency_matrix={self.__adjacency_matrix},

        )"""
