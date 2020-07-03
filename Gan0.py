from PyQt5.QtCore import *
from calc_conf import *
from calc_node_base import *
from utils import dumpException
import kthread
import os
import sys
import json
from utils2 import check_folder
class CalcGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 320
        self.height = 1080
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
class CalcGanContent(QDMNodeContentWidget):
    def initUI(self):
        self.lb14 = QLabel("n critic: ", self)
        self.lb14.setObjectName(self.node.content_label_objname27)
        self.edit14 = QLineEdit("1", self)
        self.edit14.setObjectName(self.node.content_label_objname28)
        self.lb13 = QLabel("n layer: ", self)
        self.lb13.setObjectName(self.node.content_label_objname25)
        self.edit13 = QLineEdit("4", self)
        self.edit13.setObjectName(self.node.content_label_objname26)
        self.lb12 = QLabel("sn: ", self)
        self.lb12.setObjectName(self.node.content_label_objname23)
        self.edit12 = QLineEdit("False", self)
        self.edit12.setObjectName(self.node.content_label_objname24)
        self.lb11 = QLabel("gp weight: ", self)
        self.lb11.setObjectName(self.node.content_label_objname21)
        self.edit11 = QLineEdit("10", self)
        self.edit11.setObjectName(self.node.content_label_objname22)
        self.lb10 = QLabel("r1 weight: ", self)
        self.lb10.setObjectName(self.node.content_label_objname19)
        self.edit10 = QLineEdit("1", self)
        self.edit10.setObjectName(self.node.content_label_objname20)
        self.lb9 = QLabel("cyc weight: ", self)
        self.lb9.setObjectName(self.node.content_label_objname17)
        self.edit9 = QLineEdit("1", self)
        self.edit9.setObjectName(self.node.content_label_objname18)
        self.lb8 = QLabel("ds weight: ", self)
        self.lb8.setObjectName(self.node.content_label_objname15)
        self.edit8 = QLineEdit("1", self)
        self.edit8.setObjectName(self.node.content_label_objname16)
        self.lb7 = QLabel("sty weight: ", self)
        self.lb7.setObjectName(self.node.content_label_objname13)
        self.edit7 = QLineEdit("1", self)
        self.edit7.setObjectName(self.node.content_label_objname14)
        self.lb6 = QLabel("adv weight: ", self)
        self.lb6.setObjectName(self.node.content_label_objname11)
        self.edit6 = QLineEdit("1", self)
        self.edit6.setObjectName(self.node.content_label_objname12)
        self.lb5 = QLabel("ema decay: ", self)
        self.lb5.setObjectName(self.node.content_label_objname9)
        self.edit5 = QLineEdit("0.999", self)
        self.edit5.setObjectName(self.node.content_label_objname10)
        self.lb4 = QLabel("lr: ", self)
        self.lb4.setObjectName(self.node.content_label_objname7)
        self.edit4 = QLineEdit("0.0001", self)
        self.edit4.setObjectName(self.node.content_label_objname8)
        self.lb3 = QLabel("Decay iters: ", self)
        self.lb3.setObjectName(self.node.content_label_objname5)
        self.edit3 = QLineEdit("50000", self)
        self.edit3.setObjectName(self.node.content_label_objname6)
        self.lb2 = QLabel("Decaying: ", self)
        self.lb2.setObjectName(self.node.content_label_objname3)
        self.edit2 = QLineEdit("True", self)
        self.edit2.setObjectName(self.node.content_label_objname4)
        self.lb1 = QLabel("GAN Type: ", self)
        self.lb1.setObjectName(self.node.content_label_objname1)
        self.edit1 = QComboBox(self)
        self.edit1.setObjectName(self.node.content_label_objname2)
        self.edit1.addItem("gan")
        self.edit1.addItem("lsgan")
        self.edit1.addItem("hinge")
        self.edit1.addItem("wgan-gp")
        self.edit1.addItem("wgan-lp")
        self.edit1.addItem("dragan")
    def serialize(self):
        res = super().serialize()
        return res
    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            return True & res
        except Exception as e:
            dumpException(e)
        return res
