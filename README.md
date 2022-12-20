# graph searcher
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

A graph search algorithms visualization tool.

## Install

  The package is available on [pypi](https://pypi.org/project/graph-searcher/):

  ```bash
pip install graph_searcher
  ```

## Usage

```
usage: graph_searcher [-h] [--verbose] [--version] (--file FILE | --random) --path START END [--algorithm {bfs,sma}] [--bound BOUND]
                      [--interval INTERVAL] [--repeat] [--output OUTPUT]

Search a graph for a path between two nodes

options:
  -h, --help            show this help message and exit
  --verbose, -v         increase output verbosity
  --version             show program's version number and exit
  --file FILE           JSON File to read graph from
  --random              A random generated graph
  --path START END      Starting and ending nodes
  --algorithm {bfs,sma}, -a {bfs,sma}
                        Which algorithm to use for searching the graph
  --bound BOUND, -b BOUND
                        Bound for SMA algorithm
  --interval INTERVAL, -i INTERVAL
                        Animation Interval
  --repeat, -r          Repeat the animation
  --output OUTPUT, -o OUTPUT
                        Output file
```

## Run

The `assets` folder contains some graphs for testing:

- **SMA \*(boundary=5) algorithm on Paraná Graph**:

```bash
graph_searcher --file ./assets/parana.json --path Cascavel Londrina -a sma -b 5
```

https://user-images.githubusercontent.com/44649669/208787339-f90d841c-91df-4011-975d-b0f8760ae27e.mp4


- **BFS algorithm on Paraná Graph**:

```bash
graph_searcher --file ./assets/parana.json --path Cascavel Londrina -a bfs
```

https://user-images.githubusercontent.com/44649669/208787516-8edfaeeb-8f4a-40d9-9828-808c6543caf2.mp4

- **SMA\* (boundary=4) algorithm on example Graph**:

```bash
graph_searcher --file ./assets/example.json --path n m -a sma -b 4
```

https://user-images.githubusercontent.com/44649669/208787598-bd7578c8-1cdf-4dfe-96c2-17c778845ee4.mp4


- **BFS algorithm on example Graph**:

```bash
graph_searcher --file ./assets/example.json --path n m -a bfs
```

https://user-images.githubusercontent.com/44649669/208787387-2f3a82cb-ea0f-4a67-bf66-7e64a367c38c.mp4



## Colaborators

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/Tomcat-42"><img src="https://avatars.githubusercontent.com/u/44649669?v=4?s=100" width="100px;" alt="Pablo Alessandro Santos Hugen"/><br /><sub><b>Pablo Alessandro Santos Hugen</b></sub></a><br /><a href="https://github.com/Tomcat-42/graph_searcher/commits?author=Tomcat-42" title="Code">💻</a> <a href="https://github.com/Tomcat-42/graph_searcher/commits?author=Tomcat-42" title="Documentation">📖</a> <a href="#ideas-Tomcat-42" title="Ideas, Planning, & Feedback">🤔</a> <a href="#research-Tomcat-42" title="Research">🔬</a></td>
      <td align="center"><a href="https://github.com/matheusnunesismael"><img src="https://avatars.githubusercontent.com/u/32654785?v=4?s=100" width="100px;" alt="Matheus Nunes Ismael"/><br /><sub><b>Matheus Nunes Ismael</b></sub></a><br /><a href="https://github.com/Tomcat-42/graph_searcher/commits?author=matheusnunesismael" title="Code">💻</a> <a href="https://github.com/Tomcat-42/graph_searcher/commits?author=matheusnunesismael" title="Documentation">📖</a> <a href="#ideas-matheusnunesismael" title="Ideas, Planning, & Feedback">🤔</a> <a href="#research-matheusnunesismael" title="Research">🔬</a></td>
      <td align="center"><a href="https://github.com/AlessandraDosSantos"><img src="https://avatars.githubusercontent.com/u/66135957?v=4?s=100" width="100px;" alt="AlessandraDosSantos"/><br /><sub><b>AlessandraDosSantos</b></sub></a><br /><a href="https://github.com/Tomcat-42/graph_searcher/commits?author=AlessandraDosSantos" title="Code">💻</a> <a href="https://github.com/Tomcat-42/graph_searcher/commits?author=AlessandraDosSantos" title="Documentation">📖</a> <a href="#ideas-AlessandraDosSantos" title="Ideas, Planning, & Feedback">🤔</a> <a href="#research-AlessandraDosSantos" title="Research">🔬</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!