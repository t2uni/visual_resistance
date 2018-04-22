"""Visualise the resistances between contacts on a substrate."""

from asyncio import SelectorEventLoop
from graphviz import Graph
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtSvg import QSvgWidget
import random
import sys
from threading import Thread
import time
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

    @pyqtSlot(bytes)
    def set_graph(self, graph_svg: bytes) -> None:
        """Renders SVG bytes in the graph display."""
        self._graph_display.load(graph_svg)


class DataProvider(QObject):
    """ Emits a Qt signal whenever a connection has been detected. 

    Call start() to begin listening for connection detection,
    stop() to terminate thread.

    Attributes:
        _listen_loop  Event loop to receive detection data
        _should_run  Control loop run time
    """

    def __init__(self):
        super().__init__()
        
        self._listen_thread = Thread(target=self._listen)
        self._should_run = False  # type: bool

    def start(self):
        self._should_run = True
        self._listen_thread.start()

    def stop(self):
        self._should_run = False
        self._listen_thread.join()
        
    def _listen(self):
        while self._should_run:
            # TODO: listen for signals from easy2point process, remove following dummy code
            time.sleep(2)
            
            first_connection = random.randint(1, 24)
            second_connection = first_connection
            while second_connection == first_connection:
                second_connection = random.randint(1, 24)
            self.connection_detected.emit(
                "{:02d}".format(first_connection),
                "{:02d}".format(second_connection)
            )
    
    # Arguments: name of contact on which a connection was detected; resistance value measured
    connection_detected = pyqtSignal(str, str)  # TODO: pass resistance value
        
        
class Grid(QObject):
    """ graphviz representation of contact board grid.

    Attributes:
        _dot  graphviz Graph representing the board
        _contact_numbers
    """

    grid_aspect_ratio = 1.0  # type: float
    connection_color = "red"  # type: str
    connection_width = "5.0"  # type: str

    def __init__(self, grid_size: int, coord_size: int,
                 contact_numbers: Dict[str, Tuple[int, int]]) -> None:
        """
        :param contact_numbers: Contact points with their grid position
        """
        super().__init__()

        self._contact_numbers = contact_numbers
        
        self._dot = Graph(comment="ALD interface board", engine="neato")
        self._dot.attr("graph", ratio="{}".format(self.grid_aspect_ratio))
        self._dot.attr("graph", splines="spline")

        # Display contact points in a grid:
        for number in contact_numbers.keys():
            tile_x, tile_y = contact_numbers[number]  # type: Tuple[int, int]
            coord_x, coord_y = self.grid_to_coords(
                grid_size, coord_size, tile_x, tile_y
            )  # type: Tuple[float, float]

            self._dot.node(
                number, number,
                pos="{},{}!".format(coord_x, coord_y)
            )

    def get_svg(self) -> bytes:
        """ Return graph as SVG bytes. """
        return self._dot.pipe(format="svg")

    @pyqtSlot(str, str)
    def add_connection(self, first_contact: str, second_contact: str):
        """ Add an electrical connection between two contact points.

        :raises: RuntimeError if contacts are not on this grid
        """
        if (first_contact not in self._contact_numbers.keys()) or \
               (second_contact not in self._contact_numbers.keys()):
            raise RuntimeError(
                "Contacts " + first_contact + " and/or " + second_contact +
                " are not on this board."
            )

        self._dot.edge(first_contact, second_contact,
                       color=self.connection_color,
                       penwidth=self.connection_width)
        self.connection_added.emit(self.get_svg())

    # Arguments: new graph as SVG bytes
    connection_added = pyqtSignal(bytes)
    
    @staticmethod
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
    # Assign each contact number its grid coordinates:
    contact_numbers = {
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

    board = Grid(grid_size, coord_size, contact_numbers)
                     
    app = QApplication(sys.argv)
    window = MainWindow(board.get_svg(), board.grid_aspect_ratio)

    board.connection_added.connect(window.set_graph)
    provider = DataProvider()
    provider.connection_detected.connect(board.add_connection)
    provider.start()
    
    window.show()
    exit_code =  app.exec()  # type: int

    provider.stop()
    return exit_code


if __name__ == "__main__":
    exit(main())
