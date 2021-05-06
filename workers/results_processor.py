import threading
import typing as t
from queue import Queue

from helpers import LoggerMixin


class ResultProcessorThread(threading.Thread, LoggerMixin):
    def __init__(
        self,
        progress: t.Mapping[str, t.Any],
        queue_in: Queue,
        destination: str,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._progress = progress
        self._queue_in = queue_in
        self._destination = destination
        self.logger.debug("ResultProcessor worker initialized")

    def run(self) -> None:
        pass
