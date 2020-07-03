from PyQt5.QtCore import *
from calc_conf import *
from calc_node_base import *
from utils import dumpException
from gan import *
import multiprocessing
import os
import sys
class CalcGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 320
        self.height = 420
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
class CalcImgContent(QDMNodeContentWidget):
    def initUI(self):
        self.lb5 = QLabel("Augmented: ", self)
        self.lb5.setObjectName(self.node.content_label_objname9)
        self.edit5 = QCheckBox("Activated", self)
        self.edit5.setObjectName(self.node.content_label_objname10)
        self.lb4 = QLabel("Channel: ", self)
        self.lb4.setObjectName(self.node.content_label_objname7)
        self.edit4 = QLineEdit("3", self)
        self.edit4.setObjectName(self.node.content_label_objname8)
        self.lb3 = QLabel("Width: ", self)
        self.lb3.setObjectName(self.node.content_label_objname5)
        self.edit3 = QLineEdit("256", self)
        self.edit3.setObjectName(self.node.content_label_objname6)
        self.lb2 = QLabel("Height: ", self)
        self.lb2.setObjectName(self.node.content_label_objname3)
        self.edit2 = QLineEdit("256", self)
        self.edit2.setObjectName(self.node.content_label_objname4)
        self.lb1 = QLabel("Dataset: ", self)
        self.lb1.setObjectName(self.node.content_label_objname1)
        self.edit1 = QLineEdit("", self)
        self.edit1.setObjectName(self.node.content_label_objname2)
    def serialize(self):
        res = super().serialize()
        self.d = self.edit1.text()
        self.h = self.edit2.text()
        self.w = self.edit3.text()
        self.c = self.edit4.text()
        self.a = self.edit5.checkState()
        if self.a != 0:
            self.a = True
        else:
            self.a = False
        res['value'] = [self.a, self.c, self.w, self.h, self.d]
        return res
    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            return True & res
        except Exception as e:
            dumpException(e)
        return res
@register_node(OP_NODE_IMGSETTINGS)
class CalcNode_Img(CalcNode):
    icon = "icons/i.png"
    op_code = OP_NODE_IMGSETTINGS
    op_title = "Image Settings"
    content_label_objname1 = "calc_node_imglb1"
    content_label_objname2 = "calc_node_imgedit1"
    content_label_objname3 = "calc_node_imglb2"
    content_label_objname4 = "calc_node_imgedit2"
    content_label_objname5 = "calc_node_imglb3"
    content_label_objname6 = "calc_node_imgedit3"
    content_label_objname7 = "calc_node_imglb4"
    content_label_objname8 = "calc_node_imgedit4"
    content_label_objname9 = "calc_node_imglb5"
    content_label_objname10 = "calc_node_imgedit5"
    GraphicsNode_class = CalcGraphicsNode
    def __init__(self, scene):
        super().__init__(scene, inputs=[0], outputs=[0])
        self.eval()
    def initInnerClasses(self):
        self.content = CalcImgContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit1.textChanged.connect(self.onInputChanged)
    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return
        value2 = input_node.eval()
        if value2 is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return
        self.content.edit1.setText(value2)
        self.d = self.content.edit1.text()
        self.h = self.content.edit2.text()
        self.w = self.content.edit3.text()
        self.c = self.content.edit4.text()
        self.a = self.content.edit5.checkState()
        if self.a!=0:
            self.a = True
        else:
            self.a = False
        value = [self.d, self.h, self.w, self.c, self.a]
        self.markInvalid(False)
        self.markDirty(False)
        self.grNode.setToolTip("")
        return value
