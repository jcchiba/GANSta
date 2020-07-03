# -*- coding: utf-8 -*-
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
class QDMGraphicsScene(QGraphicsScene):
    itemSelected = pyqtSignal()
    itemsDeselected = pyqtSignal()
    def __init__(self, scene:'Scene', parent:QWidget=None):
        super().__init__(parent)
        self.scene = scene
        self.gridSize = 20
        self.gridSquares = 5
        self.initAssets()
        self.setBackgroundBrush(self._color_background)
    def initAssets(self):
        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")
        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)
    def dragMoveEvent(self, event):
        pass
    def setGrScene(self, width:int, height:int):
        self.setSceneRect(-width // 2, -height // 2, width, height)
    def drawBackground(self, painter:QPainter, rect:QRect):
        super().drawBackground(painter, rect)
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))
        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if (x % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(x, top, x, bottom))
            else: lines_dark.append(QLine(x, top, x, bottom))
        for y in range(first_top, bottom, self.gridSize):
            if (y % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(left, y, right, y))
            else: lines_dark.append(QLine(left, y, right, y))
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)
        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)