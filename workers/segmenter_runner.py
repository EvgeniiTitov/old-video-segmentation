import threading
import typing as t
from queue import Queue

from helpers import LoggerMixin
from segmenter import AbstractSegmenter


class SegmenterRunnerThread(threading.Thread, LoggerMixin):
    def __init__(
        self,
        progress: t.Mapping[str, t.Any],
        segmenter: AbstractSegmenter,
        queue_in: Queue,
        queue_out: Queue,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._progress = progress
        self._segmenter = segmenter
        self._queue_in = queue_in
        self._queue_out = queue_out
        self.logger.debug("SegmenterRunner worker initialized")

    def run(self) -> None:
        while True:
            item = self._queue_in.get()
            if item == "STOP":
                self.logger.debug("SegmenterRunner worker stopped")
                self._queue_out.put("STOP")
                break
            elif item == "END":
                self._queue_out.put("END")
                continue

            video_id, batch = item
            masks = self._segmenter.process_batch(batch)
            self._queue_out.put((video_id, batch, masks))
