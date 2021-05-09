import threading
import typing as t
from queue import Queue

import cv2
import numpy as np

from helpers import LoggerMixin


class FrameReaderThread(threading.Thread, LoggerMixin):
    def __init__(
        self,
        progress: t.MutableMapping[str, t.Any],
        queue_in: Queue,
        queue_out: Queue,
        batch_size: int,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._progress = progress
        self._queue_in = queue_in
        self._queue_out = queue_out
        self._batch_size = batch_size
        self.logger.debug("FrameReader worker initialized")

    def run(self) -> None:
        while True:
            item = self._queue_in.get()
            if item == "STOP":
                self.logger.debug("FrameReader worker stopped")
                self._queue_out.put("STOP")
                break
            else:
                self.logger.debug(f"Started decoding video {item}")

            video_id = item
            if video_id not in self._progress:
                self.logger.error(
                    f"Unknown ID {video_id}, it wasn't accepted for processing"
                )

            path_to_video = self._progress[video_id]["path_to_video"]
            try:
                cap = cv2.VideoCapture(path_to_video)
            except Exception as e:
                self.logger.exception(
                    f"Failed to open the video {item}. Error: {e}. Skipping"
                )
                continue

            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            total_seconds = total_frames // fps
            self._progress[video_id]["frame_width"] = frame_width
            self._progress[video_id]["frame_height"] = frame_height
            self._progress[video_id]["fps"] = fps
            self._progress[video_id]["total_frames"] = total_frames
            self._progress[video_id]["total_seconds"] = total_seconds
            self._progress[video_id]["status"] = "Processing"

            batch: t.List[np.ndarray] = []
            to_break = False
            while True:
                if len(batch) < self._batch_size:
                    has_frame, frame = cap.read()
                    if not has_frame:
                        to_break = True
                    else:
                        batch.append(frame)
                        continue
                if len(batch):
                    self._queue_out.put((video_id, batch))
                    batch = []
                if to_break:
                    break

            cap.release()
            # Signal the video has ended, start decoding the next one
            self._queue_out.put("END")
            self.logger.debug(f"Video {item} completely decoded")
