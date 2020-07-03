# -*- coding: utf-8 -*-
from collections import OrderedDict
from node_graphics_edge import *
from node_serializable import Serializable
from utils import dumpException
EDGE_TYPE_DIRECT = 1        
EDGE_TYPE_BEZIER = 2        
DEBUG = False
class Edge(Serializable):
    def __init__(self, scene:'Scene', start_socket:'Socket'=None, end_socket:'Socket'=None, edge_type=EDGE_TYPE_DIRECT):
        super().__init__()
        self.scene = scene
        self._start_socket = None
        self._end_socket = None
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type
        self.scene.addEdge(self)
    def __str__(self):
        return "<Edge %s..%s -- S:%s E:%s>" % (
            hex(id(self))[2:5], hex(id(self))[-3:],
            self.start_socket, self.end_socket
        )
    @property
    def start_socket(self):
        return self._start_socket
    @start_socket.setter
    def start_socket(self, value):
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)
        self._start_socket = value
        if self.start_socket is not None:
            self.start_socket.addEdge(self)
    @property
    def end_socket(self):
        return self._end_socket
    @end_socket.setter
    def end_socket(self, value):
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)
        self._end_socket= value
        if self.end_socket is not None:
            self.end_socket.addEdge(self)
    @property
    def edge_type(self):
        return self._edge_type
    @edge_type.setter
    def edge_type(self, value):
        if hasattr(self, 'grEdge') and self.grEdge is not None:
            self.scene.grScene.removeItem(self.grEdge)
        self._edge_type = value
        edgeClass = self.determineEdgeClass(self.edge_type)
        self.grEdge = edgeClass(self)
        self.scene.grScene.addItem(self.grEdge)
        if self.start_socket is not None:
            self.updatePositions()
    def determineEdgeClass(self, edge_type:int):
        edge_class = QDMGraphicsEdgeBezier
        if edge_type == EDGE_TYPE_DIRECT:
            edge_class = QDMGraphicsEdgeDirect
        return edge_class
    def getOtherSocket(self, known_socket:'Socket'):
        return self.start_socket if known_socket == self.end_socket else self.end_socket
    def doSelect(self, new_state:bool=True):
        self.grEdge.doSelect(new_state)
    def updatePositions(self):
        source_pos = self.start_socket.getSocketPosition()
        source_pos[0] += self.start_socket.node.grNode.pos().x()
        source_pos[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*source_pos)
        if self.end_socket is not None:
            end_pos = self.end_socket.getSocketPosition()
            end_pos[0] += self.end_socket.node.grNode.pos().x()
            end_pos[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDestination(*end_pos)
        else:
            self.grEdge.setDestination(*source_pos)
        self.grEdge.update()
    def remove_from_sockets(self):
        self.end_socket = None
        self.start_socket = None
    def remove(self, silent_for_socket:'Socket'=None, silent=False):
        old_sockets = [self.start_socket, self.end_socket]
        if DEBUG: print(" - hide grEdge")
        self.grEdge.hide()
        if DEBUG: print(" - remove grEdge", self.grEdge)
        self.scene.grScene.removeItem(self.grEdge)
        if DEBUG: print("   grEdge:", self.grEdge)
        self.scene.grScene.update()
        if DEBUG: print("# Removing Edge", self)
        if DEBUG: print(" - remove edge from all sockets")
        self.remove_from_sockets()
        if DEBUG: print(" - remove edge from scene")
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass
        if DEBUG: print(" - everything is done.")
        try:
            for socket in old_sockets:
                if socket and socket.node:
                    if silent:
                        continue
                    if silent_for_socket is not None and socket == silent_for_socket:
                        continue
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.is_input: socket.node.onInputChanged(socket)
        except Exception as e: dumpException(e)
    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id if self.start_socket is not None else None),
            ('end', self.end_socket.id if self.end_socket is not None else None),
        ])
    def deserialize(self, data:dict, hashmap:dict={}, restore_id:bool=True) -> bool:
        if restore_id: self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']
