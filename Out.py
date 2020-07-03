from PyQt5.QtCore import *
from calc_conf import *
from calc_node_base import *
from utils import dumpException
import os
import sys
from utils2 import *
import kthread
class CalcGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 320
        self.height = 560
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
class CalcOutContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit2 = QPushButton("Open", self)
        self.edit2.setObjectName(self.node.content_label_objname7)
        self.pixmap = QPixmap("icons/256x256.png")
        self.lb4 = QLabel("Image", self)
        self.lb4.setPixmap(self.pixmap)
        self.lb4.setObjectName(self.node.content_label_objname6)
        self.lb3 = QLabel("Preview: ", self)
        self.lb3.setObjectName(self.node.content_label_objname5)
        self.lb2 = QLabel("Output Path: ", self)
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
@register_node(OP_NODE_OUT)
class CalcNode_Out(CalcNode):
    icon = "icons/o.png"
    op_code = OP_NODE_OUT
    op_title = "Out"
    content_label_objname1 = "calc_node_outlb"
    content_label_objname2 = "calc_node_outpath"
    content_label_objname3 = "calc_node_outlb2"
    content_label_objname4 = "calc_node_outedit"
    content_label_objname5 = "calc_node_outlb3"
    content_label_objname6 = "calc_node_outlb4"
    content_label_objname7 = "calc_node_outedit2"
    GraphicsNode_class = CalcGraphicsNode
    def __init__(self, scene):
        super().__init__(scene, inputs=[6], outputs=[])
        self.eval()
    def loop(self):
        while True:
            time.sleep(1)
            dir = os.path.join(str(self.content.edit.text()), 'samples')
            file1 = open(os.path.join(dir,'log'), "r")
            first = file1.readline()
            if first != "0":
                mimi = QPixmap(first)
                self.content.lb4.setPixmap(mimi)
            file1.close()
        return
    def initInnerClasses(self):
        self.content = CalcOutContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)
        self.content.path.clicked.connect(self.selectDirectory)
    def selectDirectory(self):
        dirName = QFileDialog.getExistingDirectory(None, 'Select Directory', os.path.expanduser('~') + '/Desktop')
        if dirName != "":
            self.content.edit.setText(dirName)
            check_folder(os.path.join(dirName, "samples"))
            x2 = kthread.KThread(target=self.loop, args=())
            x2.start()
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
