import argparse

from pydantic import ValidationError

from config import Config
from detector import Detector
from helpers import Logger
from helpers import RuntimeArgsValidator
from segmenter import SegmenterV1


logger = Logger(__file__, verbose=Config.VERBOSE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_to_video", type=str)
    parser.add_argument("-d", "--destination", type=str)
    parser.add_argument("--show_progress", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        RuntimeArgsValidator(**(vars(args)))
    except ValidationError as e:
        logger.exception(f"Incorrect arguments provided. Errors: {e}")
        raise e
    else:
        logger.info("Arguments verified")

    # At this point we could pick any segmentation algorithm provided that
    # it implements the AbstractSegmenter interface that Detector relies on
    segmenter = SegmenterV1()
    detector = Detector(segmenter=segmenter, destination=args.destination)
    detector.start()

    # Submit video for processing. If successful, we get its ID, which we could
    # potentially use to check the progress
    is_accepted, _id, err = detector.process_video(args.path_to_video)
    if is_accepted:
        logger.info(f"Video has been accepted for processing. Its ID: {_id}")
    else:
        logger.error(
            f"Video {args.path_to_video} was not accepted for processing. "
            f"Error: {err}"
        )
        detector.stop()

    # TODO: Unexpected behaviour - needs fixing
    while True:
        if detector.is_processing_finished():
            break
        if args.show_progress:
            err, info = detector.get_video_progress(_id)
            if err:
                logger.error(err)
            else:
                logger.info(f"Processed {info[0]} / {info[1]} frames")

    detector.stop()
    return 0


if __name__ == "__main__":
    main()
