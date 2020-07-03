# -*- coding: utf-8 -*-
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
EDGE_CP_ROUNDNESS = 100     
class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge:'Edge', parent:QWidget=None):
        super().__init__(parent)
        self.edge = edge
        self._last_selected_state = False
        self.hovered = False
        self.posSource = [0, 0]
        self.posDestination = [200, 100]
        self.initAssets()
        self.initUI()
    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)
    def initAssets(self):
        self._color = self._default_color = QColor("#001000")
        self._color_selected = QColor("#00ff00")
        self._color_hovered = QColor("#FF37A6FF")
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidthF(3.0)
        self._pen_selected.setWidthF(3.0)
        self._pen_dragging.setWidthF(3.0)
        self._pen_hovered.setWidthF(5.0)
    def changeColor(self, color):
        self._color = QColor(color) if type(color) == str else color
        self._pen = QPen(self._color)
        self._pen.setWidthF(3.0)
    def setColorFromSockets(self) -> bool:
        socket_type_start = self.edge.start_socket.socket_type
        socket_type_end = self.edge.end_socket.socket_type
        if socket_type_start != socket_type_end: return False
        self.changeColor(self.edge.start_socket.grSocket.getSocketColor(socket_type_start))
    def onSelected(self):
        self.edge.scene.grScene.itemSelected.emit()
    def doSelect(self, new_state:bool=True):
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state: self.onSelected()
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            self.edge.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()
    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = True
        self.update()
    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = False
        self.update()
    def setSource(self, x:float, y:float):
        self.posSource = [x, y]
    def setDestination(self, x:float, y:float):
        self.posDestination = [x, y]
    def boundingRect(self) -> QRectF:
        return self.shape().boundingRect()
    def shape(self) -> QPainterPath:
        return self.calcPath()
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.calcPath())
        painter.setBrush(Qt.NoBrush)
        if self.hovered and self.edge.end_socket is not None:
            painter.setPen(self._pen_hovered)
            painter.drawPath(self.path())
        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.drawPath(self.path())
    def intersectsWith(self, p1:QPointF, p2:QPointF) -> bool:
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)
    def calcPath(self) -> QPainterPath:
        raise NotImplemented("This method has to be overriden in a child class")
class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    def calcPath(self) -> QPainterPath:
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path
class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    def calcPath(self) -> QPainterPath:
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0]) * 0.5
        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0
        if self.edge.start_socket is not None:
            ssin = self.edge.start_socket.is_input
            ssout = self.edge.start_socket.is_output
            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1
                cpy_d = (
                    (s[1] - d[1]) / math.fabs(
                        (s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS
                cpy_s = (
                    (d[1] - s[1]) / math.fabs(
                        (d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo( s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.posDestination[0], self.posDestination[1])
        return path
