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
        self.height = 130
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
class CalcModeContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit2 = QCheckBox("Test", self)
        self.edit2.setObjectName(self.node.content_label_objname3)
        self.edit1 = QCheckBox("Train", self)
        self.edit1.setObjectName(self.node.content_label_objname2)
        self.lb1 = QLabel("Select Mode: ", self)
        self.lb1.setObjectName(self.node.content_label_objname1)
        self.edit1.setChecked(False)
        self.edit2.setChecked(False)
    def serialize(self):
        res = super().serialize()
        if self.edit1.checkState() != 0:
            self.edit2.setChecked(False)
        if self.edit2.checkState() != 0:
            self.edit1.setChecked(False)
        return res
    def deserialize(self, data, hashmap={}):
        if self.edit1.checkState() != 0:
            self.edit2.setChecked(False)
        if self.edit2.checkState() != 0:
            self.edit1.setChecked(False)
        res = super().deserialize(data, hashmap)
        try:
            return True & res
        except Exception as e:
            dumpException(e)
        return res
@register_node(OP_NODE_MODE)
class CalcNode_Mode(CalcNode):
    icon = "icons/t.png"
    op_code = OP_NODE_MODE
    op_title = "Mode"
    content_label_objname1 = "calc_node_modelb"
    content_label_objname2 = "calc_node_modeedit1"
    content_label_objname3 = "calc_node_modeedit2"
    GraphicsNode_class = CalcGraphicsNode
    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.eval()
    def initInnerClasses(self):
        self.content = CalcModeContent(self)
        self.grNode = CalcGraphicsNode(self)
    def evalImplementation(self):
        if self.content.edit1.checkState() != 0:
            self.content.edit2.setChecked(False)
            u_value = "train"
        if self.content.edit2.checkState() != 0:
            self.content.edit1.setChecked(False)
            u_value = "test"
        s_value = u_value
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)
        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()
        self.grNode.setToolTip("")
        self.evalChildren()
        return self.value
