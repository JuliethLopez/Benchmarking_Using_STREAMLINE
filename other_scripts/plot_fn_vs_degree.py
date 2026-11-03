"""Scatter of false negatives and false positive rate against inferred degree."""

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from streamline_edges import (
    CURATED,
    DEGREE_FILE,
    FIGURES,
    GSD_REP,
    IN_DEGREE_FILE,
    INPUTS,
    predicted_graph,
    reference_graph,
)


def correlation(x, y):
    if len(x) < 3 or np.unique(x).size < 2 or np.unique(y).size < 2:
        return np.nan, np.nan
    return float(pearsonr(x, y)[0]), float(spearmanr(x, y)[0])


def degree_from_csv(path, column):
    if not path.exists():
        return None
    table = pd.read_csv(path, index_col=0)
    if column not in table.columns:
        return None
    return table[column]


def inferred_degree(method, directed):
    rep_dir = CURATED / "GSD" / GSD_REP
    method_dir = rep_dir / method
    if directed:
        series = degree_from_csv(method_dir / IN_DEGREE_FILE, "Node In Degrees")
        if series is not None:
            return series
        ref_graph = reference_graph(INPUTS / "GSD" / GSD_REP / "refNetwork.csv", directed=True)
        pred_graph = predicted_graph(method_dir / "rankedEdges.csv", ref_graph, directed=True)
        if pred_graph is None:
            return None
        return pd.Series(dict(pred_graph.in_degree()), name="Node In Degrees")
    return degree_from_csv(method_dir / DEGREE_FILE, "Node Degrees")


def plot_mode(directed, y_column, y_label, file_stem):
    rep_dir = CURATED / "GSD" / GSD_REP
    table_name = "TP_FN_local_directed.csv" if directed else "TP_FN_local_undirected.csv"
    table = pd.read_csv(rep_dir / table_name)
    methods = list(dict.fromkeys(table["Method"]))
    ncols = 4
    nrows = math.ceil(len(methods) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.4 * ncols, 3.1 * nrows), squeeze=False)
    xlabel = "Grado de entrada" if directed else "Grado"
    correlations = []

    for ax, method in zip(axes.ravel(), methods):
        subset = table[table["Method"] == method]
        degrees = inferred_degree(method, directed)
        if degrees is None:
            ax.set_title(method)
            ax.text(0.5, 0.5, "sin grado", ha="center", va="center", transform=ax.transAxes)
            correlations.append({"Method": method, "Pearson": np.nan, "Spearman": np.nan, "N": 0})
            continue
        degree_frame = degrees.rename("Degree").to_frame()
        merged = subset.merge(
            degree_frame,
            left_on="Node",
            right_index=True,
            how="inner",
        )
        merged = merged.replace([np.inf, -np.inf], np.nan).dropna(subset=["Degree", y_column])
        x = merged["Degree"].astype(float).values
        y = merged[y_column].astype(float).values
        pearson, spearman = correlation(x, y)
        ax.scatter(x, y, s=36, color="#1f77b4", zorder=3)
        if len(x) and (x.max() - x.min()) < 0.5:
            ax.set_xlim(x.min() - 0.5, x.max() + 0.5)
        if np.isfinite(pearson):
            slope, intercept = np.polyfit(x, y, 1)
            xs = np.linspace(x.min(), x.max(), 40)
            ax.plot(xs, slope * xs + intercept, color="0.35", linewidth=1)
        ax.set_title(method, fontsize=10)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(y_label)
        ax.set_ylim(bottom=0)
        ax.text(
            0.04,
            0.96,
            f"Pearson r={pearson:.2f}\nSpearman ρ={spearman:.2f}"
            if np.isfinite(pearson) and np.isfinite(spearman)
            else "correlación no definida",
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=8,
        )
        correlations.append(
            {
                "Method": method,
                "Pearson": pearson,
                "Spearman": spearman,
                "N": int(len(merged)),
            }
        )

    for ax in axes.ravel()[len(methods):]:
        ax.axis("off")

    fig.suptitle(f"{GSD_REP} {'dirigido' if directed else 'no dirigido'}")
    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    tag = "directed" if directed else "undirected"
    figure_path = FIGURES / f"{GSD_REP}_{file_stem}_vs_degree_{tag}.png"
    corr_path = rep_dir / f"{file_stem}_degree_correlation_{tag}.csv"
    fig.savefig(figure_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    pd.DataFrame.from_records(correlations)[
        ["Method", "Pearson", "Spearman", "N"]
    ].to_csv(corr_path, index=False)
    print(figure_path)
    print(corr_path)


def main():
    for directed in (False, True):
        plot_mode(directed, "FN", "Falsos negativos", "FN")
        plot_mode(directed, "FPR", "Tasa de falsos positivos", "FPR")


if __name__ == "__main__":
    main()
