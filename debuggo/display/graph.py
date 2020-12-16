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
        if not len(model):
            return "\u2205"
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

    def draw_rule_labels(self, G, pos,
                         edge_labels=None,
                         label_pos=0.5,
                         font_size=10,
                         font_color='k',
                         font_family='sans-serif',
                         font_weight='normal',
                         alpha=1.0,
                         bbox=None,
                         ax=None,
                         rotate=True,
                         **kwds):
        try:
            import matplotlib.pyplot as plt
            import matplotlib.cbook as cb
            import numpy
        except ImportError:
            raise ImportError("Matplotlib required for draw()")
        except RuntimeError:
            print("Matplotlib unable to open display")
            raise

        if ax is None:
            ax = plt.gca()
        if edge_labels is None:
            labels = dict(((u, v), d) for u, v, d in G.edges(data=True))
        else:
            labels = edge_labels
        text_items = {}

        max_x = -math.inf
        min_x = +math.inf
        for x, _ in pos.values():
            max_x = max(max_x, x)
            min_x = min(min_x, x)
        center_x = (max_x + min_x) / 2
        print(f"Center x: {center_x}")

        for (n1, n2), label in labels.items():
            (x1, y1) = pos[n1]
            (x2, y2) = pos[n2]
            (x, y) = (center_x,
                      y1 * label_pos + y2 * (1.0 - label_pos))


            if rotate:
                angle = numpy.arctan2(y2 - y1, x2 - x1) / (2.0 * numpy.pi) * 360  # degrees
                # make label orientation "right-side-up"
                if angle > 90:
                    angle -= 180
                if angle < - 90:
                    angle += 180
                # transform data coordinate angle to screen coordinate angle
                xy = numpy.array((x, y))
                trans_angle = ax.transData.transform_angles(numpy.array((angle,)),
                                                            xy.reshape((1, 2)))[0]
            else:
                trans_angle = 0.0
            # use default box of white with white border
            if bbox is None:
                bbox = dict(boxstyle='round',
                            ec=(1.0, 1.0, 1.0),
                            fc=(1.0, 1.0, 1.0),
                            )

            # set optional alignment
            horizontalalignment = kwds.get('horizontalalignment', 'center')
            verticalalignment = kwds.get('verticalalignment', 'center')

            t = ax.text(x, y,
                        label,
                        size=font_size,
                        color=font_color,
                        family=font_family,
                        weight=font_weight,
                        horizontalalignment=horizontalalignment,
                        verticalalignment=verticalalignment,
                        rotation=trans_angle,
                        transform=ax.transData,
                        bbox=bbox,
                        zorder=1,
                        clip_on=True,
                        )
            text_items[(n1, n2)] = t

        return text_items

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

        self.draw_rule_labels(self._ng, pos,
                              label_pos=.5,
                              rotate=False,
                              font_size=7,
                              font_family="monospace",
                              bbox={'facecolor' : 'White',
                                           'edgecolor' : 'Red',
                                           'boxstyle':'round'},
                              edge_labels=recursive_labels)
        self.draw_rule_labels(self._ng, pos,
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

