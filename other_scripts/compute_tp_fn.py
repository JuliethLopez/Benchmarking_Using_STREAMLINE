"""Per-node true positives, false positives and false positive rate for GSD-2000-1."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from streamline_edges import CURATED, GSD_REP, INPUTS, predicted_graph, reference_graph


def method_dirs(rep_dir):
    methods = []
    for path in rep_dir.iterdir():
        if path.is_dir() and (path / "rankedEdges.csv").exists():
            methods.append(path)
    return sorted(methods, key=lambda p: p.name)


def _rate(fp, negatives):
    if negatives == 0:
        return float("nan")
    return float(fp) / float(negatives)


def undirected_counts(ref_graph, pred_graph):
    """FP are predicted neighbors that are not real. FPR = FP / non-edges."""
    n_others = ref_graph.number_of_nodes() - 1
    rows = []
    for node in ref_graph.nodes:
        real_neighbors = set(ref_graph.neighbors(node))
        if node in pred_graph:
            pred_neighbors = set(pred_graph.neighbors(node))
        else:
            pred_neighbors = set()
        real = len(real_neighbors)
        tp = len(real_neighbors & pred_neighbors)
        fp = len(pred_neighbors - real_neighbors)
        rows.append((node, real, tp, fp, real - tp, _rate(fp, n_others - real)))
    return rows


def directed_counts(ref_graph, pred_graph):
    """FP are predicted incoming edges that are not real. FPR = FP / non-edges."""
    n_others = ref_graph.number_of_nodes() - 1
    rows = []
    for node in ref_graph.nodes:
        real_sources = set(ref_graph.predecessors(node))
        if node in pred_graph:
            pred_sources = set(pred_graph.predecessors(node))
        else:
            pred_sources = set()
        real = len(real_sources)
        tp = len(real_sources & pred_sources)
        fp = len(pred_sources - real_sources)
        rows.append((node, real, tp, fp, real - tp, _rate(fp, n_others - real)))
    return rows


def build_table(rep_dir, ref_path, directed):
    ref_graph = reference_graph(ref_path, directed=directed)
    records = []
    for method_dir in method_dirs(rep_dir):
        pred_graph = predicted_graph(
            method_dir / "rankedEdges.csv", ref_graph, directed=directed
        )
        if pred_graph is None:
            print(f"Warning - no edges for {method_dir.name} directed={directed}")
            continue
        counter = directed_counts if directed else undirected_counts
        for node, real, tp, fp, fn, fpr in counter(ref_graph, pred_graph):
            records.append(
                {
                    "Method": method_dir.name,
                    "Node": node,
                    "Real": real,
                    "TP": tp,
                    "FP": fp,
                    "FN": fn,
                    "FPR": fpr,
                }
            )
    table = pd.DataFrame.from_records(records)
    if directed:
        table = table.rename(columns={"Real": "RealInEdges"})
        columns = ["Method", "Node", "RealInEdges", "TP", "FP", "FN", "FPR"]
    else:
        table = table.rename(columns={"Real": "RealEdges"})
        columns = ["Method", "Node", "RealEdges", "TP", "FP", "FN", "FPR"]
    table = table[columns]
    return table.sort_values(["Method", "Node"]).reset_index(drop=True)


def main():
    rep_dir = CURATED / "GSD" / GSD_REP
    ref_path = INPUTS / "GSD" / GSD_REP / "refNetwork.csv"
    undirected = build_table(rep_dir, ref_path, directed=False)
    directed = build_table(rep_dir, ref_path, directed=True)
    undirected_path = rep_dir / "TP_FN_local_undirected.csv"
    directed_path = rep_dir / "TP_FN_local_directed.csv"
    undirected.to_csv(undirected_path, index=False)
    directed.to_csv(directed_path, index=False)
    print(undirected_path, undirected.shape)
    print(directed_path, directed.shape)


if __name__ == "__main__":
    main()
