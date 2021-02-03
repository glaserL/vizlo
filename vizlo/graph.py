import math
import sys
from copy import copy
from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import defaultdict, Counter
import igraph
import networkx as nx
from matplotlib.textpath import TextPath

from vizlo.solver import INITIAL_EMPTY_SET, SolverState

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


def get_width_and_height_of_text_label(text_label, fig):
    t = plt.text(0.5, 0.5, text_label, size=10)
    r= fig.canvas.get_renderer()
    #renderer = r
    bb = t.get_window_extent(renderer=r).transformed(fig.dpi_scale_trans.inverted())
    width = bb.width
    height = bb.height

    width, height = bb.width, bb.height
    #bbox = fig.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    #t = TextPath((0, 0), text_label, size=10)
    # bb = t.get_extents()
    # del t
    # width = max(bb.x0, bb.x1) - min(bb.x0, bb.x1)
    # width = bb.width
    # height = max(bb.y0, bb.y1) - min(bb.y0, bb.y1)
    # height = bb.height
    return width, height


def adjust_figure_size(pos, plotted_nodes, fig):
    row_set = set()
    col_set = set()
    highest_in_row = {}
    widest_in_col = {}
    nodes_per_column = Counter()
    nodes_per_row = Counter()
    tricky_map = defaultdict(list)
    r= fig.canvas.get_renderer()
    max_width = -1
    max_height = -1
    for node, label in plotted_nodes.items():
        step = node.step
        x, y = pos[node]
        round_x = round(x)
        round_y = round(y)
        nodes_per_row[round_y] += 1
        nodes_per_column[round_x] += 1
        # row_set.add(round_y)
        # col_set.add(round_x)
        # tricky_map[round_y].append(round_x)
        #renderer = r
        label.update_bbox_position_size(r)
        bb = label.get_bbox_patch().get_bbox()
        bb = label.get_window_extent(renderer=r)
        bb = bb.inverse_transformed(fig.dpi_scale_trans)
        width = bb.width
        height = bb.height
        widest_in_col[round_x] = max(widest_in_col.get(round_x, -math.inf), width)
        highest_in_row[round_y] = max(highest_in_row.get(round_y, -math.inf), height)
        #max_width, max_height = max(width, max_width), max(height, max_height)
    #rows = len(row_set)
    #sys.stderr.write(f"w: {max_width}, h: {max_height}")
    # cols = max([len(lst) for lst in tricky_map.values()])
    #cols = len(col_set)
    height = 0
    for _, h in highest_in_row.items():
        height += h#*fig.dpi
    x = height
    # return cols*max_width/150, max_height*rows*1.5/10
    print(height)
    height = height
    fig.set_figheight(height, forward=True)


class NetworkxDisplay():

    def __init__(self, graph, atom_draw_maximum=20, print_changes_only=True, merge_nodes=True):
        if merge_nodes:
            self._ng = self.merge_nodes_on_same_step(graph)
        else:
            self._ng = graph
        self.atom_draw_maximum = atom_draw_maximum
        self._print_changes_only = print_changes_only
        self.max_depth = max(n.step for n in self._ng.nodes())
        self._ig: igraph.Graph = self.nxgraph_to_igraph(self._ng)
        print(f"Initialized {self.__class__}")

    def model_to_string(self, model):
        if self.atom_draw_maximum <= 0:
            return ""
        if not len(model):
            return "\u2205"
        result_str = ""
        how_many_per_line = math.sqrt(len(model))
        tmp = []
        for m in list(model)[:min(len(model), self.atom_draw_maximum)]:
            if len(tmp) >= how_many_per_line:
                result_str += " ".join(tmp) + "\n"
                tmp.clear()
            tmp.append(str(m))
        result_str += " ".join(tmp)
        return f"{result_str}"

    def solver_state_to_string(self, solver_state: SolverState) -> str:
        atoms_to_draw = solver_state.adds if self._print_changes_only and self.max_depth != solver_state.step else solver_state.model
        return self.model_to_string(atoms_to_draw)

    def merge_nodes_on_same_step(self, g):
        mapping = {}
        for x in g.nodes():
            for y in g.nodes():
                if x.step == y.step and x.model == y.model and x.is_still_active == y.is_still_active:
                    mapping[x] = y
        return nx.relabel_nodes(g, mapping)

    def make_node_labels(self, g):
        node2label = {}
        for node in g:
            label = self.solver_state_to_string(node)
            node2label[node] = label
        return node2label

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
        if ax is None:
            ax = plt.gca()
        if edge_labels is None:
            labels = dict(((u, v), d) for u, v, d in G.edges(data=True))
        else:
            labels = edge_labels
        text_items = {}
        for (n1, n2), label in labels.items():
            (_, y2) = pos[n2]
            x = 1
            y = y2

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
            if "#false" in str(edge[2]["rule"]):
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
        node_size = 300

        node_labels = self.make_node_labels(self._ng)
        print(node_labels)

        pos = {node: (x, y) for node, (x, y) in pos.items()}
        #fig, (ax1, ax2) = plt.subplots(1, 2, dpi=100,constrained_layout=True)
        figsize = (4,6)
        fig = plt.figure(dpi= 100, figsize=figsize, constrained_layout=True)
        specs = fig.add_gridspec(ncols=2, nrows=1, width_ratios=[1,2])
        ax1 = fig.add_subplot(specs[0, 0])
        ax2 = fig.add_subplot(specs[0, 1])
        ax2.autoscale(enable=True)
        #fig.set_size_inches(11, 8)
