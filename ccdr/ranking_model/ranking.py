import numpy


class RankingModel:
    def __init__(self) -> None:
        pass

    def __call__(self, query_embedding: numpy.ndarray, equipments_embeddings: numpy.ndarray) -> float:
        return 0.
