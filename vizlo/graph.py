import math

from typing import Tuple, Dict, Any, Collection, Union
from collections import Counter
import igraph
import networkx as nx
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import ConnectionPatch
from matplotlib.path import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mp

from vizlo.solver import SolverState
from vizlo.util import log

NODE_SIZE = 0

EDGE_ALPHA = 0.3


class MyBoxStyle(mp.BoxStyle.Round):
    def __init__(self, pad=1, rounding_size=None):
        super().__init__(pad, rounding_size)

    def transmute(self, x0, y0, width, height, mutation_size):

        # padding
        pad = mutation_size * self.pad

        # size of the rounding corner
        if self.rounding_size:
            dr = mutation_size * self.rounding_size
        else:
            dr = pad

            width, height = width + 2 * pad, height + 2 * pad

            x0, y0 = x0 - pad, y0 - pad,
            x1, y1 = x0 + width, y0 + height
            arrow_width = (width + height) / 2 * .3
            half_arrow_width = arrow_width / 2
            middle_y = y0 + y1 / 2
            middle_x = x0 + x1 / 2

            # Round corners are implemented as quadratic Bezier, e.g.,
            # [(x0, y0-dr), (x0, y0), (x0+dr, y0)] for lower left corner.
            cp = [(middle_x, y0),
                  (middle_x, y0),
                  (middle_x, y0 - half_arrow_width),
                  (middle_x + arrow_width, y0),
                  (middle_x, y0 + half_arrow_width),
                  (middle_x, y0 - half_arrow_width),
                  (middle_x + arrow_width, y0),
                  (x1, y0), (x1, middle_y),
                  (x1 + half_arrow_width, middle_y),
                  (x1, middle_y + arrow_width),
                  (x1 - half_arrow_width, middle_y),
                  (x1 + half_arrow_width, middle_y),
                  (x1, middle_y + arrow_width),
                  (x1, y1), (middle_x + arrow_width, y1),
                  (middle_x + arrow_width, y1 + half_arrow_width),
                  (middle_x, y1),
                  (middle_x + arrow_width, y1 - half_arrow_width),
                  (middle_x + arrow_width, y1 + half_arrow_width),
                  (middle_x, y1),
                  (x0, y1), (x0, middle_y + arrow_width),
                  (x0 - half_arrow_width, middle_y + arrow_width),
                  (x0, middle_y),
                  (x0 + half_arrow_width, middle_y + arrow_width),
                  (x0 - half_arrow_width, middle_y + arrow_width),
                  (x0, middle_y),
                  (x0, y0), (middle_x, y0),
                  (middle_x, y0)
                  ]

            com = [Path.MOVETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.CURVE3, Path.CURVE3,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.CURVE3, Path.CURVE3,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.CURVE3, Path.CURVE3,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.LINETO,
                   Path.CURVE3, Path.CURVE3,
                   Path.CLOSEPOLY
                   ]
            path = Path(cp, com, closed=True)
            return path


def adjust_figure_size(plotted_nodes: Dict[SolverState, Any], fig: Figure):
    nodes_per_row = Counter()
    rows = set()
    for node in plotted_nodes.keys():
        step = node.step
        nodes_per_row[step] += 1
        rows.add(step)
    _, num_of_cols = nodes_per_row.most_common(1)[0]
    fig.set_size_inches((max(5, math.ceil(num_of_cols * 1.25)), max(8, math.ceil(len(rows)))), forward=True)