@register_node(OP_NODE_GAN)
class CalcNode_Gan(CalcNode):
    icon = "icons/mul.png"
    op_code = OP_NODE_GAN
    op_title = "GAN"
    content_label_objname1 = "calc_node_ganlb1"
    content_label_objname2 = "calc_node_ganedit1"
    content_label_objname3 = "calc_node_ganlb2"
    content_label_objname4 = "calc_node_ganedit2"
    content_label_objname5 = "calc_node_ganlb3"
    content_label_objname6 = "calc_node_ganedit3"
    content_label_objname7 = "calc_node_ganlb4"
    content_label_objname8 = "calc_node_ganedit4"
    content_label_objname9 = "calc_node_ganlb5"
    content_label_objname10 = "calc_node_ganedit5"
    content_label_objname11 = "calc_node_ganlb6"
    content_label_objname12 = "calc_node_ganedit6"
    content_label_objname13 = "calc_node_ganlb7"
    content_label_objname14 = "calc_node_ganedit7"
    content_label_objname15 = "calc_node_ganlb8"
    content_label_objname16 = "calc_node_ganedit8"
    content_label_objname17 = "calc_node_ganlb9"
    content_label_objname18 = "calc_node_ganedit9"
    content_label_objname19 = "calc_node_ganlb10"
    content_label_objname20 = "calc_node_ganedit10"
    content_label_objname21 = "calc_node_ganlb11"
    content_label_objname22 = "calc_node_ganedit11"
    content_label_objname23 = "calc_node_ganlb12"
    content_label_objname24 = "calc_node_ganedit12"
    content_label_objname25 = "calc_node_ganlb13"
    content_label_objname26 = "calc_node_ganedit13"
    content_label_objname27 = "calc_node_ganlb14"
    content_label_objname28 = "calc_node_ganedit14"
    GraphicsNode_class = CalcGraphicsNode
    def __init__(self, scene):
        super().__init__(scene, inputs=[0,1,2,3,4], outputs=[])
        self.eval()
    def initInnerClasses(self):
        self.content = CalcGanContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit2.textChanged.connect(self.onInputChanged)
    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return
        else:
            value = input_node.evalImplementation()
            augment_flag = value[4]
            dataset = value[0]
            img_ch = int(value[3])
            img_height = int(value[1])
            img_width = int(value[2])
        input_node1 = self.getInput(1)
        if not input_node1:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return
        else:
            value1 = input_node1.eval()
            phase = value1
        input_node2 = self.getInput(2)
        if not input_node2:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return
        else:
            value2 = input_node2.eval()
            gpu_num = int(value2)
        input_node3 = self.getInput(3)
        if not input_node3:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return
        else:
            value3 = input_node3.eval()
            batch_size = int(value3[0])
            iteration = int(value3[1])
        input_node4 = self.getInput(4)
        if not input_node4:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return
        else:
            value4 = input_node4.eval()
            num_style = int(value4[0])
            style_dim = int(value4[1])
        adv_weight = self.content.edit6.text()
        adv_weight = int(adv_weight)
        ch = 32
        cyc_weight = self.content.edit9.text()
        cyc_weight = int(cyc_weight)
        if self.content.edit2.text() == "True":
             decay_flag = True
        else:
             decay_flag = False
        decay_iter = self.content.edit3.text()
        decay_iter = int(decay_iter)
        ds_weight = self.content.edit8.text()
        ds_weight = int(ds_weight)
        ema_decay = self.content.edit5.text()
        ema_decay = float(ema_decay)
        gan_type = self.content.edit1.currentText()
        gp_weight = self.content.edit11.text()
        gp_weight = int(gp_weight)
        lr = self.content.edit4.text()
        lr = float(lr)
        n_critic = self.content.edit14.text()
        n_critic = int(n_critic)
        n_layer = self.content.edit13.text()
        n_layer = int(n_layer)
        print_freq = 2
        r1_weight = self.content.edit10.text()
        r1_weight = int(r1_weight)
        save_freq = 10
        if self.content.edit3.text() == "True":
            sn = True
        else:
            sn = False
        sty_weight = self.content.edit7.text()
        sty_weight = int(sty_weight)
        outdir = os.path.expanduser('~')
        checkpoint_dir = outdir + '/checkpoint'
        refer_img_path = outdir + '/refer_img.jpg'
        result_dir = outdir + '/results'
        sample_dir = outdir + '/samples'
        log_dir = outdir + '/logs'
        self.value = [adv_weight, augment_flag, batch_size, ch, checkpoint_dir, cyc_weight, dataset, decay_flag, decay_iter, ds_weight, ema_decay, gan_type, gp_weight, gpu_num, img_ch, img_height, img_width, iteration, log_dir, lr, n_critic, n_layer, num_style, phase, print_freq, r1_weight, refer_img_path, result_dir, sample_dir, save_freq, sn, sty_weight, style_dim]
        vj = {"a": adv_weight, "b": augment_flag, "c": batch_size, "d": ch, "e": checkpoint_dir, "f": cyc_weight,
              "g": dataset, "h": decay_flag, "i": decay_iter, "j": ds_weight, "k": ema_decay, "l": gan_type,
              "m": gp_weight, "n": gpu_num, "o": img_ch, "p": img_height, "q": img_width, "r": iteration, "s": log_dir,
              "t": lr, "u": n_critic, "v": n_layer, "w": num_style, "x": phase, "y": print_freq, "z": r1_weight,
              "aa": refer_img_path, "bb": result_dir, "cc": sample_dir, "dd": save_freq, "ee": sn, "ff": sty_weight,
              "gg": style_dim}
        print(value)
        y = json.dumps(vj)
        y2 = json.loads(y)
        print(y2['a'])
        pp = os.path.join(log_dir, "sess.json")
        check_folder(log_dir)
        with open(pp, 'w+') as outfile:
            json.dump(y, outfile)
        self.markDirty(False)
        self.markInvalid(False)
        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()
        self.grNode.setToolTip("")
        return self.value
