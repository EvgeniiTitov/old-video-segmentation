import typing as t
from abc import ABC
from abc import abstractmethod

import numpy as np


class AbstractSegmenter(ABC):
    @abstractmethod
    def process_batch(
        self, batch: t.Sequence[np.ndarray]
    ) -> t.Sequence[np.ndarray]:
        ...
