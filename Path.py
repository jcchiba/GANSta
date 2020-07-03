from PyQt5.QtCore import *
from calc_conf import *
from calc_node_base import *
from utils import dumpException
import multiprocessing
import os
import sys
class CalcGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 320
        self.height = 200
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10
    def initAssets(self):
        super().initAssets()
        self.icons = QImage("icons/status_icons.png")
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0
        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )
class CalcDatasetContent(QDMNodeContentWidget):
    def initUI(self):
        self.lb2 = QLabel("Dataset: ", self)
        self.lb2.setObjectName(self.node.content_label_objname3)
        self.edit = QLineEdit("", self)
        self.edit.setObjectName(self.node.content_label_objname4)
        self.lb = QLabel("Path: ", self)
        self.lb.setObjectName(self.node.content_label_objname1)
        self.path = QPushButton("Get Path", self)
        self.path.setObjectName(self.node.content_label_objname2)
    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res
    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res
@register_node(OP_NODE_DATASET)
class CalcNode_Dataset(CalcNode):
    icon = "icons/d.png"
    op_code = OP_NODE_DATASET
    op_title = "Dataset"
    content_label_objname1 = "calc_node_inputlb"
    content_label_objname2 = "calc_node_inputpath"
    content_label_objname3 = "calc_node_inputlb2"
    content_label_objname4 = "calc_node_inputedit"
    GraphicsNode_class = CalcGraphicsNode
    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[0])
        self.eval()
    def initInnerClasses(self):
        self.content = CalcDatasetContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)
        self.content.path.clicked.connect(self.selectDirectory)
    def selectDirectory(self):
        dirName = QFileDialog.getExistingDirectory(None, 'Select Directory', os.path.expanduser('~') + '/Desktop')
        if dirName != "":
            self.content.edit.setText(dirName)
    def evalImplementation(self):
        u_value = self.content.edit.text()
        s_value = str(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)
        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()
        self.grNode.setToolTip("")
        self.evalChildren()
        return self.value
