# -*- coding: utf-8 -*-
from node_graphics_edge import QDMGraphicsEdge
from utils import dumpException
DEBUG = False
DEBUG_SELECTION = False
class SceneHistory():
    def __init__(self, scene:'Scene'):
        self.scene = scene
        self.clear()
        self.history_limit = 32
        self.undo_selection_has_changed = False
        self._history_modified_listeners = []
        self._history_stored_listeners = []
        self._history_restored_listeners = []
    def clear(self):
        self.history_stack = []
        self.history_current_step = -1
    def storeInitialHistoryStamp(self):
        self.storeHistory("Initial History Stamp")
    def addHistoryModifiedListener(self, callback:'function'):
        self._history_modified_listeners.append(callback)
    def addHistoryStoredListener(self, callback:'function'):
        self._history_stored_listeners.append(callback)
    def addHistoryRestoredListener(self, callback:'function'):
        self._history_restored_listeners.append(callback)
    def canUndo(self) -> bool:
        return self.history_current_step > 0
    def canRedo(self) -> bool:
        return self.history_current_step + 1 < len(self.history_stack)
    def undo(self):
        if DEBUG: print("UNDO")
        if self.canUndo():
            self.history_current_step -= 1
            self.restoreHistory()
            self.scene.has_been_modified = True
    def redo(self):
        if DEBUG: print("REDO")
        if self.canRedo():
            self.history_current_step += 1
            self.restoreHistory()
            self.scene.has_been_modified = True
    def restoreHistory(self):
        if DEBUG: print("Restoring history",
                        ".... current_step: @%d" % self.history_current_step,
                        "(%d)" % len(self.history_stack))
        self.restoreHistoryStamp(self.history_stack[self.history_current_step])
        for callback in self._history_modified_listeners: callback()
        for callback in self._history_restored_listeners: callback()
    def storeHistory(self, desc:str, setModified:bool=False):
        if setModified:
            self.scene.has_been_modified = True
        if DEBUG: print("Storing history", '"%s"' % desc,
                        ".... current_step: @%d" % self.history_current_step,
                        "(%d)" % len(self.history_stack))
        if self.history_current_step+1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_current_step+1]
        if self.history_current_step+1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1
        hs = self.createHistoryStamp(desc)
        self.history_stack.append(hs)
        self.history_current_step += 1
        if DEBUG: print("  -- setting step to:", self.history_current_step)
        for callback in self._history_modified_listeners: callback()
        for callback in self._history_stored_listeners: callback()
    def captureCurrentSelection(self) -> dict:
        sel_obj = {
            'nodes': [],
            'edges': [],
        }
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'): sel_obj['nodes'].append(item.node.id)
            elif hasattr(item, 'edge'): sel_obj['edges'].append(item.edge.id)
        return sel_obj
    def createHistoryStamp(self, desc:str) -> dict:
        history_stamp = {
            'desc': desc,
            'snapshot': self.scene.serialize(),
            'selection': self.captureCurrentSelection(),
        }
        return history_stamp
    def restoreHistoryStamp(self, history_stamp:dict):
        if DEBUG: print("RHS: ", history_stamp['desc'])
        try:
            self.undo_selection_has_changed = False
            previous_selection = self.captureCurrentSelection()
            if DEBUG_SELECTION: print("selected nodes before restore:", previous_selection['nodes'])
            self.scene.deserialize(history_stamp['snapshot'])
            for edge in self.scene.edges: edge.grEdge.setSelected(False)
            for edge_id in history_stamp['selection']['edges']:
                for edge in self.scene.edges:
                    if edge.id == edge_id:
                        edge.grEdge.setSelected(True)
                        break
            for node in self.scene.nodes: node.grNode.setSelected(False)
            for node_id in history_stamp['selection']['nodes']:
                for node in self.scene.nodes:
                    if node.id == node_id:
                        node.grNode.setSelected(True)
                        break
            current_selection = self.captureCurrentSelection()
            if DEBUG_SELECTION: print("selected nodes after restore:", current_selection['nodes'])
            if current_selection['nodes'] != previous_selection['nodes'] or current_selection['edges'] != previous_selection['edges']:
                if DEBUG_SELECTION: print("\nSCENE: Selection has changed")
                self.undo_selection_has_changed = True
        except Exception as e: dumpException(e)
