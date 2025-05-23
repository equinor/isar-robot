import logging
import os
import random
from datetime import datetime, timezone
from logging import Logger
from pathlib import Path
from typing import Union

from robot_interface.models.exceptions.robot_exceptions import (
    RobotRetrieveInspectionException,
)
from robot_interface.models.inspection.inspection import (
    Audio,
    AudioMetadata,
    CO2Measurement,
    GasMeasurementMetadata,
    Image,
    ImageMetadata,
    ThermalVideo,
    ThermalVideoMetadata,
    Video,
    VideoMetadata,
)
from robot_interface.models.mission.task import (
    InspectionTask,
    RecordAudio,
    TakeCO2Measurement,
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

logger: Logger = logging.getLogger("isar_robot")


def create_image(task: Union[TakeImage, TakeThermalImage]) -> Image:
    now: datetime = datetime.now(timezone.utc)

    image_metadata: ImageMetadata = ImageMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task),
        file_type="jpg",
    )
    image_metadata.tag_id = task.tag_id
    image_metadata.inspection_description = task.inspection_description

    filepath: Path = random.choice(list(example_images.iterdir()))
    data = _read_data_from_file(filepath)

    return Image(metadata=image_metadata, id=task.inspection_id, data=data)


def create_video(task: TakeVideo) -> Video:
    now: datetime = datetime.now(timezone.utc)
    video_metadata: VideoMetadata = VideoMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task),
        file_type="mp4",
        duration=11,
    )
    video_metadata.tag_id = task.tag_id
    video_metadata.inspection_description = task.inspection_description

    filepath: Path = random.choice(list(example_videos.iterdir()))
    data = _read_data_from_file(filepath)

    return Video(metadata=video_metadata, id=task.inspection_id, data=data)


def create_thermal_video(task: TakeThermalVideo):
    now: datetime = datetime.now(timezone.utc)
    thermal_video_metadata: ThermalVideoMetadata = ThermalVideoMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task),
        file_type="mp4",
        duration=task.duration,
    )
    thermal_video_metadata.tag_id = task.tag_id
    thermal_video_metadata.inspection_description = task.inspection_description

    filepath: Path = random.choice(list(example_thermal_videos.iterdir()))
    data = _read_data_from_file(filepath)

    return ThermalVideo(
        metadata=thermal_video_metadata, id=task.inspection_id, data=data
    )


def create_audio(task: RecordAudio):
    now: datetime = datetime.now(timezone.utc)
    audio_metadata: AudioMetadata = AudioMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task),
        file_type="wav",
        duration=task.duration,
    )
    audio_metadata.tag_id = task.tag_id
    audio_metadata.inspection_description = task.inspection_description

    filepath: Path = random.choice(list(example_thermal_videos.iterdir()))
    data = _read_data_from_file(filepath)

    return Audio(metadata=audio_metadata, id=task.inspection_id, data=data)


def create_co2_measurement(task: TakeCO2Measurement):
    now: datetime = datetime.now(timezone.utc)
    gas_measurement_metadata: GasMeasurementMetadata = GasMeasurementMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task),
        file_type="not_a_file",
    )
    gas_measurement_metadata.tag_id = task.tag_id
    gas_measurement_metadata.inspection_description = task.inspection_description

    return CO2Measurement(
        metadata=gas_measurement_metadata,
        id=task.inspection_id,
        value=random.uniform(0, 5),
        unit="% v/v",
    )


def _read_data_from_file(filename: Path) -> bytes:
    try:
        with open(filename, "rb") as f:
            data: bytes = f.read()
    except FileNotFoundError:
        raise RobotRetrieveInspectionException(
            "An error occurred while retrieving the inspection data"
        )
    return data


def _get_target_position(task: InspectionTask):
    try:
        target_position = task.target
    except AttributeError:
        logger.debug("No inspection target specified, using robot position instead")
        target_position = telemetry.get_pose().position

    return target_position
