import typing as t

import cv2
import numpy as np

from .abstract_segmenter import AbstractSegmenter


class SegmenterV2(AbstractSegmenter):
    def __init__(self):
        self._kernel_1 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        self._kernel_2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        self._subtractor = cv2.createBackgroundSubtractorMOG2()

    def process_batch(
        self, batch: t.Sequence[np.ndarray]
    ) -> t.Sequence[np.ndarray]:
        return [self.process_frame(frame) for frame in batch]

    # @timer
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        mask = self._subtractor.apply(frame)
        th = cv2.threshold(mask, 244, 255, cv2.THRESH_BINARY)[1]
        dilate_eroison = cv2.morphologyEx(
            th, cv2.MORPH_OPEN, iterations=2, kernel=self._kernel_1
        )
        closing = cv2.morphologyEx(
            dilate_eroison, cv2.MORPH_CLOSE, self._kernel_2
        )
        return cv2.bitwise_and(frame, frame, mask=closing)
