import argparse
from pprint import pprint as pp

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
            "-a",
            choices=["bfs", "sma"],
            default="bfs",
            help="Which algorithm to use for searching the graph",
        )

        # SMA bound
        self.parser.add_argument(
            "--bound",
            "-b",
            type=int,
            default=0,
            help="Bound for SMA algorithm",
        )

        self.args = vars(self.parser.parse_args())

    def run(self):
        data = self.args["file"]
        nodes, edges = data["nodes"], data["edges"]
        algorithm = self.args["algorithm"]
        bound = self.args["bound"]

        graph = Graph(nodes, edges)

        [start, end] = self.args["path"]

        if algorithm == "bfs":
            explored, parents, path, length = graph.path_bfs(start, end)
        else:
            explored, parents, path, length = graph.path_sma(start, end, bound)

        pp("explored")
        pp(explored)
        pp("parents")
        pp(parents)
        pp("path")
        pp(path)
        pp("length")
        pp(length)

        graph.highlight_path(
            path,
            explored,
            parents,
            length,
            block=True,
            alpha=1,
            scale=2,
            title="Searching path from " + r"$\bf{" + start + r"}$" + " to " +
            r"$\bf{" + end + r"}$" + " with " + r"$\bf{" + algorithm + r"}$",
        )


def main():
    cli = Cli()
    cli.run()


if __name__ == "__main__":
    main()
