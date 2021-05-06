import typing as t

import numpy as np
from abstract_segmenter import AbstractSegmenter


class SegmenterV1(AbstractSegmenter):
    def __init__(self):
        pass

    def process_batch(
        self, batch: t.Sequence[np.ndarray]
    ) -> t.Sequence[t.Any]:
        pass
