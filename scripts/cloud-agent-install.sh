#!/usr/bin/env bash
# Idempotent setup for the STREAMLINE development environment.
# Installs Miniforge (if missing) and creates/updates the `BEELINE` conda
# environment from environment.yml, then smoke-tests the critical imports.
# The env is named BEELINE because STREAMLINE is an evaluation extension of
# BEELINE and is run from the same conda environment as that prerequisite.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MINIFORGE_DIR="${HOME}/miniforge3"
ENV_NAME="BEELINE"

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

# 2. Create or update the `BEELINE` env from environment.yml (idempotent).
if conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
  echo "==> Updating existing '${ENV_NAME}' conda environment"
  conda env update -n "${ENV_NAME}" -f "${REPO_DIR}/environment.yml" --prune
else
  echo "==> Creating '${ENV_NAME}' conda environment"
  conda env create -f "${REPO_DIR}/environment.yml"
fi

# 3. Make new interactive shells activate the BEELINE env automatically.
conda init bash >/dev/null 2>&1 || true
if ! grep -q "conda activate ${ENV_NAME}" "${HOME}/.bashrc" 2>/dev/null; then
  echo "conda activate ${ENV_NAME}" >> "${HOME}/.bashrc"
fi

# 4. Smoke-test the full dependency chain used by the pipeline.
echo "==> Verifying imports"
conda run -n "${ENV_NAME}" python - <<'PY'
import numpy, pandas, networkx, tqdm, yaml, scipy, seaborn, matplotlib, sklearn
import graph_tool.all as gt
import rpy2
from rpy2.robjects.packages import importr
importr("PRROC")
print("STREAMLINE environment OK | graph-tool", gt.__version__.split()[0],
      "| scikit-learn", sklearn.__version__)
PY

echo "==> Done. Activate with: conda activate ${ENV_NAME}"
