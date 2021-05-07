import typing as t

import cv2
import numpy as np

from .abstract_segmenter import AbstractSegmenter
from helpers import timer


class SegmenterV1(AbstractSegmenter):
    def __init__(self):
        pass

    def process_batch(
        self, batch: t.Sequence[np.ndarray]
    ) -> t.Sequence[np.ndarray]:
        """
        Sequential processing (no batch processing) using methods of the
        traditional machine vision.
        Courtesy of (https://stackoverflow.com/questions/49946528/
        how-to-extract-a-specific-section-of-an-image-using-opencv-in-python)
        """
        return [SegmenterV1.process_frame(frame) for frame in batch]

    @staticmethod
    @timer
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Extra function call is costly - its here to time the algorithm only
        # TODO: Move all hardcoded parameter values to the Config
        """
        image = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        image = cv2.bilateralFilter(image, 9, 105, 105)
        r, g, b = cv2.split(image)
        equalize = cv2.merge((r, g, b))
        equalize = cv2.cvtColor(equalize, cv2.COLOR_RGB2GRAY)
        ret, thresh_image = cv2.threshold(
            equalize, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY
        )
        equalize = cv2.equalizeHist(thresh_image)
        canny_image = cv2.Canny(equalize, 250, 255)
        canny_image = cv2.convertScaleAbs(canny_image)
        kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv2.dilate(canny_image, kernel, iterations=1)
        contours, hierarchy = cv2.findContours(
            dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        c = contours[0]
        mask = np.zeros(frame.shape, np.uint8)
        cv2.drawContours(
            mask,
            [c],
            0,
            255,
            -1,
        )
        new_image = cv2.bitwise_and(frame, frame, mask=equalize)
        return new_image
