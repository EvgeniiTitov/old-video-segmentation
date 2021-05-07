import os
import threading
import typing as t
from queue import Queue

import cv2

from helpers import LoggerMixin


class ResultProcessorThread(threading.Thread, LoggerMixin):
    ID_MEMORY_CAPACITY = 20

    def __init__(
        self,
        progress: t.MutableMapping[str, t.Any],
        queue_in: Queue,
        destination: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._progress = progress
        self._queue_in = queue_in
        self._destination = destination
        self._video_writer = None
        self._previous_id = None
        self.logger.debug("ResultProcessor worker initialized")

    def run(self) -> None:
        while True:
            item = self._queue_in.get()
            if item == "STOP":
                self.logger.debug("ResultProcessor worker stopped")
                break
            elif item == "END":
                if self._previous_id:
                    self._delete_video_writer()
                continue

            video_id, batch, masks = item
            video_name = os.path.splitext(
                os.path.basename(self._progress[video_id]["path_to_video"])
            )[0]
            if self._previous_id != video_id:
                self._previous_id = video_id

            if not self._video_writer:
                # TODO: Replace with ".mp4"
                out_path = os.path.join(
                    self._destination, video_name + "_processed.avi"
                )
                fps = self._progress[video_id]["fps"]
                height = self._progress[video_id]["frame_height"]
                width = self._progress[video_id]["frame_width"]
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                try:
                    self._video_writer = cv2.VideoWriter(
                        out_path, fourcc, fps, (width, height), True
                    )
                except Exception as e:
                    # TODO: This will kill the last thread, but others working!
                    self.logger.exception(
                        f"Failed to create a video writer for video: "
                        f"{video_name}. Error: {e}"
                    )
                    raise e

            # Save masks on disk, update the progress
            for mask in masks:
                self._video_writer.write(mask)  # type: ignore
            self._progress[video_id]["processed_frames"] += len(masks)
            self.logger.debug("Saved batch of disk")
            if (
                self._progress[video_id]["processed_frames"]
                >= self._progress[video_id]["total_frames"]
            ):
                self._progress[video_id]["status"] = "Processed"
                self.logger.debug(f"Processing of {video_name} complete")
                # Delete oldest entries to progress dictionary to free memory
                if (
                    len(self._progress)
                    > ResultProcessorThread.ID_MEMORY_CAPACITY
                ):
                    self._progress.pop(next(iter(self._progress)))

    def _delete_video_writer(self) -> None:
        self._video_writer = None
