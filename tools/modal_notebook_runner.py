"""Run selected lab notebooks on Modal for headless validation."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import traceback

import modal


APP_NAME = "fsdl-lab-notebook-runner"
REMOTE_REPO = Path("/root/repo")
WORK_REPO = Path("/tmp/fsdl-text-recognizer-2022-labs")

NOTEBOOKS = {
    "lab06": {
        "path": "lab08/notebooks/lab06_data.ipynb",
        # Manual service/auth cells: ngrok auth, tunnel, label-studio install/start,
        # and the cleanup cell that can rewrite requirements via make.
        "skip_cells": {80, 82, 84, 85, 87, 94},
    },
    "lab07": {
        "path": "lab08/notebooks/lab07_deployment.ipynb",
        # Manual service/auth cells: Gradio share/API curl/close and ngrok tunnel.
        "skip_cells": {63, 65, 68, 71, 73, 76, 106, 111, 113},
    },
}


image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("curl", "git", "make", "unzip")
    .run_commands("python -m pip install 'pip<24.1'")
    .pip_install_from_requirements("requirements/prod.txt")
    .pip_install_from_requirements("requirements/dev.txt")
    .pip_install("nbclient", "ipykernel")
    .add_local_dir(
        ".",
        remote_path=str(REMOTE_REPO),
        ignore=[
            ".git",
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            "data",
            "data.zip",
            "lightning_logs",
            "build",
        ],
    )
    .add_local_dir("data/raw/iam", remote_path=str(REMOTE_REPO / "data/raw/iam"))
)

app = modal.App(APP_NAME)


def _prepare_work_repo() -> None:
    if WORK_REPO.exists():
        shutil.rmtree(WORK_REPO)
    shutil.copytree(REMOTE_REPO, WORK_REPO)


def _patch_notebook_for_headless_run(notebook_path: Path, skip_cells: set[int]) -> None:
    notebook = json.loads(notebook_path.read_text())
    for idx, cell in enumerate(notebook["cells"]):
        if idx in skip_cells and cell.get("cell_type") == "code":
            original = "".join(cell.get("source", []))
            cell["source"] = [
                f"# Skipped during Modal headless validation: cell {idx}\\n",
                "print('Skipped interactive/auth/service cell during Modal validation.')\\n",
                "\\n",
                "# Original cell source kept below for notebook readers.\\n",
                *[f"# {line}" for line in original.splitlines(keepends=True)],
            ]
            cell["execution_count"] = None
            cell["outputs"] = []
    notebook_path.write_text(json.dumps(notebook, indent=2, ensure_ascii=False) + "\n")


def _execute_notebook(name: str, notebook_relpath: str, skip_cells: set[int]) -> dict[str, str | bool]:
    import nbformat
    from nbclient import NotebookClient

    notebook_path = WORK_REPO / notebook_relpath
    _patch_notebook_for_headless_run(notebook_path, skip_cells)

    os.environ.setdefault("WANDB_MODE", "offline")
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    os.chdir(WORK_REPO)

    notebook = nbformat.read(notebook_path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=900,
        kernel_name="python3",
        allow_errors=False,
        record_timing=True,
    )

    try:
        client.execute()
    except Exception:
        executed_path = WORK_REPO / f"{name}_executed_error.ipynb"
        nbformat.write(notebook, executed_path)
        return {
            "ok": False,
            "name": name,
            "notebook": notebook_relpath,
            "traceback": traceback.format_exc(limit=8),
        }

    executed_path = WORK_REPO / f"{name}_executed_ok.ipynb"
    nbformat.write(notebook, executed_path)
    return {"ok": True, "name": name, "notebook": notebook_relpath, "traceback": ""}


@app.function(image=image, timeout=60 * 90)
def run_labs(names: list[str]) -> list[dict[str, str | bool]]:
    _prepare_work_repo()
    results = []
    for name in names:
        spec = NOTEBOOKS[name]
        results.append(_execute_notebook(name, spec["path"], spec["skip_cells"]))
    return results


@app.local_entrypoint()
def main(*names: str):
    selected = list(names) or ["lab06", "lab07"]
    results = run_labs.remote(selected)
    print(json.dumps(results, indent=2))
