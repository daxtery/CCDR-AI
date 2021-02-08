import pickle
from typing import List

from interference.operations import Operation


def read_operations(path: str) -> List[Operation]:
    with open(path, 'rb') as file:
        return pickle.load(file)
