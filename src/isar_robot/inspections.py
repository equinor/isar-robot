import os
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

from robot_interface.models.exceptions.robot_exceptions import (
    RobotRetrieveInspectionException,
)
from robot_interface.models.inspection.inspection import (
    Audio,
    AudioMetadata,
    Image,
    ImageMetadata,
    ThermalVideo,
    ThermalVideoMetadata,
    Video,
    VideoMetadata,
    GasMeasurement,
    GasMeasurementMetadata,
)
from robot_interface.models.mission.task import (
    RecordAudio,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
    TakeVideo,
    TakeGasMeasurement,
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


def create_image(task_actions: Union[TakeImage, TakeThermalImage]) -> Image:
    now: datetime = datetime.now(timezone.utc)
    image_metadata: ImageMetadata = ImageMetadata(
        start_time=now,
        pose=telemetry.get_pose(),
        file_type="jpg",
    )
    image_metadata.tag_id = task_actions.tag_id
    image_metadata.analysis_type = ["test1", "test2"]
    image_metadata.additional = task_actions.metadata

    filepath: Path = random.choice(list(example_images.iterdir()))
    data = _read_data_from_file(filepath)

    return Image(metadata=image_metadata, id=task_actions.inspection_id, data=data)


def create_video(task_actions: TakeVideo) -> Video:
    now: datetime = datetime.now(timezone.utc)
    video_metadata: VideoMetadata = VideoMetadata(
        start_time=now,
        pose=telemetry.get_pose(),
        file_type="mp4",
        duration=11,
    )
    video_metadata.tag_id = task_actions.tag_id
    video_metadata.analysis_type = ["test1", "test2"]
    video_metadata.additional = task_actions.metadata

    filepath: Path = random.choice(list(example_videos.iterdir()))
    data = _read_data_from_file(filepath)

    return Video(metadata=video_metadata, id=task_actions.inspection_id, data=data)


def create_thermal_video(task_actions: TakeThermalVideo):
    now: datetime = datetime.now(timezone.utc)
    thermal_video_metadata: ThermalVideoMetadata = ThermalVideoMetadata(
        start_time=now,
        pose=telemetry.get_pose(),
        file_type="mp4",
        duration=task_actions.duration,
    )
    thermal_video_metadata.tag_id = task_actions.tag_id
    thermal_video_metadata.analysis_type = ["test1", "test2"]
    thermal_video_metadata.additional = task_actions.metadata

    filepath: Path = random.choice(list(example_thermal_videos.iterdir()))
    data = _read_data_from_file(filepath)

    return ThermalVideo(
        metadata=thermal_video_metadata, id=task_actions.inspection_id, data=data
    )


def create_audio(task_actions: RecordAudio):
    now: datetime = datetime.now(timezone.utc)
    audio_metadata: AudioMetadata = AudioMetadata(
        start_time=now,
        pose=telemetry.get_pose(),
        file_type="wav",
        duration=task_actions.duration,
    )
    audio_metadata.tag_id = task_actions.tag_id
    audio_metadata.analysis_type = ["test1", "test2"]
    audio_metadata.additional = task_actions.metadata

    filepath: Path = random.choice(list(example_thermal_videos.iterdir()))
    data = _read_data_from_file(filepath)

    return Audio(metadata=audio_metadata, id=task_actions.inspection_id, data=data)


def create_gas_measurement(task_actions: TakeGasMeasurement):
    now: datetime = datetime.now(timezone.utc)
    gas_measurement_metadata: GasMeasurementMetadata = GasMeasurementMetadata(
        start_time=now,
        pose=telemetry.get_pose(),
        file_type="wav",
    )
    gas_measurement_metadata.tag_id = task_actions.tag_id
    gas_measurement_metadata.analysis_type = ["test1", "test2"]
    gas_measurement_metadata.additional = task_actions.metadata

    filepath: Path = random.choice(list(example_thermal_videos.iterdir()))
    data = _read_data_from_file(filepath)

    return GasMeasurement(
        metadata=gas_measurement_metadata, id=task_actions.inspection_id, data=data
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
