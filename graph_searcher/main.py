from trabalho_1.data_structures import Graph, GraphType, Queue, Stack


def main():
    n =5

    graph = Graph(vertices=n, graph_type=GraphType.UNDIRECTED, weighted=False)

    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(2, 4)
    graph.add_edge(3, 4)
    graph.add_edge(4, 4)

    print(graph)
