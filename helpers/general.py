import os

from pydantic import BaseModel
from pydantic import validator


class RuntimeArgsValidator(BaseModel):
    path_to_video: str
    destination: str

    @validator("path_to_video")
    def _video_file_exists(cls, path_to_video: str) -> str:
        if not os.path.exists(path_to_video):
            raise FileNotFoundError(
                f"Failed to locate the video: {path_to_video}"
            )
        return path_to_video

    @validator("destination")
    def _check_resolution(cls, destination: str) -> str:
        if not os.path.exists(destination):
            try:
                os.mkdir(destination)
            except Exception as e:
                print(f"Failed to create the destination folder. Error: {e}")
                raise e
        return destination
