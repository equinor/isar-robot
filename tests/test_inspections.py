from alitra import Frame, Position, Pose, Orientation
from robot_interface.models.mission.task import (
    RecordAudio,
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
