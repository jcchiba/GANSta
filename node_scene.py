# -*- coding: utf-8 -*-
import os
import json
from collections import OrderedDict
from utils import dumpException
from node_serializable import Serializable
from node_graphics_scene import QDMGraphicsScene
from node_node import Node
from node_edge import Edge
from node_scene_history import SceneHistory
from node_scene_clipboard import SceneClipboard
from utils import pp
DEBUG_REMOVE_WARNINGS = False
class InvalidFile(Exception):
    passcERLyShwxaliHRjDdhvnRhPHrnpwMWeeOPnGmATFYERFFsqQRwfFNoZUMjchUcGk = 'xhuXTyjrfRvrDREbHcfttoWUBvpfOpPHeXJmkZPWduvEqpYMoKQosrQyLHxmvRCl'
class Scene(Serializable):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []
        self.scene_width = 64000
        self.scene_height = 64000
        self._silent_selection_events = False
        self._has_been_modified = False
        self._last_selected_items = []
        self._has_been_modified_listeners = []
        self._item_selected_listeners = []
        self._items_deselected_listeners = []
        self.node_class_selector = None
        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)
        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)
    @property
    def has_been_modified(self):
        return self._has_been_modified
    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            self._has_been_modified = value
            for callback in self._has_been_modified_listeners: callback()
        self._has_been_modified = value
    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)
    def setSilentSelectionEvents(self, value:bool=True):
        self._silent_selection_events = value
    def onItemSelected(self, silent:bool=False):
        if self._silent_selection_events: return
        current_selected_items = self.getSelectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            if not silent:
                for callback in self._item_selected_listeners: callback()
                self.history.storeHistory("Selection Changed")
    def onItemsDeselected(self, silent:bool=False):
        self.resetLastSelectedStates()
        if self._last_selected_items != []:
            self._last_selected_items = []
            if not silent:
                self.history.storeHistory("Deselected Everything")
                for callback in self._items_deselected_listeners: callback()
    def isModified(self) -> bool:
        return self.has_been_modified
    def getSelectedItems(self) -> list:
        return self.grScene.selectedItems()
    def doDeselectItems(self, silent:bool=False) -> None:
        for item in self.getSelectedItems():
            item.setSelected(False)
        if not silent:
            self.onItemsDeselected()
    def addHasBeenModifiedListener(self, callback:'function'):
        self._has_been_modified_listeners.append(callback)
    def addItemSelectedListener(self, callback:'function'):
        self._item_selected_listeners.append(callback)
    def addItemsDeselectedListener(self, callback:'function'):
        self._items_deselected_listeners.append(callback)
    def addDragEnterListener(self, callback:'function'):
        self.getView().addDragEnterListener(callback)
    def addDropListener(self, callback:'function'):
        self.getView().addDropListener(callback)
    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._last_selected_state = False
    def getView(self) -> 'QGraphicsView':
        return self.grScene.views()[0]
    def getItemAt(self, pos:'QPointF'):
        return self.getView().itemAt(pos)
    def addNode(self, node:Node):
        self.nodes.append(node)
    def addEdge(self, edge:Edge):
        self.edges.append(edge)
    def removeNode(self, node:Node):
        if node in self.nodes: self.nodes.remove(node)
        else:
            if DEBUG_REMOVE_WARNINGS: print("!W:", "Scene::removeNode", "wanna remove nodeeditor", node,
                                            "from self.nodes but it's not in the list!")
    def removeEdge(self, edge:Edge):
        if edge in self.edges: self.edges.remove(edge)
        else:
            if DEBUG_REMOVE_WARNINGS: print("!W:", "Scene::removeEdge", "wanna remove edge", edge,
                                            "from self.edges but it's not in the list!")
    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()
        self.has_been_modified = False
    def saveToFile(self, filename:str):
        with open(filename, "w") as file:
            file.write( json.dumps( self.serialize(), indent=4 ) )
            print("saving to", filename, "was successfull.")
            self.has_been_modified = False
    def loadFromFile(self, filename:str):
        with open(filename, "r") as file:
            raw_data = file.read()
            try:
                data = json.loads(raw_data, encoding='utf-8')
                self.deserialize(data)
                self.has_been_modified = False
            except json.JSONDecodeError:
                raise InvalidFile("%s is not a valid JSON file" % os.path.basename(filename))
            except Exception as e:
                dumpException(e)
    def setNodeClassSelector(self, class_selecting_function:'functon') -> 'Node class type':
        self.node_class_selector = class_selecting_function
    def getNodeClassFromData(self, data:dict) -> 'Node class instance':
        return Node if self.node_class_selector is None else self.node_class_selector(data)
    def serialize(self) -> OrderedDict:
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges),
        ])
    def deserialize(self, data:dict, hashmap:dict={}, restore_id:bool=True) -> bool:
        hashmap = {}
        if restore_id: self.id = data['id']
        all_nodes = self.nodes.copy()
        for node_data in data['nodes']:
            found = False
            for node in all_nodes:
                if node.id == node_data['id']:
                    found = node
                    break
            if not found:
                new_node = self.getNodeClassFromData(node_data)(self)
                new_node.deserialize(node_data, hashmap, restore_id)
                new_node.onDeserialized(node_data)
            else:
                found.deserialize(node_data, hashmap, restore_id)
                found.onDeserialized(node_data)
                all_nodes.remove(found)
        while all_nodes != []:
            node = all_nodes.pop()
            node.remove()
        all_edges = self.edges.copy()
        for edge_data in data['edges']:
            found = False
            for edge in all_edges:
                if edge.id == edge_data['id']:
                    found = edge
                    break
            if not found:
                new_edge = Edge(self).deserialize(edge_data, hashmap, restore_id)
            else:
                found.deserialize(edge_data, hashmap, restore_id)
                all_edges.remove(found)
        while all_edges != []:
            edge = all_edges.pop()
            edge.remove()
        return True
