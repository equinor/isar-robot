from alitra import Frame, Position
from robot_interface.models.mission.task import (
    RecordAudio,
    TakeImage,
    TakeThermalVideo,
)

from isar_robot import inspections

target = Position(x=0, y=0, z=0, frame=Frame("robot"))


def test_create_image():
    task_actions = TakeImage(target=target)

    list_of_images = inspections.create_image(task_actions)

    assert len(list_of_images) == 1

    inspection_image = list_of_images[0]
    assert inspection_image.metadata.file_type == "jpg"


def test_create_video():
    task_actions = TakeImage(target=target)

    list_of_videos = inspections.create_video(task_actions)

    assert len(list_of_videos) == 1

    inspection_video = list_of_videos[0]
    assert inspection_video.metadata.file_type == "mp4"


def test_create_thermal_video():
    task_actions = TakeThermalVideo(target=target, duration=10)

    list_of_thermal_videos = inspections.create_thermal_video(task_actions)

    assert len(list_of_thermal_videos) == 1

    inspection_video = list_of_thermal_videos[0]
    assert inspection_video.metadata.file_type == "mp4"
    assert inspection_video.metadata.duration == 10


def test_create_audio():
    task_actions = RecordAudio(target=target, duration=10)

    list_of_audio_recordings = inspections.create_audio(task_actions)

    assert len(list_of_audio_recordings) == 1

    inspection_recordings = list_of_audio_recordings[0]
    assert inspection_recordings.metadata.file_type == "wav"
    assert inspection_recordings.metadata.duration == 10