#                                  height_ratios=heights)
        # nx.draw_networkx(self._ng, pos, ax=ax2,with_labels=True)

        ax1.tick_params(
            axis="both",
            which="both",
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )
        normal_edge_list, constraint_edge_list = self.split_into_edge_lists(self._ng)

        nx.draw_networkx_edges(self._ng, pos,
                                                  edgelist=normal_edge_list,
                                                  alpha=EDGE_ALPHA,
                                                  ax=ax2,
                                                  node_size=node_size)

        # axis_to_data = ax1.transAxes + ax1.transData.inverted()
        # points_data = axis_to_data.transform(ax2)
        # data_to_axis = axis_to_data.inverted()

        nx.draw_networkx_edges(self._ng, pos,
                               edgelist=constraint_edge_list,
                               alpha=EDGE_ALPHA,
                               style="dashed",
                               ax=ax2,
                               node_size=node_size)

        constraint_labels, edge_labels, node_labels, recursive_labels, choice_labels, stable_labels, constraint_rule_labels = self.make_labels()

        plotted_nodes = {}
        x = nx.draw_networkx_labels(self._ng, pos,
                                font_size=8,
                                ax=ax2,
                                bbox={'facecolor': 'dodgerblue',
                                      'edgecolor': 'deepskyblue',
                                      'boxstyle': 'Round4',
                                      'pad': 1},
                                labels=node_labels)
        plotted_nodes.update(x)
        x = nx.draw_networkx_labels(self._ng, pos,
                                font_size=8,
                                ax=ax2,
                                font_color='white',
                                font_weight='bold',
                                bbox={'facecolor': 'silver',
                                      'edgecolor': 'grey',
                                      'boxstyle': 'Round4',
                                      'pad': 1},
                                labels=constraint_labels)
        plotted_nodes.update(x)
        x = nx.draw_networkx_labels(self._ng, pos,
                                font_size=8,
                                ax=ax2,
                                font_color='black',
                                bbox={'facecolor': 'yellowgreen',
                                      'edgecolor': 'yellowgreen',
                                      'boxstyle': 'Round4',
                                      'pad': 1},
                                labels=stable_labels)
        plotted_nodes.update(x)

        all_rule_labels = choice_labels
        all_rule_labels.update(constraint_rule_labels)
        all_rule_labels.update(recursive_labels)
        all_rule_labels.update(edge_labels)

        texts = self.draw_rule_labels(self._ng, pos,
                              label_pos=.5,
                              rotate=False,
                              ax=ax1,
                              font_size=10,
                              horizontalalignment="right",
                              font_family="monospace",
                              bbox={'facecolor': 'white',
                                    'edgecolor': 'none',
                                    'boxstyle': 'round'},
                              edge_labels=all_rule_labels)
        min_text_x = +math.inf
        max_text_x = -math.inf
        for text in texts.values():
            x = text.get_window_extent(fig.canvas.get_renderer()).bounds
            min_text_x = min(min_text_x, x[0])
            max_text_x = max(max_text_x, x[0])
        min_text_x, max_text_x = ax2.transData.inverted().transform((min_text_x, max_text_x))

        ax1.set_ylim(ax2.get_ylim())
        #ax1.set_xlim(min_text_x, 1)


        ax2_bounds = ax2.get_tightbbox(fig.canvas.get_renderer()).bounds

        x_range = ax2_bounds[0], ax2_bounds[0]+ax2_bounds[2]/2
        min_x, max_x = ax2.transData.inverted().transform(x_range)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        # ax1.spines['top'].set_visible(False)
        # ax1.spines['right'].set_visible(False)
        # ax1.spines['bottom'].set_visible(False)
        # ax1.spines['left'].set_visible(False)

        xs, ys = zip(*pos.values())
        a = sorted(list(set(xs)))[0]
        b = sorted(list(set(xs)))[1]
        c = abs(a) - abs(b)
        ys = [y - c for y in ys]
        # plt.show()
        #fig.canvas.draw()
        #adjust_figure_size(pos, plotted_nodes, fig)
        #ax2.hlines(ys, min_x, max_x, linestyles='dashed', colors="grey", zorder=0)

        ax2.autoscale_view()
        return fig

    def make_labels(self):
        node_labels = {}
        constraint_labels = {}
        edge_labels = {}
        recursive_labels = {}
        choice_labels = {}
        stable_labels = {}
        constraint_rule_labels = {}
        for node, nbrsdict in self._ng.adjacency():
            if not node.is_still_active:
                constraint_labels[node] = self.solver_state_to_string(node)
            elif len(self._ng[node]) == 0:
                stable_labels[node] = self.solver_state_to_string(node)
            else:
                node_labels[node] = self.solver_state_to_string(node)

            for neighbor, edge_attrs in nbrsdict.items():
                rule = edge_attrs["rule"]
                rule_str = str(rule)
                if rule_str.count(":-") > 1:
                    rec_label = self.make_rec_label(rule)
                    recursive_labels[(node, neighbor)] = rec_label
                elif rule_str.count("{") > 0:
                    choice_labels[(node, neighbor)] = self.make_rule_label(rule)
                elif "#false" in rule_str:
                    constraint_rule_labels[(node, neighbor)] = self.make_rule_label(rule)
                else:
                    edge_labels[(node, neighbor)] = self.make_rule_label(rule)
        return constraint_labels, edge_labels, node_labels, recursive_labels, choice_labels, stable_labels, constraint_rule_labels

    def make_node_positions(self):
        node_size = 100
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

    def make_rule_label(self, param):
        return " ".join([str(e) for e in param])