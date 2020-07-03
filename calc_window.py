import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from utils import loadStylesheets
from node_editor_window import NodeEditorWindow
from calc_sub_window import CalculatorSubWindow
from calc_drag_listbox import QDMDragListbox
from utils import dumpException, pp
from calc_conf import *
import qss.nodeeditor_dark_resources
import json
import gan
from utils2 import *
import kthread
import time
from PIL import Image
DEBUG = True
class CalculatorWindow(NodeEditorWindow):
    def initUI(self):
        self.name_company = 'SPD'
        self.name_product = 'GanSta'
        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), "qss/nodeeditor.qss")
        loadStylesheets(
            os.path.join(os.path.dirname(__file__), "qss/nodeeditor-dark.qss"),
            self.stylesheet_filename
        )
        self.empty_icon = QIcon(".")
        if DEBUG:
            print("Registered nodes:")
            pp(CALC_NODES)
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)
        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)
        self.createNodesDock()
        self.createOutputDock()
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()
        self.readSettings()
        self.setWindowTitle("GanSta Alpha 1")
        self.emptyJson()
    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
            import sys
            sys.exit(0)
    def createActions(self):
        super().createActions()
        self.actClose = QAction("Cl&ose", self, statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll = QAction("Close &All", self, statusTip="Close all the windows", triggered=self.mdiArea.closeAllSubWindows)
        self.actTile = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.actCascade = QAction("&Cascade", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        self.actNext = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious = QAction("Pre&vious", self, shortcut=QKeySequence.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)
        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)
        self.actAbout = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)
    def getCurrentNodeEditorWidget(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None
    def onFileNew(self):
        try:
            subwnd = self.createMdiChild()
            subwnd.widget().fileNew()
            subwnd.show()
        except Exception as e: dumpException(e)
    def onFileOpen(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file', self.getFileDialogDirectory(), self.getFileDialogFilter())
        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        nodeeditor = CalculatorSubWindow()
                        if nodeeditor.fileLoad(fname):
                            self.statusBar().showMessage("File %s loaded" % fname, 5000)
                            nodeeditor.setTitle()
                            subwnd = self.createMdiChild(nodeeditor)
                            subwnd.show()
                        else:
                            nodeeditor.close()
        except Exception as e: dumpException(e)
    def about(self):
        QMessageBox.about(self, "GanSta",
                "<b>GanSta</b> a hello world for GAN"
                )
    def createMenus(self):
        super().createMenus()
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)
        self.menuBar().addSeparator()
        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.actAbout)
        self.editMenu.aboutToShow.connect(self.updateEditMenu)
    def updateMenus(self):
        active = self.getCurrentNodeEditorWidget()
        hasMdiChild = (active is not None)
        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        self.actClose.setEnabled(hasMdiChild)
        self.actCloseAll.setEnabled(hasMdiChild)
        self.actTile.setEnabled(hasMdiChild)
        self.actCascade.setEnabled(hasMdiChild)
        self.actNext.setEnabled(hasMdiChild)
        self.actPrevious.setEnabled(hasMdiChild)
        self.actSeparator.setVisible(hasMdiChild)
        self.updateEditMenu()
    def updateEditMenu(self):
        try:
            active = self.getCurrentNodeEditorWidget()
            hasMdiChild = (active is not None)
            self.actPaste.setEnabled(hasMdiChild)
            self.actCut.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actCopy.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actDelete.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actUndo.setEnabled(hasMdiChild and active.canUndo())
            self.actRedo.setEnabled(hasMdiChild and active.canRedo())
        except Exception as e: dumpException(e)
    def updateWindowMenu(self):
        self.windowMenu.clear()
        toolbar_nodes = self.windowMenu.addAction("Nodes Toolbar")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addAction(self.actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actNext)
        self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)
        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)
        for i, window in enumerate(windows):
            child = window.widget()
            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text
            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)
    def onWindowNodesToolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()
    def createToolBars(self):
        pass
    def createNodesDock(self):
        self.nodesListWidget = QDMDragListbox()
        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.nodesListWidget)
        self.nodesDock.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodesDock)
    def createOutputDock(self):
        self.edit3 = QProgressBar(self)
        self.edit2 = QPushButton("Stop", self)
        self.edit1 = QPushButton("Start", self)
        self.edit1.clicked.connect(self.loadSess)
        self.edit2.clicked.connect(self.stopAll)
        self.edit3.setMaximum(100)
        self.edit3.setMinimum(0)
        self.edit3.setValue(0)
        self.edit3.setGeometry(10, 120, 100, 30)
        self.edit4 = QPushButton("Output Path", self)
        self.edit5 = QPushButton("Open", self)
        self.pixmap = QPixmap("icons/x.png")
        self.lb4 = QLabel("Image", self)
        self.lb4.setObjectName("imagen")
        self.lb4.setAlignment(Qt.AlignCenter)
        self.lb4.setPixmap(self.pixmap)
        self.outDock = QDockWidget("Output")
        self.layout = QBoxLayout(2)
        self.layout.addWidget(self.edit1)
        self.layout.addWidget(self.edit2)
        self.layout.addWidget(self.edit3)
        self.layout.addWidget(self.lb4)
        self.layout.addWidget(self.edit4)
        self.layout.addWidget(self.edit5)
        self.dockedWidget = QWidget()
        self.outDock.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.layout)
        self.nodesDock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.outDock)
    def loop(self):
        while True:
            time.sleep(1)
            outdir = os.path.expanduser('~')
            log_dir = outdir + '/logs'
            if not os.path.exists(os.path.join(log_dir, "log")):
                with open(os.path.join(log_dir, "log"), 'w'): pass
            file1 = open(os.path.join(log_dir, "log"), "r")
            first = file1.readline()
            per = int(float(first)*100)
            if per == 99:
                per = 100
            file1.close()
            self.edit3.setValue(per)
            dir = os.path.join(outdir, 'samples')
            file1 = open(os.path.join(dir, 'log'), "r")
            first = file1.readline()
            print(first)
            if first != "0":
                mimi = QPixmap(first)
                self.lb4.setPixmap(mimi)
                self.lb4.setFixedWidth(256)
            file1.close()
    def loadSess(self):
        outdir = os.path.expanduser('~')
        log_dir = outdir + '/logs'
        pp = os.path.join(log_dir, "sess.json")
        with open(pp) as json_file:
            data = json.load(json_file)
        empty = False
        empty2 = False
        if data != None:
            y2 = json.loads(data)
            for i in y2:
                print(y2[i])
                if y2[i] == None:
                    empty = True
        else:
            empty2 = True
        if empty2 == True:
            QMessageBox.information(None, "Stop", "Make sure everything is ready first")
        if empty == True:
            QMessageBox.information(None, "Stop", "Make sure everything is ready first")
        if empty == False:
            self.x = gan.xx(y2['a'], y2['b'], y2['r'], y2['d'], y2['e'], y2['f'],
                       y2['g'],
                       y2['h'], y2['i'], y2['j'], y2['k'], y2['l'], y2['m'],
                       y2['n'],
                       y2['o'], y2['p'], y2['q'], y2['c'], y2['s'], y2['t'],
                       y2['u'],
                       y2['v'], y2['w'], y2['x'], y2['y'], y2['z'], y2['aa'],
                       y2['bb'],
                       y2['cc'], y2['dd'], y2['ee'], y2['ff'], y2['gg'])
            self.y = kthread.KThread(target=self.loop, args=())
            self.y.start()
    def stopAll(self):
        if self.x != None:
            self.x.terminate()
        if self.y != None:
            self.y.terminate()
    def emptyJson(self):
        outdir = os.path.expanduser('~')
        log_dir = outdir + '/logs'
        vj = {"a": None,}
        y = json.dumps(vj)
        pp = os.path.join(log_dir, "sess.json")
        check_folder(log_dir)
        with open(pp, 'w+') as outfile:
            json.dump(y, outfile)
    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
    def createMdiChild(self, child_widget=None):
        nodeeditor = child_widget if child_widget is not None else CalculatorSubWindow()
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        subwnd.setWindowIcon(self.empty_icon)
        nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        nodeeditor.addCloseEventListener(self.onSubWndClose)
        return subwnd
    def onSubWndClose(self, widget, event):
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()
    def findMdiChild(self, filename):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:
                return window
        return None
    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)
