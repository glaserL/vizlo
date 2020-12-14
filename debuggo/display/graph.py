import math
import os
from typing import Tuple

import igraph
import networkx as nx


EDGE_ALPHA = 0.8

class NetworkxDisplay():

    def __init__(self, graph):
        self._ng : nx.DiGraph = graph
        self._ig : igraph.Graph = self.nxgraph_to_igraph(graph)

    def model_to_string(self, model):
        result_str = ""
        how_many_per_line = math.sqrt(len(model))
        tmp = []
        for m in model:
            print(f"Consuming {str(m)}, current_state = {tmp}")
            if len(tmp) >= how_many_per_line:
                result_str += " ".join(tmp)+"\n"
                tmp.clear()
            tmp.append(str(m))
        result_str += " ".join(tmp)
        return f"{result_str}"

    def split_into_edge_lists(self, g : nx.Graph) -> Tuple:
        constraints = []
        normal = []
        for edge in self._ng.edges(data=True):
            if "#false" in edge[2]["rule"]:
                constraints.append(edge)
            else:
                normal.append(edge)
        return normal, constraints

    def draw(self):
        # nx.draw(self._ng)
        print(f"Drawing graph with {len(self._ng)} nodes.")
        print(self._ig)
        node_size = 1000
        layout = self._ig.layout_reingold_tilford(root=[0])
        layout.rotate(180)
        # igraph.plot(self._ig, layout=layout)
        nx_map = {i: node for i, node in enumerate(self._ng.nodes())}
        pos = self.igraph_to_networkx_layout(layout, nx_map)

        for node in self._ng:
            print(f"{node.model} ({type(node)})")

        # pos = layouting_func(self._ng,
        #                      scale=100,
        #                      #subset_key="model"
        #                      )

        nx.draw_networkx_nodes(self._ng, pos,
                               # node_color=node_color,
                               alpha=0.9,
                               node_size=node_size,
                               # cmap=plt.get_cmap(colormap))
                               )

        normal_edge_list, constraint_edge_list = self.split_into_edge_lists(self._ng)

        nx.draw_networkx_edges(self._ng, pos,
                               edgelist=normal_edge_list,
                               alpha=EDGE_ALPHA,
                               node_size=node_size)

        nx.draw_networkx_edges(self._ng, pos,
                               edgelist=constraint_edge_list,
                               alpha=EDGE_ALPHA,
                               style="dashed",
                               node_size=node_size)



        node_labels = {}
        edge_labels = {}
        recursive_labels = {}
        rec_edge_c = 0
        for node, nbrsdict in self._ng.adjacency():
            node_labels[node] = self.model_to_string(node.model)
            for neighbor, edge_attrs in nbrsdict.items():
                if str(edge_attrs["rule"]).count(":-") > 1:
                    rec_label = self.make_rec_label(edge_attrs['rule'])
                    recursive_labels[(node, neighbor)] = f"[{rec_edge_c}] {rec_label}"
                    rec_edge_c += 1
                else:
                    edge_labels[(node, neighbor)] = edge_attrs["rule"]

        nx.draw_networkx_labels(self._ng, pos,
                                font_size=8,
                                labels=node_labels)

        nx.draw_networkx_edge_labels(self._ng, pos,
                                     label_pos=.5,
                                     rotate=False,
                                     font_size=7,
                                     font_family="monospace",
                                     bbox={'facecolor' : 'White',
                                           'edgecolor' : 'Red',
                                           'boxstyle':'round'},
                                     edge_labels=recursive_labels)
        nx.draw_networkx_edge_labels(self._ng, pos,
                                     label_pos=.5,
                                     rotate=False,
                                     font_size=7,
                                     font_family="monospace",
                                     bbox={'facecolor' : 'White',
                                           'edgecolor' : 'Black',
                                           'boxstyle':'round'},
                                     edge_labels=edge_labels)

    @staticmethod
    def _inject_for_drawing(g):
        for v, dat in g.nodes(data=True):
            dat["step"] = v.rule
            print(dat)
        # pos = graphviz_layout(self._g, prog="twopi")
        # nx.draw(self._g, pos)
        # plt.show()
    @staticmethod
    def igraph_to_networkx_layout(i_layout, nx_map):
        nx_layout = {}
        for i, pos in enumerate(i_layout.coords):
            nx_layout[nx_map[i]] = pos
        return nx_layout

    @staticmethod
    def nxgraph_to_igraph(nxgraph):
        return igraph.Graph.Adjacency((nx.to_numpy_matrix(nxgraph) > 0).tolist())

    def make_rec_label(self, param):
        return "\n".join(param)

