# -*- coding: utf-8 -*-
from node_graphics_node import QDMGraphicsNode
from node_content_widget import QDMNodeContentWidget
from node_socket import *
from utils import dumpException, pp
DEBUG = False
class Node(Serializable):
    GraphicsNode_class = QDMGraphicsNode
    NodeContent_class = QDMNodeContentWidget
    Socket_class = Socket
    def __init__(self, scene:'Scene', title:str="Undefined Node", inputs:list=[], outputs:list=[]):
        super().__init__()
        self._title = title
        self.scene = scene
        self.content = None
        self.grNode = None
        self.initInnerClasses()
        self.initSettings()
        self.title = title
        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)
        self.inputs = []
        self.outputs = []
        self.initSockets(inputs, outputs)
        self._is_dirty = False
        self._is_invalid = False
    def __str__(self):
        return "<%s:%s %s..%s>" % (self.title, self.__class__.__name__,hex(id(self))[2:5], hex(id(self))[-3:])
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title
    @property
    def pos(self):
        return self.grNode.pos()        
    def setPos(self, x:float, y:float):
        self.grNode.setPos(x, y)
    def initInnerClasses(self):
        node_content_class = self.getNodeContentClass()
        graphics_node_class = self.getGraphicsNodeClass()
        if node_content_class is not None: self.content = node_content_class(self)
        if graphics_node_class is not None: self.grNode = graphics_node_class(self)
    def getNodeContentClass(self):
        return self.__class__.NodeContent_class
    def getGraphicsNodeClass(self):
        return self.__class__.GraphicsNode_class
    def initSettings(self):
        self.socket_spacing = 22
        self.input_socket_position = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.input_multi_edged = False
        self.output_multi_edged = True
        self.socket_offsets = {
            LEFT_BOTTOM: -1,
            LEFT_CENTER: -1,
            LEFT_TOP: -1,
            RIGHT_BOTTOM: 1,
            RIGHT_CENTER: 1,
            RIGHT_TOP: 1,
        }
    def initSockets(self, inputs:list, outputs:list, reset:bool=True):
        if reset:
            if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
                for socket in (self.inputs+self.outputs):
                    self.scene.grScene.removeItem(socket.grSocket)
                self.inputs = []
                self.outputs = []
        counter = 0
        for item in inputs:
            socket = self.__class__.Socket_class(
                node=self, index=counter, position=self.input_socket_position,
                socket_type=item, multi_edges=self.input_multi_edged,
                count_on_this_node_side=len(inputs), is_input=True
            )
            counter += 1
            self.inputs.append(socket)
        counter = 0
        for item in outputs:
            socket = self.__class__.Socket_class(
                node=self, index=counter, position=self.output_socket_position,
                socket_type=item, multi_edges=self.output_multi_edged,
                count_on_this_node_side=len(outputs), is_input=False
            )
            counter += 1
            self.outputs.append(socket)
    def onEdgeConnectionChanged(self, new_edge:'Edge'):
        pass
    def onInputChanged(self, socket:'Socket'):
        self.markDirty()
        self.markDescendantsDirty()
    def onDeserialized(self, data:dict):
        pass
    def onDoubleClicked(self, event):
        pass
    def doSelect(self, new_state:bool=True):
        self.grNode.doSelect(new_state)
    def isSelected(self):
        return self.grNode.isSelected()
    def getSocketPosition(self, index:int, position:int, num_out_of:int=1) -> '(x, y)':
        x = self.socket_offsets[position] if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM)) else self.grNode.width + self.socket_offsets[position]
        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = self.grNode.height - self.grNode.edge_roundness - self.grNode.title_vertical_padding - index * self.socket_spacing
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            num_sockets = num_out_of
            node_height = self.grNode.height
            top_offset = self.grNode.title_height + 2 * self.grNode.title_vertical_padding + self.grNode.edge_padding
            available_height = node_height - top_offset
            total_height_of_all_sockets = num_sockets * self.socket_spacing
            new_top = available_height - total_height_of_all_sockets
            y = top_offset + available_height/2.0 + (index-0.5)*self.socket_spacing
            if num_sockets > 1:
                y -= self.socket_spacing * (num_sockets-1)/2
        elif position in (LEFT_TOP, RIGHT_TOP):
            y = self.grNode.title_height + self.grNode.title_vertical_padding + self.grNode.edge_roundness + index * self.socket_spacing
        else:
            y = 0
        return [x, y]
    def getSocketScenePosition(self, socket:'Socket') -> '(x, y)':
        nodepos = self.grNode.pos()
        socketpos = self.getSocketPosition(socket.index, socket.position, socket.count_on_this_node_side)
        return (nodepos.x() + socketpos[0], nodepos.y() + socketpos[1])
    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            for edge in socket.edges:
                edge.updatePositions()
    def remove(self):
        if DEBUG: print("> Removing Node", self)
        if DEBUG: print(" - remove all edges from sockets")
        for socket in (self.inputs+self.outputs):
            for edge in socket.edges:
                if DEBUG: print("    - removing from socket:", socket, "edge:", edge)
                edge.remove()
        if DEBUG: print(" - remove grNode")
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG: print(" - remove node from the scene")
        self.scene.removeNode(self)
        if DEBUG: print(" - everything was done.")
    def isDirty(self) -> bool:
        return self._is_dirty
    def markDirty(self, new_value:bool=True):
        self._is_dirty = new_value
        if self._is_dirty: self.onMarkedDirty()
    def onMarkedDirty(self):
        pass
    def markChildrenDirty(self, new_value:bool=True):
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
    def markDescendantsDirty(self, new_value:bool=True):
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markChildrenDirty(new_value)
    def isInvalid(self) -> bool:
        return self._is_invalid
    def markInvalid(self, new_value:bool=True):
        self._is_invalid = new_value
        if self._is_invalid: self.onMarkedInvalid()
    def onMarkedInvalid(self):
        pass
    def markChildrenInvalid(self, new_value:bool=True):
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
    def markDescendantsInvalid(self, new_value:bool=True):
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
            other_node.markChildrenInvalid(new_value)
    def eval(self, index=0):
        self.markDirty(False)
        self.markInvalid(False)
        return 0
    def evalChildren(self):
        for node in self.getChildrenNodes():
            node.eval()
    def getChildrenNodes(self) -> 'List[Node]':
        if self.outputs == []: return []
        other_nodes = []
        for ix in range(len(self.outputs)):
            for edge in self.outputs[ix].edges:
                other_node = edge.getOtherSocket(self.outputs[ix]).node
                other_nodes.append(other_node)
        return other_nodes
    def getInput(self, index:int=0) -> ['Node', None]:
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0: return None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node
        except Exception as e:
            dumpException(e)
            return None
    def getOutput(self, index: int = 0) -> ['Node', None]:
        try:
            output_socket = self.outputs[index]
            if len(output_socket.edges) == 0: return None
            connecting_edge = output_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.outputs[index])
            return other_socket.node
        except Exception as e:
            dumpException(e)
            return None
    def getInputWithSocket(self, index:int=0) -> [('Node', 'Socket'), (None, None)]:
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0: return None, None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node, other_socket
        except Exception as e:
            dumpException(e)
            return None, None
    def getInputWithSocketIndex(self, index:int=0) -> ('Node', int):
        try:
            edge = self.inputs[index].edges[0]
            socket = edge.getOtherSocket(self.inputs[index])
            return socket.node, socket.index
        except IndexError:
            return None, None
        except Exception as e:
            dumpException(e)
            return None, None
    def getInputs(self, index:int=0) -> 'List[Node]':
        ins = []
        for edge in self.inputs[index].edges:
            other_socket = edge.getOtherSocket(self.inputs[index])
            ins.append(other_socket.node)
        return ins
    def getOutputs(self, index:int=0) -> 'List[Node]':
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outs.append(other_socket.node)
        return outs
    def serialize(self) -> OrderedDict:
        inputs, outputs = [], []
        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())
        ser_content = self.content.serialize() if isinstance(self.content, Serializable) else {}
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', ser_content),
        ])
    def deserialize(self, data:dict, hashmap:dict={}, restore_id:bool=True) -> bool:
        try:
            if restore_id: self.id = data['id']
            hashmap[data['id']] = self
            self.setPos(data['pos_x'], data['pos_y'])
            self.title = data['title']
            data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000 )
            data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000 )
            num_inputs = len( data['inputs'] )
            num_outputs = len( data['outputs'] )
            for socket_data in data['inputs']:
                found = None
                for socket in self.inputs:
                    if socket.index == socket_data['index']:
                        found = socket
                        break
                if found is None:
                    found = self.__class__.Socket_class(
                        node=self, index=socket_data['index'], position=socket_data['position'],
                        socket_type=socket_data['socket_type'], count_on_this_node_side=num_inputs,
                        is_input=True
                    )
                    self.inputs.append(found)  
                found.deserialize(socket_data, hashmap, restore_id)
            for socket_data in data['outputs']:
                found = None
                for socket in self.outputs:
                    if socket.index == socket_data['index']:
                        found = socket
                        break
                if found is None:
                    found = self.__class__.Socket_class(
                        node=self, index=socket_data['index'], position=socket_data['position'],
                        socket_type=socket_data['socket_type'], count_on_this_node_side=num_outputs,
                        is_input=False
                    )
                    self.outputs.append(found)  
                found.deserialize(socket_data, hashmap, restore_id)
        except Exception as e: dumpException(e)
        if isinstance(self.content, Serializable):
            res = self.content.deserialize(data['content'], hashmap)
            return res
        return True
