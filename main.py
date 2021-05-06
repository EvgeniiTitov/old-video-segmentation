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
    parser.add_argument("--destination", type=str)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        RuntimeArgsValidator(**(vars(args)))
    except ValidationError as e:
        logger.exception(f"Incorrect arguments provided. Errors: {e}")
        raise e
    detector = Detector(segmenter=SegmenterV1(), destination=args.destination)
    success, _id = detector.process_video(args.path_to_video)
    if success:
        logger.info(f"Video has been accepted for processing. Its ID: {_id}")
    return 0


if __name__ == "__main__":
    main()
