# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
SOCKET_COLORS = [
    QColor("#74d6e0"),
    QColor("#eaadc7"),
    QColor("#9ecc96"),
    QColor("#c4b7ea"),
    QColor("#cedca5"),
    QColor("#9dbcea"),
    QColor("#e5be97"),
    QColor("#7bcaed"),
    QColor("#a3ead4"),
    QColor("#8dc6af"),
    QColor("#b6bed8"),
    QColor("#a3c1c2"),
]
class QDMGraphicsSocket(QGraphicsItem):
    def __init__(self, socket:'Socket'):
        super().__init__(socket.node.grNode)
        self.socket = socket
        self.isHighlighted = False
        self.radius = 6.0
        self.outline_width = 1.0
        self.initAssets()
    @property
    def socket_type(self):
        return self.socket.socket_type
    def getSocketColor(self, key):
        if type(key) == int: return SOCKET_COLORS[key]
        elif type(key) == str: return QColor(key)
        return Qt.transparent
    def changeSocketType(self):
        self._color_background = self.getSocketColor(self.socket_type)
        self._brush = QBrush(self._color_background)
        self.update()
    def initAssets(self):
        self._color_background = self.getSocketColor(self.socket_type)
        self._color_outline = QColor("#FF000000")
        self._color_highlight = QColor("#FF37A6FF")
        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._pen_highlight = QPen(self._color_highlight)
        self._pen_highlight.setWidthF(2.0)
        self._brush = QBrush(self._color_background)
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen if not self.isHighlighted else self._pen_highlight)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
    def boundingRect(self) -> QRectF:
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )