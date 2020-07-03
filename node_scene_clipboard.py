# -*- coding: utf-8 -*-
from collections import OrderedDict
from node_graphics_edge import QDMGraphicsEdge
from node_edge import Edge
DEBUG = False
DEBUG_PASTING = False
class SceneClipboard():
    def __init__(self, scene:'Scene'):
        self.scene = scene
    def serializeSelected(self, delete:bool=False) -> OrderedDict:
        if DEBUG: print("-- COPY TO CLIPBOARD ---")
        sel_nodes, sel_edges, sel_sockets = [], [], {}
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())
                for socket in (item.node.inputs + item.node.outputs):
                    sel_sockets[socket.id] = socket
            elif isinstance(item, QDMGraphicsEdge):
                sel_edges.append(item.edge)
        if DEBUG:
            print("  NODES\n      ", sel_nodes)
            print("  EDGES\n      ", sel_edges)
            print("  SOCKETS\n     ", sel_sockets)
        edges_to_remove = []
        for edge in sel_edges:
            if edge.start_socket.id in sel_sockets and edge.end_socket.id in sel_sockets:
                pass
            else:
                if DEBUG: print("edge", edge, "is not connected with both sides")
                edges_to_remove.append(edge)
        for edge in edges_to_remove:
            sel_edges.remove(edge)
        edges_final = []
        for edge in sel_edges:
            edges_final.append(edge.serialize())
        if DEBUG: print("our final edge list:", edges_final)
        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edges_final),
        ])
        if delete:
            self.scene.getView().deleteSelected()
            self.scene.history.storeHistory("Cut out elements from scene", setModified=True)
        return data
    def deserializeFromClipboard(self, data:dict):
        hashmap = {}
        view = self.scene.getView()
        mouse_scene_pos = view.last_scene_mouse_position
        minx, maxx, miny, maxy = 10000000,-10000000, 10000000,-10000000
        for node_data in data['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
        maxx -= 180
        maxy += 100
        relbboxcenterx = (minx + maxx) / 2 - minx
        relbboxcentery = (miny + maxy) / 2 - miny
        if DEBUG_PASTING:
            print (" *** PASTA:")
            print("Copied boudaries:\n\tX:", minx, maxx, "   Y:", miny, maxy)
            print("\tbbox_center:", relbboxcenterx, relbboxcentery)
        mousex, mousey = mouse_scene_pos.x(), mouse_scene_pos.y()
        created_nodes = []
        self.scene.setSilentSelectionEvents()
        self.scene.doDeselectItems()
        for node_data in data['nodes']:
            new_node = self.scene.getNodeClassFromData(node_data)(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False)
            created_nodes.append(new_node)
            posx, posy = new_node.pos.x(), new_node.pos.y()
            newx, newy = mousex + posx - minx, mousey + posy - miny
            new_node.setPos(newx, newy)
            new_node.doSelect()
            if DEBUG_PASTING:
                print("** PASTA SUM:")
                print("\tMouse pos:", mousex, mousey)
                print("\tnew node pos:", posx, posy)
                print("\tFINAL:", newx, newy)
        if 'edges' in data:
            for edge_data in data['edges']:
                new_edge = Edge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)
        self.scene.setSilentSelectionEvents(False)
        self.scene.history.storeHistory("Pasted elements in scene", setModified=True)
        return created_nodes
