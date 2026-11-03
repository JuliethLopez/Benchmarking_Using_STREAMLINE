"""Mean node-degree frequency by method, one figure per curated dataset."""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from streamline_edges import CURATED, DATASETS, DEGREE_FILE, FIGURES, SIZES


def replicate_dirs(dataset, size):
    root = CURATED / dataset
    prefix = f"{dataset}-{size}-"
    reps = []
    for path in root.iterdir():
        if path.is_dir() and path.name.startswith(prefix):
            suffix = path.name[len(prefix):]
            if suffix.isdigit():
                reps.append(path)
    return sorted(reps, key=lambda p: int(p.name[len(prefix):]))


def method_names(reps):
    found = set()
    for rep in reps:
        for path in rep.iterdir():
            if path.is_dir() and (path / DEGREE_FILE).exists():
                found.add(path.name)
    ordered = sorted(name for name in found if name != "ground truth")
    if "ground truth" in found:
        ordered.insert(0, "ground truth")
    return ordered


def mean_frequency(samples, index):
    counts = []
    for degrees in samples:
        counts.append(degrees.value_counts().reindex(index, fill_value=0))
    return pd.concat(counts, axis=1).mean(axis=1)


def frequencies_for_size(dataset, size):
    reps = replicate_dirs(dataset, size)
    methods = method_names(reps)
    samples = {method: [] for method in methods}
    for rep in reps:
        for method in methods:
            path = rep / method / DEGREE_FILE
            if not path.exists():
                continue
            degrees = pd.read_csv(path, index_col=0)["Node Degrees"].dropna().astype(int)
            if degrees.empty:
                continue
            samples[method].append(degrees)
    present = {method: vals for method, vals in samples.items() if vals}
    if not present:
        return {}
    max_degree = max(int(series.max()) for vals in present.values() for series in vals)
    index = pd.RangeIndex(0, max_degree + 1)
    return {method: mean_frequency(vals, index) for method, vals in present.items()}


def plot_dataset(dataset):
    panels = [(size, frequencies_for_size(dataset, size)) for size in SIZES]
    methods = []
    for _, freqs in panels:
        for method in freqs:
            if method not in methods:
                methods.append(method)

    max_degree = 0
    for _, freqs in panels:
        for series in freqs.values():
            if len(series):
                max_degree = max(max_degree, int(series.index.max()))
    degrees = np.arange(0, max_degree + 1)

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8), sharex=True, sharey=True)
    colors = {}
    palette = plt.get_cmap("tab10")
    color_i = 0
    for method in methods:
        if method == "ground truth":
            colors[method] = "black"
        else:
            colors[method] = palette(color_i % 10)
            color_i += 1

    n_methods = max(len(methods), 1)
    width = 0.82 / n_methods
    for ax, (size, freqs) in zip(axes, panels):
        for i, method in enumerate(methods):
            series = freqs.get(method)
            if series is None:
                values = np.zeros(len(degrees))
            else:
                values = series.reindex(degrees, fill_value=0).astype(float).values
            offset = (i - (n_methods - 1) / 2.0) * width
            ax.bar(
                degrees + offset,
                values,
                width=width * 0.92,
                color=colors[method],
                label=method,
                zorder=2,
            )
        ax.set_title(str(size))
        ax.set_xlabel("Grado")
        ax.set_xticks(degrees)
        ax.set_xlim(-0.6, max_degree + 0.6)
        ax.set_ylim(bottom=0)
    axes[0].set_ylabel("Media del número de nodos")
    fig.suptitle(dataset, y=0.98)
    handles = [Patch(facecolor=colors[method], label=method) for method in methods]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    fig.tight_layout(rect=[0, 0, 0.84, 0.90])
    FIGURES.mkdir(parents=True, exist_ok=True)
    out = FIGURES / f"{dataset}_degree_frequency.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(out)


def main():
    for dataset in DATASETS:
        plot_dataset(dataset)


if __name__ == "__main__":
    main()
