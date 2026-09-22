import logging
import os
import random
from datetime import UTC, datetime
from pathlib import Path

from robot_interface.models.exceptions.robot_exceptions import (
    RobotRetrieveInspectionException,
)
from robot_interface.models.inspection.inspection import (
    AcousticMeasurement,
    AcousticMeasurementMetadata,
    Audio,
    AudioMetadata,
    CO2Measurement,
    GasMeasurementMetadata,
    Image,
    ImageMetadata,
    ThermalImage,
    ThermalImageMetadata,
    ThermalVideo,
    ThermalVideoMetadata,
    Video,
    VideoMetadata,
)
from robot_interface.models.mission.task import (
    InspectionTask,
    RecordAudio,
    TakeAcousticMeasurement,
    TakeCO2Measurement,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
    TakeVideo,
)

from isar_robot.telemetry import Telemetry

EXAMPLE_DATA_DIR: Path = Path(
    os.path.dirname(os.path.realpath(__file__)), "example_data"
)


def _example_data_path(filename: str) -> Path:
    return Path(EXAMPLE_DATA_DIR, filename)


example_cloe_image_nls: Path = _example_data_path("example_image_cloe_nls.jpeg")
example_cloe_image_nls_empty: Path = _example_data_path(
    "example_image_cloe_nls_empty.jpeg"
)
example_fencilla_image: Path = _example_data_path("example_image_fencilla.jpeg")
example_fencilla_hole_image: Path = _example_data_path(
    "example_image_fencilla_hole.jpeg"
)
example_fencilla_rain_drops_image: Path = _example_data_path(
    "example_image_fencilla_rain_drops.jpeg"
)
example_thermal_image: Path = _example_data_path("example_thermal_image.fff")
example_video: Path = _example_data_path("example_video.mp4")
example_thermal_video: Path = _example_data_path("example_thermal_video.mp4")
example_audio: Path = _example_data_path("example_audio.wav")

# Not checked in yet; falls back until the file is added to example_data/.
example_cloe_image_low: Path = _example_data_path("example_image_cloe_low.jpeg")
example_cloe_image_rain_drops: Path = _example_data_path(
    "example_image_cloe_rain_drops.jpeg"
)
example_thermal_image_hot_spot: Path = _example_data_path(
    "example_thermal_image_hot_spot.fff"
)

# SARA keys alarm identity partly on the tag id, so a tag must always yield the
# same image. Entries are (intended, fallback while the intended file is absent).
TAG_ID_TO_IMAGE: dict[str, tuple[Path, Path]] = {
    "cloe-empty": (example_cloe_image_nls_empty, example_cloe_image_nls_empty),
    "cloe-low": (example_cloe_image_low, example_cloe_image_nls_empty),
    "cloe-normal": (example_cloe_image_nls, example_cloe_image_nls),
    "cloe-rain-drops": (example_cloe_image_rain_drops, example_cloe_image_nls),
    "fence-intact": (example_fencilla_image, example_fencilla_image),
    "fence-hole": (example_fencilla_hole_image, example_fencilla_hole_image),
    "fence-rain-drops": (
        example_fencilla_rain_drops_image,
        example_fencilla_rain_drops_image,
    ),
}

TAG_ID_TO_THERMAL_IMAGE: dict[str, tuple[Path, Path]] = {
    "thermal-normal": (example_thermal_image, example_thermal_image),
    "thermal-hot-spot": (example_thermal_image_hot_spot, example_thermal_image),
}

logger = logging.getLogger(__name__)


def create_image(task: TakeImage, telemetry: Telemetry) -> Image:
    now: datetime = datetime.now(UTC)

    image_metadata: ImageMetadata = ImageMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task, telemetry),
        file_type="jpg",
    )
    image_metadata.tag_id = task.tag_id
    image_metadata.inspection_description = task.inspection_description

    filepath: Path = _select_image_filepath(task)
    data = _read_data_from_file(filepath)

    return Image(metadata=image_metadata, id=task.id, data=data)


def create_thermal_image(task: TakeThermalImage, telemetry: Telemetry) -> Image:
    now: datetime = datetime.now(UTC)

    image_metadata: ThermalImageMetadata = ThermalImageMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task, telemetry),
        file_type="fff",
    )
    image_metadata.tag_id = task.tag_id
    image_metadata.inspection_description = task.inspection_description

    filepath: Path = _select_thermal_image_filepath(task)
    data = _read_data_from_file(filepath)

    return ThermalImage(metadata=image_metadata, id=task.id, data=data)


def create_video(task: TakeVideo, telemetry: Telemetry) -> Video:
    now: datetime = datetime.now(UTC)
    video_metadata: VideoMetadata = VideoMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task, telemetry),
        file_type="mp4",
        duration=11,
    )
    video_metadata.tag_id = task.tag_id
    video_metadata.inspection_description = task.inspection_description

    filepath: Path = example_video
    data = _read_data_from_file(filepath)

    return Video(metadata=video_metadata, id=task.id, data=data)


