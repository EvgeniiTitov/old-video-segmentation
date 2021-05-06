import os
import typing as t
import uuid
from queue import Queue

from config import Config
from helpers import LoggerMixin
from segmenter import AbstractSegmenter
from workers import FrameReaderThread
from workers import ResultProcessorThread
from workers import SegmenterRunner


class Detector(LoggerMixin):
    def __init__(self, segmenter: AbstractSegmenter, destination: str) -> None:
        self.logger.debug("Detector initialized")
        self._progress: t.MutableMapping[str, t.Any] = dict()
        self._threads = []

        self._Q_files_to_process: Queue = Queue()
        self._Q_reader_to_runner: Queue = Queue(Config.READER_RUNNER_Q_SIZE)
        self._Q_runner_to_writer: Queue = Queue(Config.RUNNER_TO_WRITER_Q_SIZE)
        self.logger.debug("Detector queues initialized")

        self._frames_reader = FrameReaderThread(
            progress=self._progress,
            queue_in=self._Q_files_to_process,
            queue_out=self._Q_reader_to_runner,
            batch_size=Config.BATCH_SIZE,
        )
        self._threads.append(self._frames_reader)

        # The segmentation algorithm could be easily swapped at this point
        self._segmenter_runner = SegmenterRunner(
            progress=self._progress,
            segmenter=segmenter,
            queue_in=self._Q_reader_to_runner,
            queue_out=self._Q_runner_to_writer,
        )
        self._threads.append(self._segmenter_runner)  # type: ignore

        self._writer = ResultProcessorThread(
            progress=self._progress,
            queue_in=self._Q_runner_to_writer,
            destination=destination,
        )
        self._threads.append(self._writer)  # type: ignore
        self._start()
        self.logger.debug("Detector started")

    def process_video(self, path_to_video: str) -> t.Tuple[bool, str]:
        """Receives path to a video to process. Create a unique ID for the
        video, adds it to the global progress dictionary and returns the
        result: whether the video has been accepted for processing or not, and
        its id
        """
        self.logger.debug(f"Accepted video {path_to_video} for processing")
        if (
            not os.path.splitext(path_to_video)[0].lower()
            in Config.ALLOWED_EXTS
        ):
            self.logger.error(
                f"Cannot process video {path_to_video}. Unsupported extension."
            )
            return False, ""
        video_id = str(uuid.uuid4())
        self._progress[video_id] = {
            "status": "Awaiting processing",
            "path_to_video": path_to_video,
            "frame_width": None,
            "frame_height": None,
            "fps": None,
            "total_frames": None,
            "total_seconds": None,
            "processed_frames": 0,
        }
        self._Q_files_to_process.put(video_id)
        return True, video_id

    def _start(self) -> None:
        for thread in self._threads:
            thread.start()

    def stop(self) -> None:
        self._Q_files_to_process.put("STOP")
        for thread in self._threads:
            thread.join()
        self.logger.debug("Detector stopped")
