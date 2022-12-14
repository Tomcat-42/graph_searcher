from graph_searcher import DirectedGraph, Graph, UndirectedGraph


def main():
    g = UndirectedGraph.from_dict({
        "a": "b",
        "b": "c",
        "c": "d",
        "d": "e",
        "e": "f"
    })
    print(g)
