"""Visualise the resistances between contacts on a substrate."""

from graphviz import Graph
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtSvg import QSvgWidget
import sys
from typing import Dict, Tuple, List


class MainWindow(QMainWindow):
    """ Qt application window showing a single vector graph.

    Attributes:
        _graph_display  Widget that shows the graph image
    """
    window_width = 600  # type: float  # Height is computed from aspect ratio

    def __init__(self, graph_svg: bytes = None,
                 aspect_ratio: float = 1.0) -> None:
        super().__init__()
        
        # Add image widget:
        self._graph_display = QSvgWidget()
        self.setCentralWidget(self._graph_display)
        if graph_svg is not None:
            self.set_graph(graph_svg)
#        self._graph_display.mousePressEvent.connect()

        # Set correct aspect ratio:
        self.setFixedSize(self.window_width,
                          self.window_width * aspect_ratio)

    def set_graph(self, graph_svg: bytes) -> None:
        """Renders the SVG image in the graph display."""
        self._graph_display.load(graph_svg)


def grid_to_coords(grid_size: int, coord_size: float,
                   tile_x: int, tile_y: int) -> Tuple[float, float]:
    """ Map a quadratic grid of tiles to coordinates in the x-y plane.

    Tile number are counted left to right (x), bottom to top (y).

    :param grid_size: Number of tiles along one side of quadratic grid
    :param height: Length in x-y coordinates of one grid side
    :param tile_x: x tile number to convert to coordinates
    :param tile_y: y tile number to convert to coordinates
    :returns: The converted coordinates (x, y)
    """

    coord_x = tile_x / grid_size * coord_size  # type: float
    coord_y = tile_y / grid_size * coord_size  # type: float

    return (coord_x, coord_y)


def main() -> int:
    graph_aspect_ratio = 1.0  # type: float

    dot = Graph(comment="Test Graph", engine="neato")

    # Assign each connection number its grid coordinates:
    connection_numbers = {
        "20": (0, 1), "24": (0, 2), "23": (0, 3),
        "05": (0, 4), "06": (0, 5), "02": (0, 6),
        "04": (1, 7), "03": (2, 7), "01": (3, 7),
        "07": (4, 7), "09": (5, 7), "10": (6, 7),
        "08": (7, 6), "12": (7, 5), "11": (7, 4),
        "17": (7, 3), "18": (7, 2), "14": (7, 1),
        "16": (6, 0), "15": (5, 0), "13": (4, 0),
        "19": (3, 0), "21": (2, 0), "22": (1, 0)
    }  # type: Dict[str, Tuple[int, int]]
    
    grid_size = 8  # type: int
    coord_size = 8.0  # type: float
    
    dot.attr("graph", ratio=str(graph_aspect_ratio))
    dot.attr("graph", splines="spline")

    # Display connection points in a grid:
    for number in connection_numbers.keys():
        tile_x, tile_y = connection_numbers[number]  # type: Tuple[int, int]
        coord_x, coord_y = grid_to_coords(
            grid_size, coord_size, tile_x, tile_y
        )  # type: Tuple[float, float]

        dot.node(
            number, number,
            pos="{},{}!".format(coord_x, coord_y)
        )

    # Make some connections:
    dot.edge("11", "17", color="red", label="300 Ohm")
    
    app = QApplication(sys.argv)
    window = MainWindow(dot.pipe(format="svg"), graph_aspect_ratio)

    window.show()

    return app.exec()


if __name__ == "__main__":
    exit(main())

