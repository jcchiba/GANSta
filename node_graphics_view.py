# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge
from node_edge import Edge, EDGE_TYPE_BEZIER
from node_graphics_cutline import QDMCutLine
from utils import dumpException
MODE_NOOP = 1               
MODE_EDGE_DRAG = 2          
MODE_EDGE_CUT = 3           
EDGE_DRAG_START_THRESHOLD = 50
DEBUG = False
DEBUG_MMB_SCENE_ITEMS = False
class QDMGraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)
    def __init__(self, grScene:'QDMGraphicsScene', parent:'QWidget'=None):
        super().__init__(parent)
        self.grScene = grScene
        self.initUI()
        self.setScene(self.grScene)
        self.mode = MODE_NOOP
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False
        self.last_scene_mouse_position = QPoint(0,0)
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]
        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)
        self._drag_enter_listeners = []
        self._drop_listeners = []
    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)
    def dragEnterEvent(self, event:QDragEnterEvent):
        for callback in self._drag_enter_listeners: callback(event)
    def dropEvent(self, event:QDropEvent):
        for callback in self._drop_listeners: callback(event)
    def addDragEnterListener(self, callback:'function'):
        self._drag_enter_listeners.append(callback)
    def addDropListener(self, callback:'function'):
        self._drop_listeners.append(callback)
    def mousePressEvent(self, event:QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)
    def mouseReleaseEvent(self, event:QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)
    def middleMouseButtonPress(self, event:QMouseEvent):
        item = self.getItemAtClick(event)
        if DEBUG_MMB_SCENE_ITEMS:
            if isinstance(item, QDMGraphicsEdge):
                print("MMB DEBUG:", item.edge,"\n\t", item.edge.grEdge if item.edge.grEdge is not None else None)
            if isinstance(item, QDMGraphicsSocket):
                print("MMB DEBUG:", item.socket, "socket_type:", item.socket.socket_type,
                      "has edges:", "no" if item.socket.edges == [] else "")
                if item.socket.edges:
                    for edge in item.socket.edges: print("\t", edge)
        if DEBUG_MMB_SCENE_ITEMS and (item is None):
            print("SCENE:")
            print("  Nodes:")
            for node in self.grScene.scene.nodes: print("\t", node)
            print("  Edges:")
            for edge in self.grScene.scene.edges: print("\t", edge, "\n\t\tgrEdge:", edge.grEdge if edge.grEdge is not None else None)
            if event.modifiers() & Qt.CTRL:
                print("  Graphic Items in GraphicScene:")
                for item in self.grScene.items():
                    print('    ', item)
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)
    def middleMouseButtonRelease(self, event:QMouseEvent):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
    def leftMouseButtonPress(self, event:QMouseEvent):
        item = self.getItemAtClick(event)
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return
        if isinstance(item, QDMGraphicsSocket):
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return
        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return
        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True
        super().mousePressEvent(event)
    def leftMouseButtonRelease(self, event:QMouseEvent):
        item = self.getItemAtClick(event)
        try:
            if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
                if event.modifiers() & Qt.ShiftModifier:
                    event.ignore()
                    fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                            Qt.LeftButton, Qt.NoButton,
                                            event.modifiers() | Qt.ControlModifier)
                    super().mouseReleaseEvent(fakeEvent)
                    return
            if self.mode == MODE_EDGE_DRAG:
                if self.distanceBetweenClickAndReleaseIsOff(event):
                    res = self.edgeDragEnd(item)
                    if res: return
            if self.mode == MODE_EDGE_CUT:
                self.cutIntersectingEdges()
                self.cutline.line_points = []
                self.cutline.update()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.mode = MODE_NOOP
                return
            if self.rubberBandDraggingRectangle:
                self.rubberBandDraggingRectangle = False
                current_selected_items = self.grScene.selectedItems()
                if current_selected_items != self.grScene.scene._last_selected_items:
                    if current_selected_items == []:
                        self.grScene.itemsDeselected.emit()
                    else:
                        self.grScene.itemSelected.emit()
                    self.grScene.scene._last_selected_items = current_selected_items
                return
            if item is None:
                self.grScene.itemsDeselected.emit()
        except: dumpException()
        super().mouseReleaseEvent(event)
    def rightMouseButtonPress(self, event:QMouseEvent):
        super().mousePressEvent(event)
    def rightMouseButtonRelease(self, event:QMouseEvent):
        super().mouseReleaseEvent(event)
    def mouseMoveEvent(self, event:QMouseEvent):
        scenepos = self.mapToScene(event.pos())
        if self.mode == MODE_EDGE_DRAG:
            if self.drag_edge is not None and self.drag_edge.grEdge is not None:
                self.drag_edge.grEdge.setDestination(scenepos.x(), scenepos.y())
                self.drag_edge.grEdge.update()
            else:
                print(">>> Want to update self.drag_edge grEdge, but it's None!!!")
        if self.mode == MODE_EDGE_CUT and self.cutline is not None:
            self.cutline.line_points.append(scenepos)
            self.cutline.update()
        self.last_scene_mouse_position = scenepos
        self.scenePosChanged.emit( int(scenepos.x()), int(scenepos.y()) )
        super().mouseMoveEvent(event)
    def keyPressEvent(self, event:QKeyEvent):
        super().keyPressEvent(event)
    def cutIntersectingEdges(self):
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]
            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()
        self.grScene.scene.history.storeHistory("Delete cutted edges", setModified=True)
    def deleteSelected(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()
        self.grScene.scene.history.storeHistory("Delete selected", setModified=True)
    def debug_modifiers(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
        if event.modifiers() & Qt.ControlModifier: out += "CTRL "
        if event.modifiers() & Qt.AltModifier: out += "ALT "
        return out
    def getItemAtClick(self, event:QEvent) -> 'QGraphicsItem':
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj
    def edgeDragStart(self, item:'QGraphicsItem'):
        try:
            if DEBUG: print('View::edgeDragStart ~ Start dragging edge')
            if DEBUG: print('View::edgeDragStart ~   assign Start Socket to:', item.socket)
            self.drag_start_socket = item.socket
            self.drag_edge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
            if DEBUG: print('View::edgeDragStart ~   dragEdge:', self.drag_edge)
        except Exception as e: dumpException(e)
    def edgeDragEnd(self, item:'QGraphicsItem'):
        self.mode = MODE_NOOP
        if DEBUG: print('View::edgeDragEnd ~ End dragging edge')
        self.drag_edge.remove(silent=True)      
        self.drag_edge = None
        try:
            if isinstance(item, QDMGraphicsSocket):
                if item.socket != self.drag_start_socket:
                    for socket in (item.socket, self.drag_start_socket):
                        if not socket.is_multi_edges:
                            if socket.is_input:
                                socket.removeAllEdges(silent=True)
                            else:
                                socket.removeAllEdges(silent=False)
                    new_edge = Edge(self.grScene.scene, self.drag_start_socket, item.socket, edge_type=EDGE_TYPE_BEZIER)
                    if DEBUG: print("View::edgeDragEnd ~  created new edge:", new_edge, "connecting", new_edge.start_socket, "<-->", new_edge.end_socket)
                    for socket in [self.drag_start_socket, item.socket]:
                        socket.node.onEdgeConnectionChanged(new_edge)
                        if socket.is_input: socket.node.onInputChanged(socket)
                    self.grScene.scene.history.storeHistory("Created new edge by dragging", setModified=True)
                    return True
        except Exception as e: dumpException(e)
        if DEBUG: print('View::edgeDragEnd ~ everything done.')
        return False
    def distanceBetweenClickAndReleaseIsOff(self, event:QMouseEvent) -> bool:
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD*EDGE_DRAG_START_THRESHOLD
        return (dist_scene.x()*dist_scene.x() + dist_scene.y()*dist_scene.y()) > edge_drag_threshold_sq
    def wheelEvent(self, event:QWheelEvent):
        zoomOutFactor = 1 / self.zoomInFactor
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep
        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)
