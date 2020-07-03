from PyQt5.QtCore import *
from calc_conf import *
from calc_node_base import *
from utils import dumpException
import gan
import os
from utils2 import *
import kthread
import time
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
class CalcActionContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit3 = QProgressBar(self)
        self.edit3.setObjectName(self.node.content_label_objname4)
        self.edit2 = QPushButton("Stop", self)
        self.edit2.setObjectName(self.node.content_label_objname3)
        self.edit1 = QPushButton("Start", self)
        self.edit1.setObjectName(self.node.content_label_objname2)
        self.lb1 = QLabel("Action", self)
        self.lb1.setObjectName(self.node.content_label_objname1)
        self.edit3.setMaximum(100)
        self.edit3.setMinimum(0)
        self.edit3.setValue(0)
        self.edit3.setGeometry(10, 120, 100, 30)
    def serialize(self):
        res = super().serialize()
        return res
    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            return True & res
        except Exception as e:
            dumpException(e)
        return res
@register_node(OP_NODE_ACTION)
class CalcNode_Action(CalcNode):
    icon = "icons/a.png"
    op_code = OP_NODE_ACTION
    op_title = "Action"
    content_label_objname1 = "calc_node_actlb"
    content_label_objname2 = "calc_node_actedit1"
    content_label_objname3 = "calc_node_actedit2"
    content_label_objname4 = "calc_node_actedit3"
    si = False
    xxx = []
    args = []
    GraphicsNode_class = CalcGraphicsNode
    def __init__(self, scene):
        super().__init__(scene, inputs=[5], outputs=[])
        self.eval()
    def initInnerClasses(self):
        self.content = CalcActionContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit1.clicked.connect(self.runBitch)
        self.content.edit2.clicked.connect(self.stopBitch)
    def loop(self):
        while True:
            time.sleep(1)
            file1 = open(os.path.join(self.args[18], "log"), "r")
            first = file1.readline()
            per = int(float(first)*100)
            if per == 99:
                per = 100
                self.stopBitch()
            file1.close()
            self.content.edit3.setValue(per)
        return
    def runBitch(self):
        bb= os.path.basename(self.args[6])
        patho = os.path.join(self.args[18] , bb)
        check_folder(self.args[18])
        file1 = open(os.path.join(self.args[18] ,"log"), "w+")
        file1.write("0")
        file1.close()
        if self.si == True:
            x = gan.xx(self.args[0], self.args[1], self.args[17], self.args[3], self.args[4], self.args[5],
               self.args[6],
               self.args[7], self.args[8], self.args[9], self.args[10], self.args[11], self.args[12],
               self.args[13],
               self.args[14], self.args[15], self.args[16], self.args[2], self.args[18], self.args[19],
               self.args[20],
               self.args[21], self.args[22], self.args[23], self.args[24], self.args[25], self.args[26],
               self.args[27],
               self.args[28], self.args[29], self.args[30], self.args[31], self.args[32])
            x2 = kthread.KThread(target=self.loop, args=())
            x2.start()
        if self.si == False:
            QMessageBox.information(None, "Stop", "Prepare everything first")
        return
    def stopBitch(self):
        for i in self.xxx:
            i.terminate()
        return
    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return
        val = input_node.eval()
        print(val)
        print(len(val))
        self.args = val
        if val is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            self.si = False
            return
        else:
            self.si = True
        self.markInvalid(False)
        self.markDirty(False)
        self.grNode.setToolTip("")
        return val
