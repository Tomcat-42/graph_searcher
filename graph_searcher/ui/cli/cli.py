import argparse

from graph_searcher.data_structures.graph import Graph

from .json_file_action import JsonFileAction


class Cli:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="graph_searcher",
            description="Search a graph for a path between two nodes",
            epilog="This is the end of the help message",
        )

        self.parser.add_argument(
            "--verbose",
            "-v",
            help="increase output verbosity",
            action="count",
            default=0,
        )
        self.parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s 0.1",
        )
        # a Graph Should be random or a file
        self.parser_input = self.parser.add_mutually_exclusive_group(
            required=True, )
        self.parser_input.add_argument(
            "--file",
            # type=argparse.FileType("r"),
            action=JsonFileAction,
            help="JSON File to read graph from",
        )
        self.parser_input.add_argument(
            "--random",
            action="store_true",
            help="A random generated graph",
        )

        # which path to look fo
        self.parser.add_argument(
            "--path",
            nargs=2,
            required=True,
            help="Starting and ending nodes",
            metavar=("START", "END"),
        )

        # which algorithm to use
        self.parser.add_argument(
            "--algorithm",
            choices=["bfs", "dfs"],
            default="bfs",
            help="Which algorithm to use for searching the graph",
        )

        self.args = vars(self.parser.parse_args())

    def run(self):
        data = self.args["file"]
        # pp(data
        nodes, edges = data["nodes"], data["edges"]

        graph = Graph(nodes, edges)

        # for name, geo in nodes.items():
        #     graph.add_vertex(name=name, coord=geo["utm"])
        #
        # for edge in edges:
        #     graph.add_edge(edge["start"], edge["end"], cost=edge["distance"])

        [start, end] = self.args["path"]

        path, length = graph.path_bfs(start, end)

        graph.plot(block=False)
        graph.highlight_path(path, block=True, alpha=0.5, scale=2)


def main():
    cli = Cli()
    cli.run()


if __name__ == "__main__":
    main()
