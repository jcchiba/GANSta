# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from node_scene import Scene, InvalidFile
from node_node import Node
from node_edge import Edge, EDGE_TYPE_BEZIER
from node_graphics_view import QDMGraphicsView
class NodeEditorWidget(QWidget):
    Scene_class = Scene
    def __init__(self, parent:QWidget=None):
        super().__init__(parent)
        self.filename = None
        self.initUI()
    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.scene = self.__class__.Scene_class()
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)
    def isModified(self) -> bool:
        return self.scene.isModified()
    def isFilenameSet(self) -> bool:
        return self.filename is not None
    def getSelectedItems(self) -> list:
        return self.scene.getSelectedItems()
    def hasSelectedItems(self) -> bool:
        return self.getSelectedItems() != []
    def canUndo(self) -> bool:
        return self.scene.history.canUndo()
    def canRedo(self) -> bool:
        return self.scene.history.canRedo()
    def getUserFriendlyFilename(self) -> str:
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")
    def fileNew(self):
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()
    def fileLoad(self, filename:str):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            return True
        except InvalidFile as e:
            print(e)
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(filename), str(e))
            return False
        finally:
            QApplication.restoreOverrideCursor()
    def fileSave(self, filename:str=None):
        if filename is not None: self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        return True
    def addNodes(self):
        node1 = Node(self.scene, "Dataset Path", inputs=[0], outputs=[1])
        node2 = Node(self.scene, "Image Settings", inputs=[1], outputs=[1])
        node3 = Node(self.scene, "Train", inputs=[0], outputs=[1])
        node4 = Node(self.scene, "GPU", inputs=[0], outputs=[1])
        node5 = Node(self.scene, "Batch", inputs=[0], outputs=[1])
        node6 = Node(self.scene, "Dimensions", inputs=[0], outputs=[1])
        node7 = Node(self.scene, "GAN", inputs=[0,1,2,3,4,5,5,5,5,7], outputs=[2])
        node8 = Node(self.scene, "Start", inputs=[0], outputs=[0])
        node9 = Node(self.scene, "Output", inputs=[0], outputs=[1])
        node1.setPos(-450, -150)
        node2.setPos(-200, -150)
        node3.setPos(-450, 200)
        node4.setPos(-450, 350)
        node5.setPos(-450, 500)
        node6.setPos(-200, 200)
        node7.setPos(150, -150)
        node8.setPos(400, -150)
        node9.setPos(400, 250)
        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[0], node7.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge3 = Edge(self.scene, node3.outputs[0], node7.inputs[1], edge_type=EDGE_TYPE_BEZIER)
        edge4 = Edge(self.scene, node4.outputs[0], node7.inputs[2], edge_type=EDGE_TYPE_BEZIER)
        edge5 = Edge(self.scene, node5.outputs[0], node7.inputs[3], edge_type=EDGE_TYPE_BEZIER)
        edge6 = Edge(self.scene, node6.outputs[0], node7.inputs[4], edge_type=EDGE_TYPE_BEZIER)
        edge7 = Edge(self.scene, node7.outputs[0], node8.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge8 = Edge(self.scene, node7.outputs[0], node9.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        self.scene.history.storeInitialHistoryStamp()
    def addCustomNode(self):
        from nodeeditor.node_content_widget import QDMNodeContentWidget
        from nodeeditor.node_serializable import Serializable
        class NNodeContent(QLabel):  
            def __init__(self, node, parent=None):
                super().__init__("Hello")
                self.node = node
                self.setParent(parent)
        class NNode(Node):
            NodeContent_class = NNodeContent
        self.scene.setNodeClassSelector(lambda data: NNode)
        node = NNode(self.scene, "A Custom Node 1", inputs=[0, 1, 2])
        print("node content:", node.content)
    def addDebugContent(self):
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)
        rect = self.grScene.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)
        text = self.grScene.addText("This is my Awesome text!", QFont("Ubuntu"))
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))
        widget1 = QPushButton("Hello World")
        proxy1 = self.grScene.addWidget(widget1)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)
        widget2 = QTextEdit()
        proxy2 = self.grScene.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 60)
        line = self.grScene.addLine(-200, -200, 400, -100, outlinePen)
        line.setFlag(QGraphicsItem.ItemIsMovable)
        line.setFlag(QGraphicsItem.ItemIsSelectable)