class NetworkxDisplay:

    def __init__(self, graph, atom_draw_maximum=20, print_changes_only=True, merge_nodes=True):
        if merge_nodes:
            self._ng = self.merge_nodes_on_same_step(graph)
        else:
            self._ng = graph
        self.atom_draw_maximum = atom_draw_maximum
        self._print_changes_only = print_changes_only
        self.max_depth = max(n.step for n in self._ng.nodes())
        self._ig: igraph.Graph = self.nxgraph_to_igraph(self._ng)
        log(f"Initialized {self.__class__}")

    def model_to_string(self, model: Collection):
        if self.atom_draw_maximum <= 0:
            return ""
        if not len(model):
            return "\u2205"
        result_str = ""
        atoms_to_draw = list(model)[:min(len(model), self.atom_draw_maximum)]
        how_many_per_line = math.sqrt(sum(len(str(m)) for m in atoms_to_draw))
        tmp = ""
        for m in atoms_to_draw:
            if len(tmp) >= how_many_per_line:
                result_str += tmp.strip() + "\n"
                tmp = ""
            tmp += str(m) + " "
        result_str += tmp.strip()
        return f"{result_str}"

    def solver_state_to_string(self, solver_state: SolverState) -> str:
        atoms_to_draw = solver_state.adds if self._print_changes_only and self.max_depth != solver_state.step else solver_state.model
        return self.model_to_string(atoms_to_draw)

    def merge_nodes_on_same_step(self, g: nx.Graph):
        mapping = {}
        for x in g.nodes():
            for y in g.nodes():
                if x.step == y.step and x.model == y.model and x.is_still_active == y.is_still_active:
                    mapping[x] = y
        return nx.relabel_nodes(g, mapping)

    def create_rule_positions(self, pos: Dict[SolverState, Tuple[float, float]],
                              labels: Dict[Tuple[SolverState, SolverState], str]):
        rule_positions = {}
        for (n1, n2), label in labels.items():
            (x1, y1) = pos[n1]
            (x2, y2) = pos[n2]
            (x, y) = (
                x1 * .5 + x2 * .5,
                y1 * .5 + y2 * .5,
            )
            rule_positions[label] = (x, y)
        return rule_positions

    def draw_rule_labels(self, pos,
                         edge_labels=None,
                         font_size=10,
                         font_color='k',
                         font_family='sans-serif',
                         font_weight='normal',
                         bbox=None,
                         ax=None,
                         horizontalalignment='right'):
        labels = edge_labels
        text_items = {}
        for (n1, n2), label in labels.items():
            (_, y) = pos[n2]
            x = 1

            t = ax.text(x, y,
                        label,
                        size=font_size,
                        color=font_color,
                        family=font_family,
                        weight=font_weight,
                        horizontalalignment=horizontalalignment,
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
        for edge in g.edges(data=True):
            if "#false" in str(edge[2]["rule"]):
                constraints.append(edge)
            else:
                normal.append(edge)
        return normal, constraints

    def draw(self, figsize: Union[Tuple[float, float], None] = None, dpi: int = 300, rule_font_size: int = 12,
             model_font_size: int = 10):
        """
        Will draw the graph visualization of a logic programs solving.
        :param figsize: Tuple[float, float]
            The figure size the visualization will be set to. If none, vizlo tries to extrapolate a appropriate one.
            default=None
        :param dpi: int
            The dots per inch ratio for the visualization.
            default=300
        :param rule_font_size: int
            The font size for the rules.
            default=12
        :param model_font_size: int
            The font size for the atoms in the model nodes.
            default=10
        :return:
        """
        # 1. Figure out node positions using igraph
        log(f"Drawing graph with {len(self._ng)} nodes.")
        pos = self.make_node_positions()
        fig = plt.figure(dpi=dpi)
        specs = fig.add_gridspec(ncols=2, nrows=1, width_ratios=[1, 2])
        rule_axis = fig.add_subplot(specs[0, 0])
        graph_axis = fig.add_subplot(specs[0, 1], sharey=rule_axis)

        self.draw_edges(graph_axis, pos)

        normal_models, recursive_models, constraint_models, stable_models, rule_labels = self.make_labels()

        plotted_nodes = self.draw_models(graph_axis, constraint_models, model_font_size, normal_models, pos,
                                         recursive_models,
                                         stable_models)

        self.draw_rule_labels(pos,
                              ax=rule_axis,
                              font_size=rule_font_size,
                              horizontalalignment="right",
                              font_family="monospace",
                              bbox={'facecolor': 'none',
                                    'edgecolor': 'none',
                                    'boxstyle': 'round'},
                              edge_labels=rule_labels)

        rule_axis.set_ylim(graph_axis.get_ylim())

        rule_positions = self.create_rule_positions(pos, rule_labels)

        self.remove_clutter_from_axis(rule_axis)
        self.remove_clutter_from_axis(graph_axis)
        self.draw_lines_at_rule_boarders(rule_axis, graph_axis, rule_positions)

        rule_axis.apply_aspect()
        graph_axis.apply_aspect()

        fig.tight_layout()
        if figsize is None:
            adjust_figure_size(plotted_nodes, fig)
        else:
            fig.set_size_inches(figsize)
        return fig

    def draw_models(self, graph_axis: Axes,
                    constraint_models: Dict[SolverState, str],
                    model_font_size: int,
                    normal_models: Dict[SolverState, str],
                    pos: Dict[SolverState, Tuple[float, float]],
                    recursive_models: Dict[SolverState, str],
                    stable_models: Dict[SolverState, str]
                    ):
        recursive_and_stable_models = {node: stable_models[node] for node in stable_models if
                                       recursive_models.get(node, not stable_models[node]) == stable_models[node]}
        stable_models = {node: label for node, label in stable_models.items() if
                         node not in recursive_and_stable_models}
        recursive_models = {node: label for node, label in recursive_models.items() if
                            node not in recursive_and_stable_models}
        plotted_nodes = {}
        x = nx.draw_networkx_labels(self._ng, pos,
                                    font_size=model_font_size,
                                    ax=graph_axis,
                                    bbox={'facecolor': 'yellowgreen',
                                          'edgecolor': 'greenyellow',
                                          'boxstyle': MyBoxStyle(),
                                          'pad': 1},
                                    labels=recursive_and_stable_models)
        plotted_nodes.update(x)
        x = nx.draw_networkx_labels(self._ng, pos,
                                    font_size=model_font_size,
                                    ax=graph_axis,
                                    bbox={'facecolor': 'dodgerblue',
                                          'edgecolor': 'deepskyblue',
                                          'boxstyle': 'Round4',
                                          'pad': 1},
                                    labels=normal_models)
        plotted_nodes.update(x)
        x = nx.draw_networkx_labels(self._ng, pos,
                                    font_size=model_font_size,
                                    ax=graph_axis,
                                    bbox={'facecolor': 'dodgerblue',
                                          'edgecolor': 'deepskyblue',
                                          'boxstyle': MyBoxStyle(),
                                          'pad': 1},
                                    labels=recursive_models)
        plotted_nodes.update(x)
        x = nx.draw_networkx_labels(self._ng, pos,
                                    font_size=model_font_size,
                                    ax=graph_axis,
                                    font_color='white',
                                    font_weight='bold',
                                    bbox={'facecolor': 'silver',
                                          'edgecolor': 'grey',
                                          'boxstyle': 'Round4',
                                          'pad': 1},
                                    labels=constraint_models)
        plotted_nodes.update(x)
        x = nx.draw_networkx_labels(self._ng, pos,
                                    font_size=model_font_size,
                                    ax=graph_axis,
                                    font_color='black',
                                    bbox={'facecolor': 'yellowgreen',
                                          'edgecolor': 'greenyellow',
                                          'boxstyle': 'Round4',
                                          'pad': 1},
                                    labels=stable_models)
        plotted_nodes.update(x)
        return plotted_nodes

    def draw_edges(self, ax: Axes, pos: Dict[SolverState, Tuple[float, float]]):
        normal_edge_list, constraint_edge_list = self.split_into_edge_lists(self._ng)
        nx.draw_networkx_edges(self._ng, pos,
                               edgelist=normal_edge_list,
                               alpha=EDGE_ALPHA,
                               ax=ax,
                               node_size=NODE_SIZE)
        nx.draw_networkx_edges(self._ng, pos,
                               edgelist=constraint_edge_list,
                               alpha=EDGE_ALPHA,
                               style="dashed",
                               ax=ax,
                               node_size=NODE_SIZE)

    def draw_rule_delimiters(self, y: Tuple[float, float], ax1: Axes, ax2: Axes, min_x1: float, max_x1: float,
                             min_x2: float, max_x2: float, **kwargs):
        axis_to_data = ax1.transAxes + ax1.transData.inverted()
        ax1_data_to_axis = axis_to_data.inverted()
        axis_to_data = ax2.transAxes + ax2.transData.inverted()
        ax2_data_to_axis = axis_to_data.inverted()
        y1 = ax1_data_to_axis.transform(y)[1]
        y2 = ax2_data_to_axis.transform(y)[1]
        ax1.plot([min_x1, max_x1], [y1, y1],
                 transform=ax1.get_xaxis_transform(), **kwargs)
        ax2.plot([min_x2, max_x2], [y2, y2],
                 transform=ax2.get_xaxis_transform(), **kwargs)

        p = ConnectionPatch((max_x1, y1), (min_x2, y2),
                            coordsA=ax1.get_xaxis_transform(),
                            coordsB=ax2.get_xaxis_transform(), **kwargs)

        ax1.add_artist(p)

    def draw_lines_at_rule_boarders(self, ax1: Axes, ax2: Axes, pos: Dict[SolverState, Tuple[float, float]]):
        pos_as_list = list(pos.values())
        min_x1, max_x1 = ax1.get_xlim()
        min_x2, max_x2 = ax2.get_xlim()
        for rule_position in pos_as_list:
            self.draw_rule_delimiters(rule_position, ax1, ax2, min_x1, max_x1, min_x2, max_x2, linewidth=1, zorder=0,
                                      color='grey')

    def remove_clutter_from_axis(self, axis: Axes):
        axis.patch.set_alpha(0.0)
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.spines['bottom'].set_visible(False)
        axis.spines['left'].set_visible(False)
        axis.tick_params(
            axis="both",
            which="both",
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )

    def make_labels(self):
        normal_models = {}
        constraint_models = {}
        recursive_models = {}
        stable_models = {}
        rule_labels = {}
        for node, nbrsdict in self._ng.adjacency():
            if not node.is_still_active:
                constraint_models[node] = self.solver_state_to_string(node)
            elif len(self._ng[node]) == 0:
                stable_models[node] = self.solver_state_to_string(node)
            else:
                normal_models[node] = self.solver_state_to_string(node)

            for neighbor, edge_attrs in nbrsdict.items():
                rule = edge_attrs["rule"]
                rule_str = str(rule)
                if rule_str.count(":-") > 1:
                    recursive_models[neighbor] = self.solver_state_to_string(neighbor)
                    rule_labels[(node, neighbor)] = self.make_rec_label(rule)
                else:
                    rule_labels[(node, neighbor)] = self.make_rule_label(rule)
        return normal_models, recursive_models, constraint_models, stable_models, rule_labels

    def make_node_positions(self):
        layout = self._ig.layout_reingold_tilford(root=[0])
        layout.rotate(180)
        nx_map = {i: node for i, node in enumerate(self._ng.nodes())}
        pos = self.igraph_to_networkx_layout(layout, nx_map)
        return pos

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
