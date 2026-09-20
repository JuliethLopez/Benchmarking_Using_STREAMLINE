#!/usr/bin/env bash
# Idempotent setup for the STREAMLINE development environment.
# Installs Miniforge (if missing) and creates/updates the `streamline` conda
# environment from environment.yml, then smoke-tests the critical imports.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MINIFORGE_DIR="${HOME}/miniforge3"

# 1. Install Miniforge (conda + mamba) if it is not already present.
if [ ! -x "${MINIFORGE_DIR}/bin/conda" ]; then
  echo "==> Installing Miniforge to ${MINIFORGE_DIR}"
  curl -fsSL -o /tmp/miniforge.sh \
    https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
  bash /tmp/miniforge.sh -b -p "${MINIFORGE_DIR}"
  rm -f /tmp/miniforge.sh
else
  echo "==> Miniforge already present at ${MINIFORGE_DIR}"
fi

# shellcheck disable=SC1091
source "${MINIFORGE_DIR}/etc/profile.d/conda.sh"

# 2. Create or update the `streamline` env from environment.yml (idempotent).
if conda env list | awk '{print $1}' | grep -qx streamline; then
  echo "==> Updating existing 'streamline' conda environment"
  conda env update -n streamline -f "${REPO_DIR}/environment.yml" --prune
else
  echo "==> Creating 'streamline' conda environment"
  conda env create -f "${REPO_DIR}/environment.yml"
fi

# 3. Make new interactive shells activate the streamline env automatically.
conda init bash >/dev/null 2>&1 || true
if ! grep -q "conda activate streamline" "${HOME}/.bashrc" 2>/dev/null; then
  echo "conda activate streamline" >> "${HOME}/.bashrc"
fi

# 4. Smoke-test the full dependency chain used by the pipeline.
echo "==> Verifying imports"
conda run -n streamline python - <<'PY'
import numpy, pandas, networkx, tqdm, yaml, scipy, seaborn, matplotlib, sklearn
import graph_tool.all as gt
import rpy2
from rpy2.robjects.packages import importr
importr("PRROC")
print("STREAMLINE environment OK | graph-tool", gt.__version__.split()[0],
      "| scikit-learn", sklearn.__version__)
PY

echo "==> Done. Activate with: conda activate streamline"
