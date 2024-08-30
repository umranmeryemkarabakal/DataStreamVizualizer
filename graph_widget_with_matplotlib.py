from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class GraphWidget(QWidget):
    def __init__(self, fig):
        super().__init__()
        layout = QVBoxLayout()

        self.canvas = FigureCanvas(fig)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)

class LegendWidget(QWidget):
    def __init__(self, legend_figure):
        super().__init__()
        layout = QVBoxLayout()

        self.canvas = FigureCanvas(legend_figure)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)