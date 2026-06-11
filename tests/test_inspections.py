from alitra import Frame, Orientation, Pose, Position
from robot_interface.models.mission.task import (
    AcousticDetectionType,
    RecordAudio,
    TakeAcousticMeasurement,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
)

from isar_robot import inspections, telemetry

robot_pose = Pose(
    Position(0, 0, 0, Frame("asset")),
    Orientation(x=0, y=0, z=0, w=1, frame=Frame("asset")),
    Frame("asset"),
)
target = Position(x=0, y=0, z=0, frame=Frame("robot"))
telemetryModule = telemetry.Telemetry()


def test_create_image() -> None:
    task_actions = TakeImage(target=target, robot_pose=robot_pose)

    inspection_image = inspections.create_image(task_actions, telemetryModule)

    assert inspection_image.metadata.file_type == "jpg"


def test_create_thermal_image() -> None:
    task_actions = TakeThermalImage(target=target, robot_pose=robot_pose)

    inspection_image = inspections.create_thermal_image(task_actions, telemetryModule)

    assert inspection_image.metadata.file_type == "fff"


def test_create_video() -> None:
    task_actions = TakeImage(target=target, robot_pose=robot_pose)

    inspection_video = inspections.create_video(task_actions, telemetryModule)

    assert inspection_video.metadata.file_type == "mp4"


def test_create_thermal_video() -> None:
    task_actions = TakeThermalVideo(target=target, duration=10, robot_pose=robot_pose)

    inspection_video = inspections.create_thermal_video(task_actions, telemetryModule)

    assert inspection_video.metadata.file_type == "mp4"
    assert inspection_video.metadata.duration == 10


def test_create_audio() -> None:
    task_actions = RecordAudio(target=target, duration=10, robot_pose=robot_pose)

    inspection_recording = inspections.create_audio(task_actions, telemetryModule)

    assert inspection_recording.metadata.file_type == "wav"
    assert inspection_recording.metadata.duration == 10


def test_create_acoustic_measurement() -> None:
    task_actions = TakeAcousticMeasurement(
        target=target,
        robot_pose=robot_pose,
        frequency_from=35000,
        frequency_to=40000,
        snr_value_threshold=10,
        detection_type=AcousticDetectionType.leak,
    )

    inspection = inspections.create_acoustic_measurement(task_actions, telemetryModule)

    assert inspection.metadata.file_type == "mp4"
    assert inspection.metadata.frequency_from == 35000


def test_select_image_filepath_cloe_kaa(monkeypatch) -> None:
    monkeypatch.setattr(inspections.settings, "PLANT_SHORT_NAME", "kaa")
    task = TakeImage(target=target, robot_pose=robot_pose, analysis_types=["CLOE"])

    assert (
        inspections._select_image_filepath(task) == inspections.example_cloe_image_kaa
    )


def test_select_image_filepath_fencilla(monkeypatch) -> None:
    monkeypatch.setattr(inspections.settings, "PLANT_SHORT_NAME", "nls")
    task = TakeImage(target=target, robot_pose=robot_pose, analysis_types=["Fencilla"])

    assert (
        inspections._select_image_filepath(task) == inspections.example_fencilla_image
    )
