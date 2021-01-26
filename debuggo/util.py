from collections.abc import Iterable
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection

import numpy as np
def draw_nodes(
    G,
    pos,
    nodelist=None,
    node_size=300,
    node_size_map=None,
    node_color="#1f78b4",
    node_shape="o",
    alpha=None,
    cmap=None,
    vmin=None,
    vmax=None,
    ax=None,
    linewidths=None,
    edgecolors=None,
    label=None,
):
    if ax is None:
        ax = plt.gca()

    if nodelist is None:
        nodelist = list(G)

    try:
        xy = np.asarray([pos[v] for v in nodelist])
    except KeyError as e:
        raise nx.NetworkXError(f"Node {e} has no position.") from e
    except ValueError as e:
        raise nx.NetworkXError("Bad value in node positions.") from e

    # node_size_map = { node : size }
    if node_size_map:
        sizes = [node_size_map[v] for v in nodelist]
    else:
        sizes=node_size

    node_collection = ax.scatter(
        xy[:, 0],
        xy[:, 1],
        s=sizes,
        c=node_color,
        marker=node_shape,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        alpha=alpha,
        linewidths=linewidths,
        edgecolors=edgecolors,
        label=label,
    )
    ax.tick_params(
        axis="both",
        which="both",
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False,
    )

    node_collection.set_zorder(2)
    return node_collection