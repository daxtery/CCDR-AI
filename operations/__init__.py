from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from interference.operations import Operation
import pickle

import os


@dataclass
class OperationFile:
    """
    layer: "avg"\n
    test_subpath: "1/avg"\n
    full_path: "data/operations_instances_ss_confirmed/1/avg"
    """
    layer: str
    test_subpath: str
    full_path: str


_BASE = "data/operations_instances_ss_confirmed"


def fetch_operations_files(sub_folders: Optional[List[str]] = None, layers: Optional[List[str]] = None) -> List[OperationFile]:
    collected: List[OperationFile] = []

    for folder_name in os.listdir(_BASE):
        if folder_name in ["__pycache__", "__init__.py"]:
            continue

        if sub_folders is not None and not folder_name in sub_folders:
            continue

        folder_path = os.path.join(_BASE, folder_name)

        for layer in os.listdir(folder_path):
            if layers is not None and layer not in layers:
                continue

            full_path = os.path.join(folder_path, layer)
            test_subpath = os.path.join(folder_name, layer)

            collected.append(OperationFile(layer, test_subpath, full_path))

    return collected


def store_operations(layer: str, subfolder_no_layer: str, operations: List[Operation]) -> OperationFile:
    subfolder = os.path.join(_BASE, subfolder_no_layer)
    folder_path = os.path.join(subfolder, layer)
    Path(folder_path).parent.mkdir(parents=True, exist_ok=True)

    with open(folder_path, 'wb') as f:
        pickle.dump(operations, f)
        return OperationFile(layer, subfolder, folder_path)
