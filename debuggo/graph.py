import math
import sys
from copy import copy
from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import defaultdict
import igraph
import networkx as nx

from debuggo.solver import INITIAL_EMPTY_SET

EDGE_ALPHA = 0.3


#########################
def make_node_label_positions(
        G,
        pos,
        labels=None,
        font_size=12,
        font_color="k",
        font_family="sans-serif",
        font_weight="normal",
        alpha=None,
        bbox=None,
        horizontalalignment="center",
        verticalalignment="center",
        ax=None,
):
    if ax is None:
        ax = plt.gca()

    text_items = {}  # there is no text collection so we'll fake one
    for n, label in labels.items():
        (x, y) = pos[n]
        if not isinstance(label, str):
            label = str(label)  # this makes "1" and 1 labeled the same
        t = ax.text(
            x,
            y,
            label,
            size=font_size,
            color=font_color,
            family=font_family,
            weight=font_weight,
            alpha=alpha,
            horizontalalignment=horizontalalignment,
            verticalalignment=verticalalignment,
            transform=ax.transData,
            bbox=bbox,
            clip_on=True,
        )
        text_items[n] = t

    ax.tick_params(
        axis="both",
        which="both",
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False,
    )

    return text_items


def changes_only(graph: nx.DiGraph) -> nx.DiGraph():
    display_graph = nx.DiGraph()
    display_graph.add_node(INITIAL_EMPTY_SET)
    for u, v in nx.bfs_edges(graph, INITIAL_EMPTY_SET):
        new_v = copy(v)
        new_v.model = v.model - u.model
        print(f"{u} ({u in display_graph}) -> {new_v} ({new_v in display_graph}) ((old: {v}))")
        display_graph.add_edge(u, new_v, rule=graph[u][v]["rule"])
    print(f"{len(display_graph)}, {len(graph)}")
    # assert len(display_graph) == len(graph)
    return display_graph


def assert_no_bi_edges(g: nx.Graph):
    assert len(g.nodes) == len(g.edges) - 1


def model_to_string(model):
    if not len(model):
        return "\u2205"
    result_str = ""
    how_many_per_line = math.sqrt(len(model))
    tmp = []
    for m in model:
        print(f"Consuming {str(m)}, current_state = {tmp}")
        if len(tmp) >= how_many_per_line:
            result_str += " ".join(tmp) + "\n"
            tmp.clear()
        tmp.append(str(m))
    result_str += " ".join(tmp)
    return f"{result_str}"


def get_width_and_height_of_text_label(text_label):
    t = mpl.textpath.TextPath((0, 0), text_label, size=8)
    bb = t.get_extents()
    width = max(bb.x0, bb.x1) - min(bb.x0, bb.x1)
    height = max(bb.y0, bb.y1) - min(bb.y0, bb.y1)
    return width, height


def make_node_labels(g):
    node2label = {}
    for node in g:
        label = model_to_string(node.model)
        node2label[node] = label
    return node2label


def adjust_figure_size(pos, node_labels):
    row_set = set()
    tricky_map = defaultdict(list)
    max_width = -1
    max_height = -1
    for node, label in node_labels.items():
        x, y = pos[node]
        round_x = round(x)
        round_y = round(y)
        row_set.add(round_x)
        tricky_map[round_y].append(round_x)
        width, height = get_width_and_height_of_text_label(label)
        max_width, max_height = max(width, max_width), max(height, max_height)
    rows = len(row_set)
    sys.stderr.write(f"w: {max_width}, h: {max_height}")
    cols = max([len(lst) for lst in tricky_map.values()])
    #return cols*max_width/150, max_height*rows*1.5/10
    return cols*max_width/2, max_height*rows*1.5/5



class NetworkxDisplay():

    def __init__(self, graph, print_changes_only=True, merge_nodes=True):
        if merge_nodes:
            self._ng = self.merge_nodes_on_same_step(graph)
        else:
            self._ng = graph
        self._print_changes_only = print_changes_only
        self._ig: igraph.Graph = self.nxgraph_to_igraph(self._ng)
        print(f"Initialized {self.__class__}")

    def merge_nodes_on_same_step(self, g):
        mapping = {}
        for x in g.nodes():
            for y in g.nodes():
                if x.step == y.step and x.model == y.model:
                    mapping[x] = y
        return nx.relabel_nodes(g, mapping)

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

    def split_into_edge_lists(self, g: nx.Graph) -> Tuple:
        constraints = []
        normal = []
        for edge in self._ng.edges(data=True):
            if "#false" in edge[2]["rule"]:
                constraints.append(edge)
            else:
                normal.append(edge)
        return normal, constraints

    def make_text_label_sizes(self, node2label):
        result = []
        for node, label in node2label.keys():
            width, height = get_width_and_height_of_text_label(node)

    def draw(self):
        # 1. Figure out node positions using igraph
        print(f"Drawing graph with {len(self._ng)} nodes.")
        node_size, pos = self.make_node_positions()

        # {node : label}
        node_labels = make_node_labels(self._ng)
        print(node_labels)
        #nodes = self.make_nodes_around_node_labels(node_labels)

        figsize = adjust_figure_size(pos, node_labels)
        figsize = (4,5)
        sys.stderr.write(str(figsize))
        plt.figure(figsize=figsize)
        # draw the node cricles.
        #draw_nodes(self._ng, pos,
                   # node_color=node_color,
        #           alpha=0.9,
        #           node_size=node_size,
                   # cmap=plt.get_cmap(colormap))
        #           )
        # Draw edges into the positions
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
            node_labels[node] = model_to_string(node.model)
            for neighbor, edge_attrs in nbrsdict.items():
                if str(edge_attrs["rule"]).count(":-") > 1:
                    rec_label = self.make_rec_label(edge_attrs['rule'])
                    recursive_labels[(node, neighbor)] = f"[{rec_edge_c}] {rec_label}"
                    rec_edge_c += 1
                else:
                    edge_labels[(node, neighbor)] = edge_attrs["rule"]

        nx.draw_networkx_labels(self._ng, pos,
                                font_size=8,
                              bbox={'facecolor': 'dodgerblue',
                                    'edgecolor': 'deepskyblue',
                                    'boxstyle': 'Round4',
                                    'pad' : 1},
                                labels=node_labels)
        # Circle
        # DArrow
        # LArrow
        # RArrow
        # Round
        # Round4
        # Roundtooth
        # Sawtooth
        # Square
        self.draw_rule_labels(self._ng, pos,
                              label_pos=.5,
                              rotate=False,
                              font_size=7,
                              font_family="monospace",
                              bbox={'facecolor': 'White',
                                    'edgecolor': 'Red',
                                    'boxstyle': 'round'},
                              edge_labels=recursive_labels)
        self.draw_rule_labels(self._ng, pos,
                              label_pos=.5,
                              rotate=False,
                              font_size=10,
                              font_family="monospace",
                              bbox={'facecolor': 'White',
                                    'edgecolor': 'Black',
                                    'boxstyle': 'round'},
                              edge_labels=edge_labels)

    def make_node_positions(self):
        node_size = 1000
        layout = self._ig.layout_reingold_tilford(root=[0])
        layout.rotate(180)
        nx_map = {i: node for i, node in enumerate(self._ng.nodes())}
        pos = self.igraph_to_networkx_layout(layout, nx_map)
        return node_size, pos

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
        return "\n".join([str(e) for e in param])
