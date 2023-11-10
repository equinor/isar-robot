import os
import random
from datetime import datetime
from pathlib import Path
from typing import Union

from robot_interface.models.exceptions.robot_exceptions import (
    RobotRetrieveInspectionException,
)
from robot_interface.models.inspection import Audio, ThermalVideo, ThermalVideoMetadata
from robot_interface.models.inspection.inspection import (
    AudioMetadata,
    Image,
    ImageMetadata,
    Video,
    VideoMetadata,
)
from robot_interface.models.mission.step import (
    RecordAudio,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
    TakeVideo,
)

from isar_robot import telemetry

example_images: Path = Path(
    os.path.dirname(os.path.realpath(__file__)), "example_data/example_images"
)
example_videos: Path = Path(
    os.path.dirname(os.path.realpath(__file__)), "example_data/example_videos"
)
example_thermal_videos: Path = Path(
    os.path.dirname(os.path.realpath(__file__)),
    "example_data/example_thermal_videos",
)
example_audio: Path = Path(
    os.path.dirname(os.path.realpath(__file__)), "example_data/example_audio"
)


def create_image(step: Union[TakeImage, TakeThermalImage]):
    now: datetime = datetime.utcnow()
    image_metadata: ImageMetadata = ImageMetadata(
        start_time=now,
        pose=telemetry.get_pose(),
        file_type="jpg",
    )
    image_metadata.tag_id = step.tag_id
    image_metadata.analysis_type = ["test1", "test2"]
    image_metadata.additional = step.metadata

    image: Image = Image(metadata=image_metadata)

    filepath: Path = random.choice(list(example_images.iterdir()))
    image.data = _read_data_from_file(filepath)

    return [image]


def create_video(step: TakeVideo):
    now: datetime = datetime.utcnow()
    video_metadata: VideoMetadata = VideoMetadata(
        start_time=now,
        pose=telemetry.get_pose(),
        file_type="mp4",
        duration=11,
    )
    video_metadata.tag_id = step.tag_id
    video_metadata.analysis_type = ["test1", "test2"]
    video_metadata.additional = step.metadata

    video: Video = Video(metadata=video_metadata)

    filepath: Path = random.choice(list(example_videos.iterdir()))
    video.data = _read_data_from_file(filepath)

    return [video]


def create_thermal_video(step: TakeThermalVideo):
    now: datetime = datetime.utcnow()
    thermal_video_metadata: ThermalVideoMetadata = ThermalVideoMetadata(
        start_time=now,
        pose=telemetry.get_pose(),
        file_type="mp4",
        duration=step.duration,
    )
    thermal_video_metadata.tag_id = step.tag_id
    thermal_video_metadata.analysis_type = ["test1", "test2"]
    thermal_video_metadata.additional = step.metadata

    thermal_video: ThermalVideo = ThermalVideo(metadata=thermal_video_metadata)

    filepath: Path = random.choice(list(example_thermal_videos.iterdir()))
    thermal_video.data = _read_data_from_file(filepath)

    return [thermal_video]


def create_audio(step: RecordAudio):
    now: datetime = datetime.utcnow()
    audio_metadata: AudioMetadata = AudioMetadata(
        start_time=now,
        pose=telemetry.get_pose(),
        file_type="wav",
        duration=step.duration,
    )
    audio_metadata.tag_id = step.tag_id
    audio_metadata.analysis_type = ["test1", "test2"]
    audio_metadata.additional = step.metadata

    audio: Audio = Audio(metadata=audio_metadata)

    filepath: Path = random.choice(list(example_thermal_videos.iterdir()))
    audio.data = _read_data_from_file(filepath)

    return [audio]


def _read_data_from_file(filename: Path) -> bytes:
    try:
        with open(filename, "rb") as f:
            data: bytes = f.read()
    except FileNotFoundError as e:
        raise RobotRetrieveInspectionException(
            "An error occurred while retrieving the inspection data"
        )
    return data
