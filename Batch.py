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
        self.width = 120
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
class CalcBatchContent(QDMNodeContentWidget):
    def initUI(self):
        self.lb2 = QLabel("Batch size: ", self)
        self.lb2.setObjectName(self.node.content_label_objname3)
        self.edit2 = QLineEdit("1", self)
        self.edit2.setObjectName(self.node.content_label_objname4)
        self.lb1 = QLabel("Iterations: ", self)
        self.lb1.setObjectName(self.node.content_label_objname1)
        self.edit1 = QLineEdit("100000", self)
        self.edit1.setObjectName(self.node.content_label_objname2)
    def serialize(self):
        a2 = [self.edit1.text(), self.edit2.text()]
        res = super().serialize()
        res['value'] = a2
        return res
    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            return True & res
        except Exception as e:
            dumpException(e)
        return res
@register_node(OP_NODE_BATCH)
class CalcNode_Batch(CalcNode):
    icon = "icons/b.png"
    op_code = OP_NODE_BATCH
    op_title = "Batch Settings"
    content_label_objname1 = "calc_node_batchlb1"
    content_label_objname2 = "calc_node_batchedit1"
    content_label_objname3 = "calc_node_batchlb2"
    content_label_objname4 = "calc_node_batchedit2"
    GraphicsNode_class = CalcGraphicsNode
    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()
    def initInnerClasses(self):
        self.content = CalcBatchContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit1.textChanged.connect(self.onInputChanged)
        self.content.edit2.textChanged.connect(self.onInputChanged)
    def evalImplementation(self):
        a3 =  [self.content.edit1.text(), self.content.edit2.text()]
        u_value = a3
        self.value = u_value
        self.markDirty(False)
        self.markInvalid(False)
        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()
        self.grNode.setToolTip("")
        self.evalChildren()
        return self.value
