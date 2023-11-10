from alitra import Frame, Position
from robot_interface.models.mission.step import RecordAudio, TakeImage, TakeThermalVideo

from isar_robot import inspections

target = Position(x=0, y=0, z=0, frame=Frame("robot"))


def test_create_image():
    step = TakeImage(target=target)

    list_of_images = inspections.create_image(step)

    assert len(list_of_images) == 1

    inspection_image = list_of_images[0]
    assert inspection_image.metadata.file_type == "jpg"


def test_create_video():
    step = TakeImage(target=target)

    list_of_videos = inspections.create_video(step)

    assert len(list_of_videos) == 1

    inspection_video = list_of_videos[0]
    assert inspection_video.metadata.file_type == "mp4"


def test_create_thermal_video():
    step = TakeThermalVideo(target=target, duration=10)

    list_of_thermal_videos = inspections.create_thermal_video(step)

    assert len(list_of_thermal_videos) == 1

    inspection_video = list_of_thermal_videos[0]
    assert inspection_video.metadata.file_type == "mp4"
    assert inspection_video.metadata.duration == 10


def test_create_audio():
    step = RecordAudio(target=target, duration=10)

    list_of_audio_recordings = inspections.create_audio(step)

    assert len(list_of_audio_recordings) == 1

    inspection_recordings = list_of_audio_recordings[0]
    assert inspection_recordings.metadata.file_type == "wav"
    assert inspection_recordings.metadata.duration == 10
