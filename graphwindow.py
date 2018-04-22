from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtSvg import QSvgWidget


class GraphWindow(QMainWindow):
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
