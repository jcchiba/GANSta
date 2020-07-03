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
        self.height = 120
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
class CalcGPUContent(QDMNodeContentWidget):
    def initUI(self):
        self.lb1 = QLabel("Select Mode: ", self)
        self.lb1.setObjectName(self.node.content_label_objname1)
        self.edit1 = QLineEdit("1", self)
        self.edit1.setObjectName(self.node.content_label_objname2)
    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit1.text()
        return res
    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit1.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res
@register_node(OP_NODE_GPU)
class CalcNode_GPU(CalcNode):
    icon = "icons/g.png"
    op_code = OP_NODE_GPU
    op_title = "GPU"
    content_label_objname1 = "calc_node_gpulb"
    content_label_objname2 = "calc_node_gpuedit1"
    GraphicsNode_class = CalcGraphicsNode
    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[2])
        self.eval()
    def initInnerClasses(self):
        self.content = CalcGPUContent(self)
        self.grNode = CalcGraphicsNode(self)
    def evalImplementation(self):
        u_value = self.content.edit1.text()
        s_value = str(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)
        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()
        self.grNode.setToolTip("")
        self.evalChildren()
        return self.value
