from copy import deepcopy
from PyQt5.QtCore import pyqtSlot, QPoint, Qt
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QAction, QFileDialog, QMainWindow, QMenu
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtPrintSupport import QPrinter


class GraphWindow(QMainWindow):
    """ Qt application window showing a single vector graph.
    
    Save graph using right click menu.

    Attributes:
        _graph_display  Widget that shows the graph image
        _svg_bytes  SVG bytes representing currently displayed image
    """
    window_width = 600  # type: float  # Height is computed from aspect ratio

    def __init__(self, graph_svg: bytes = None,
                 aspect_ratio: float = 1.0) -> None:
        super().__init__()

        self._svg_bytes = bytes()
        
        # Add image widget:
        self._graph_display = QSvgWidget()
        self.setCentralWidget(self._graph_display)
        if graph_svg is not None:
            self.set_graph(graph_svg)
        self._graph_display.setContextMenuPolicy(Qt.CustomContextMenu)
        self._graph_display.customContextMenuRequested.connect(
            self._show_context_menu
        )
        self._graph_display.setToolTip("Right-click to save image")
        self._graph_display.setToolTipDuration(2000)

        # Set correct aspect ratio:
        self.setFixedSize(self.window_width,
                          self.window_width * aspect_ratio)

    def _show_context_menu(self, point: QPoint) -> None:
        """ Show a context menu for the graph display. """
        menu = QMenu(self)
        save_action = QAction("Save current image...", menu)
        save_action.triggered.connect(
            lambda checked: self._save_current_image()
        )
        menu.addAction(save_action)
        menu.exec(self._graph_display.mapToGlobal(point))

    def _save_current_image(self):
        """ Copy current image and save it to a file. """
        current_svg = deepcopy(self._svg_bytes)  # type: bytes
        file_path = QFileDialog.getSaveFileUrl()[0].path()  # type: str
        
        with open(file_path, "w") as outfile:
            outfile.write(current_svg.decode())

    @pyqtSlot(bytes)
    def set_graph(self, graph_svg: bytes) -> None:
        """Renders SVG bytes in the graph display."""
        self._graph_display.load(graph_svg)
        self._svg_bytes = graph_svg