def create_thermal_video(task: TakeThermalVideo, telemetry: Telemetry):
    now: datetime = datetime.now(UTC)
    thermal_video_metadata: ThermalVideoMetadata = ThermalVideoMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task, telemetry),
        file_type="mp4",
        duration=task.duration,
    )
    thermal_video_metadata.tag_id = task.tag_id
    thermal_video_metadata.inspection_description = task.inspection_description

    filepath: Path = example_thermal_video
    data = _read_data_from_file(filepath)

    return ThermalVideo(metadata=thermal_video_metadata, id=task.id, data=data)


def create_audio(task: RecordAudio, telemetry: Telemetry):
    now: datetime = datetime.now(UTC)
    audio_metadata: AudioMetadata = AudioMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task, telemetry),
        file_type="wav",
        duration=task.duration,
    )
    audio_metadata.tag_id = task.tag_id
    audio_metadata.inspection_description = task.inspection_description

    filepath: Path = example_audio
    data = _read_data_from_file(filepath)

    return Audio(metadata=audio_metadata, id=task.id, data=data)


def create_co2_measurement(task: TakeCO2Measurement, telemetry: Telemetry):
    now: datetime = datetime.now(UTC)
    gas_measurement_metadata: GasMeasurementMetadata = GasMeasurementMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task, telemetry),
        file_type="not_a_file",
    )
    gas_measurement_metadata.tag_id = task.tag_id
    gas_measurement_metadata.inspection_description = task.inspection_description

    return CO2Measurement(
        metadata=gas_measurement_metadata,
        id=task.id,
        value=random.normalvariate(0.043, 0.005),
        unit="% v/v",
    )


def create_acoustic_measurement(
    task: TakeAcousticMeasurement, telemetry: Telemetry
) -> AcousticMeasurement:
    now: datetime = datetime.now(UTC)
    metadata: AcousticMeasurementMetadata = AcousticMeasurementMetadata(
        start_time=now,
        robot_pose=telemetry.get_pose(),
        target_position=_get_target_position(task, telemetry),
        file_type="mp4",
        duration=11.0,
        snr_value=0.0,
        leak_rate=0.0,
        leak_rate_unit="l/min",
        sound_pressure_level_at_sensor_db=40.0,
        sound_pressure_level_at_source_db=45.0,
        distance_to_source=2.0,
        result="RI_NO_ANOMALY",
        frequency_from=task.frequency_from,
        frequency_to=task.frequency_to,
    )
    metadata.tag_id = task.tag_id
    metadata.inspection_description = task.inspection_description

    data = _read_data_from_file(example_video)

    return AcousticMeasurement(metadata=metadata, id=task.id, data=data)


def _select_image_filepath(task: TakeImage) -> Path:
    filepath: Path | None = _resolve_tagged_fixture(task.tag_id, TAG_ID_TO_IMAGE)
    if filepath is not None:
        return filepath

    analysis_types = [
        analysis_type.lower() for analysis_type in (task.analysis_types or [])
    ]

    if "cloe" in analysis_types:
        return example_cloe_image_nls
    if "fencilla" in analysis_types:
        return example_fencilla_image

    return example_cloe_image_nls


def _select_thermal_image_filepath(task: TakeThermalImage) -> Path:
    filepath: Path | None = _resolve_tagged_fixture(
        task.tag_id, TAG_ID_TO_THERMAL_IMAGE
    )
    if filepath is not None:
        return filepath

    return example_thermal_image


def _resolve_tagged_fixture(
    tag_id: str | None, mapping: dict[str, tuple[Path, Path]]
) -> Path | None:
    if tag_id is None:
        return None

    entry = mapping.get(tag_id)
    if entry is None:
        return None

    intended, fallback = entry
    if intended.is_file():
        return intended

    logger.warning(
        "Fixture '%s' for tag id '%s' is missing. Place the file in '%s' to use it. "
        "Falling back to '%s'.",
        intended.name,
        tag_id,
        EXAMPLE_DATA_DIR,
        fallback.name,
    )
    return fallback


def _read_data_from_file(filename: Path) -> bytes:
    try:
        with open(filename, "rb") as f:
            data: bytes = f.read()
    except FileNotFoundError:
        raise RobotRetrieveInspectionException(
            "An error occurred while retrieving the inspection data"
        )
    return data


def _get_target_position(task: InspectionTask, telemetry: Telemetry):
    try:
        target_position = task.target
    except AttributeError:
        logger.debug("No inspection target specified, using robot position instead")
        target_position = telemetry.get_pose().position

    return target_position
