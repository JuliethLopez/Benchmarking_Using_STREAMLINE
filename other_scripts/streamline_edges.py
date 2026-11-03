"""Edge loading that follows STREAMLINE's load_data and largest-component cut."""

from pathlib import Path

import networkx as nx
import pandas as pd

BEELINE = Path("/lustre/scratch127/humgen/projects_v2/jaguar_analysis/analysis/jl38/Beeline")
CURATED = BEELINE / "outputs" / "Curated"
INPUTS = BEELINE / "inputs" / "Curated"
SCRIPTS = Path("/lustre/scratch127/humgen/projects_v2/jaguar_analysis/analysis/jl38/STREAMLINE/other_scripts")
FIGURES = SCRIPTS / "figures"

DATASETS = ("GSD", "HSC", "mCAD", "VSC")
SIZES = (200, 1000, 2000)
DEGREE_FILE = "STREAMLINE_local_undirected_raw.csv"
IN_DEGREE_FILE = "STREAMLINE_local_directed_raw.csv"
GSD_REP = "GSD-2000-1"


def load_edges(path, sep, directed):
    """Match BLEval.computeSTREAMLINE.load_data."""
    edges = pd.read_csv(path, sep=sep, header=0, index_col=None)
    edges = edges[edges["Gene1"] != edges["Gene2"]]
    if not directed:
        swap = edges["Gene1"] > edges["Gene2"]
        gene1 = edges.loc[swap, "Gene1"].copy()
        edges.loc[swap, "Gene1"] = edges.loc[swap, "Gene2"].values
        edges.loc[swap, "Gene2"] = gene1.values
    edges = edges.drop_duplicates(subset=["Gene1", "Gene2"], keep="first")
    return edges.reset_index(drop=True)


def largest_component(edge_df, directed):
    """Match BLEval.computeSTREAMLINE.nx_largest_subgraph."""
    if directed:
        graph = nx.from_pandas_edgelist(
            edge_df, source="Gene1", target="Gene2", create_using=nx.DiGraph()
        )
        components = nx.weakly_connected_components(graph)
    else:
        graph = nx.from_pandas_edgelist(
            edge_df, source="Gene1", target="Gene2", create_using=nx.Graph()
        )
        components = nx.connected_components(graph)
    component = max(components, key=len)
    return graph.subgraph(component).copy()


def reference_graph(ref_path, directed):
    return largest_component(load_edges(ref_path, sep=",", directed=directed), directed)


def predicted_graph(ranked_path, ref_graph, directed):
    """Top-k predicted edges, k = number of reference edges, then largest component."""
    pred = load_edges(ranked_path, sep="\t", directed=directed)
    pred["EdgeWeight"] = pred["EdgeWeight"].abs()
    nodes = set(ref_graph.nodes)
    pred = pred[pred["Gene1"].isin(nodes) & pred["Gene2"].isin(nodes)]
    pred = pred.reset_index(drop=True)
    if pred.shape[0] == 0:
        return None
    num_edges = ref_graph.number_of_edges()
    if pred.shape[0] < num_edges:
        num_edges = pred.shape[0]
    pred = pred.iloc[:num_edges]
    return largest_component(pred, directed)
