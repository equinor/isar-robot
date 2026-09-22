import logging

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
    task_actions = TakeImage(id="id", target=target, robot_pose=robot_pose)

    inspection_image = inspections.create_image(task_actions, telemetryModule)

    assert inspection_image.metadata.file_type == "jpg"


def test_create_thermal_image() -> None:
    task_actions = TakeThermalImage(id="id", target=target, robot_pose=robot_pose)

    inspection_image = inspections.create_thermal_image(task_actions, telemetryModule)

    assert inspection_image.metadata.file_type == "fff"


def test_create_video() -> None:
    task_actions = TakeImage(id="id", target=target, robot_pose=robot_pose)

    inspection_video = inspections.create_video(task_actions, telemetryModule)

    assert inspection_video.metadata.file_type == "mp4"


def test_create_thermal_video() -> None:
    task_actions = TakeThermalVideo(
        id="id", target=target, duration=10, robot_pose=robot_pose
    )

    inspection_video = inspections.create_thermal_video(task_actions, telemetryModule)

    assert inspection_video.metadata.file_type == "mp4"
    assert inspection_video.metadata.duration == 10


def test_create_audio() -> None:
    task_actions = RecordAudio(
        id="id", target=target, duration=10, robot_pose=robot_pose
    )

    inspection_recording = inspections.create_audio(task_actions, telemetryModule)

    assert inspection_recording.metadata.file_type == "wav"
    assert inspection_recording.metadata.duration == 10


def test_create_acoustic_measurement() -> None:
    task_actions = TakeAcousticMeasurement(
        id="id",
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


def test_select_image_filepath_is_tag_driven() -> None:
    expected = {
        "cloe-empty": inspections.example_cloe_image_nls_empty,
        "cloe-normal": inspections.example_cloe_image_nls,
        "fence-intact": inspections.example_fencilla_image,
        "fence-hole": inspections.example_fencilla_hole_image,
        "fence-rain-drops": inspections.example_fencilla_rain_drops_image,
    }

    for tag_id, filepath in expected.items():
        task = TakeImage(id="id", target=target, robot_pose=robot_pose, tag_id=tag_id)
        assert inspections._select_image_filepath(task) == filepath


def test_select_image_filepath_is_deterministic() -> None:
    task = TakeImage(
        id="id", target=target, robot_pose=robot_pose, analysis_types=["CLOE"]
    )

    selections = {inspections._select_image_filepath(task) for _ in range(10)}

    assert len(selections) == 1


def test_select_image_filepath_falls_back_when_fixture_missing(
    monkeypatch, tmp_path
) -> None:
    missing = tmp_path / "example_image_cloe_low.jpeg"
    monkeypatch.setattr(
        inspections,
        "TAG_ID_TO_IMAGE",
        {"cloe-low": (missing, inspections.example_cloe_image_nls_empty)},
    )
    task = TakeImage(id="id", target=target, robot_pose=robot_pose, tag_id="cloe-low")

    assert (
        inspections._select_image_filepath(task)
        == inspections.example_cloe_image_nls_empty
    )


def test_missing_fixture_warning_names_expected_file(
    monkeypatch, tmp_path, caplog
) -> None:
    missing = tmp_path / "example_image_cloe_low.jpeg"
    monkeypatch.setattr(
        inspections,
        "TAG_ID_TO_IMAGE",
        {"cloe-low": (missing, inspections.example_cloe_image_nls_empty)},
    )
    task = TakeImage(id="id", target=target, robot_pose=robot_pose, tag_id="cloe-low")

    with caplog.at_level(logging.WARNING, logger=inspections.logger.name):
        inspections._select_image_filepath(task)

    assert "example_image_cloe_low.jpeg" in caplog.text


def test_select_image_filepath_unknown_tag_uses_analysis_type() -> None:
    cloe_task = TakeImage(
        id="id",
        target=target,
        robot_pose=robot_pose,
        tag_id="unknown-tag",
        analysis_types=["CLOE"],
    )
    fencilla_task = TakeImage(
        id="id",
        target=target,
        robot_pose=robot_pose,
        tag_id="unknown-tag",
        analysis_types=["Fencilla"],
    )

    assert (
        inspections._select_image_filepath(cloe_task)
        == inspections.example_cloe_image_nls
    )
    assert (
        inspections._select_image_filepath(fencilla_task)
        == inspections.example_fencilla_image
    )


def test_select_thermal_image_filepath_is_tag_driven() -> None:
    task = TakeThermalImage(
        id="id", target=target, robot_pose=robot_pose, tag_id="thermal-normal"
    )

    assert (
        inspections._select_thermal_image_filepath(task)
        == inspections.example_thermal_image
    )


def test_select_thermal_image_filepath_falls_back_when_fixture_missing(
    monkeypatch, tmp_path
) -> None:
    missing = tmp_path / "example_thermal_image_hot_spot.fff"
    monkeypatch.setattr(
        inspections,
        "TAG_ID_TO_THERMAL_IMAGE",
        {"thermal-hot-spot": (missing, inspections.example_thermal_image)},
    )
    task = TakeThermalImage(
        id="id", target=target, robot_pose=robot_pose, tag_id="thermal-hot-spot"
    )

    assert (
        inspections._select_thermal_image_filepath(task)
        == inspections.example_thermal_image
    )


def test_select_thermal_image_filepath_unknown_tag() -> None:
    task = TakeThermalImage(
        id="id", target=target, robot_pose=robot_pose, tag_id="unknown-tag"
    )

    assert (
        inspections._select_thermal_image_filepath(task)
        == inspections.example_thermal_image
    )
