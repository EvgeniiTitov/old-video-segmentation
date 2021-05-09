import argparse
import os
import typing as t

from pydantic import ValidationError

from config import Config
from detector import Detector
from helpers import Logger
from helpers import RuntimeArgsValidator
from segmenter import SegmenterV1
from segmenter import SegmenterV2


logger = Logger(__file__, verbose=Config.VERBOSE)


def parse_args() -> t.MutableMapping[str, t.Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_to_video", type=str)
    parser.add_argument("-d", "--destination", type=str)
    return vars(parser.parse_args())


def main() -> int:
    args = parse_args()
    if not args["destination"]:
        args["destination"] = os.path.split(args["path_to_video"])[0]
    try:
        RuntimeArgsValidator(**args)
    except ValidationError as e:
        logger.exception(f"Incorrect arguments provided. Errors: {e}")
        raise e
    else:
        logger.info("Arguments verified")

    # At this point we could pick any segmentation algorithm available provided
    # that it implements the AbstractSegmenter interface that Detector uses
    segmenter = SegmenterV1() if Config.SEGMENT_VERSION == 1 else SegmenterV2()
    logger.info(f"Using segmenter of the version: {Config.SEGMENT_VERSION}")
    detector = Detector(segmenter=segmenter, destination=args["destination"])
    detector.start()

    # Submit video for processing. If successful, we get its ID, which we could
    # potentially use to check the progress
    is_accepted, _id, err = detector.process_video(args["path_to_video"])
    if is_accepted:
        logger.info(f"Video has been accepted for processing. Its ID: {_id}")
    else:
        logger.error(
            f"Video {args['path_to_video']} was not accepted for processing. "
            f"Error: {err}"
        )
        detector.stop()

    while True:
        if detector.is_processing_finished():
            break

    detector.stop()
    return 0


if __name__ == "__main__":
    main()
