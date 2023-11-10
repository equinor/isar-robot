import logging
import os
import random
import time
from datetime import datetime
from logging import Logger
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import List, Sequence, Union

from robot_interface.models.initialize import InitializeParams
from robot_interface.models.inspection import Audio, ThermalVideo, ThermalVideoMetadata
from robot_interface.models.inspection.inspection import (
    AudioMetadata,
    Image,
    ImageMetadata,
    Inspection,
    Video,
    VideoMetadata,
)
from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.status import MissionStatus, RobotStatus, StepStatus
from robot_interface.models.mission.step import (
    InspectionStep,
    RecordAudio,
    Step,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
    TakeVideo,
)
from robot_interface.robot_interface import RobotInterface
from robot_interface.telemetry.mqtt_client import MqttTelemetryPublisher

from isar_robot import telemetry

STEP_DURATION_IN_SECONDS = 5


class Robot(RobotInterface):
    def __init__(self) -> None:
        self.logger: Logger = logging.getLogger("robot")

        self.example_images: Path = Path(
            os.path.dirname(os.path.realpath(__file__)), "example_data/example_images"
        )
        self.example_videos: Path = Path(
            os.path.dirname(os.path.realpath(__file__)), "example_data/example_videos"
        )
        self.example_thermal_videos: Path = Path(
            os.path.dirname(os.path.realpath(__file__)),
            "example_data/example_thermal_videos",
        )
        self.example_audio: Path = Path(
            os.path.dirname(os.path.realpath(__file__)), "example_data/example_audio"
        )

    def initiate_mission(self, mission: Mission) -> None:
        time.sleep(STEP_DURATION_IN_SECONDS)

    def mission_status(self) -> MissionStatus:
        return MissionStatus.Successful

    def initiate_step(self, step: Step) -> None:
        time.sleep(STEP_DURATION_IN_SECONDS)

    def step_status(self) -> StepStatus:
        return StepStatus.Successful

    def stop(self) -> None:
        return

    def get_inspections(self, step: InspectionStep) -> Sequence[Inspection]:
        if type(step) in [TakeImage, TakeThermalImage]:
            return self._create_image(step)
        elif type(step) is TakeVideo:
            return self._create_video(step)
        elif type(step) is TakeThermalVideo:
            return self._create_thermal_video(step)
        elif type(step) is RecordAudio:
            return self._create_audio(step)
        else:
            return None

    def initialize(self, params: InitializeParams) -> None:
        return

    def get_telemetry_publishers(
        self, queue: Queue, isar_id: str, robot_name: str
    ) -> List[Thread]:
        publisher_threads: List[Thread] = []

        pose_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=telemetry.get_pose_telemetry,
            topic=f"isar/{isar_id}/pose",
            interval=5,
            retain=False,
        )
        pose_thread: Thread = Thread(
            target=pose_publisher.run,
            args=[isar_id, robot_name],
            name="ISAR Robot Pose Publisher",
            daemon=True,
        )
        publisher_threads.append(pose_thread)

        battery_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=telemetry.get_battery_telemetry,
            topic=f"isar/{isar_id}/battery",
            interval=30,
            retain=False,
        )
        battery_thread: Thread = Thread(
            target=battery_publisher.run,
            args=[isar_id, robot_name],
            name="ISAR Robot Battery Publisher",
            daemon=True,
        )
        publisher_threads.append(battery_thread)

        obstacle_status_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=telemetry.get_obstacle_status_telemetry,
            topic=f"isar/{isar_id}/obstacle_status",
            interval=10,
            retain=False,
        )
        obstacle_status_thread: Thread = Thread(
            target=obstacle_status_publisher.run,
            args=[isar_id, robot_name],
            name="ISAR Robot Obstacle Status Publisher",
            daemon=True,
        )
        publisher_threads.append(obstacle_status_thread)

        pressure_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=telemetry.get_pressure_telemetry,
            topic=f"isar/{isar_id}/pressure",
            interval=20,
            retain=False,
        )
        pressure_thread: Thread = Thread(
            target=pressure_publisher.run,
            args=[isar_id, robot_name],
            name="ISAR Robot Pressure Publisher",
            daemon=True,
        )
        publisher_threads.append(pressure_thread)

        return publisher_threads

    def robot_status(self) -> RobotStatus:
        return RobotStatus.Available

    def _create_image(self, step: Union[TakeImage, TakeThermalImage]):
        now: datetime = datetime.utcnow()
        image_metadata: ImageMetadata = ImageMetadata(
            start_time=now,
            pose=telemetry.get_pose(),
            file_type="jpg",
        )
        image_metadata.tag_id = step.tag_id
        image_metadata.analysis = ["test1", "test2"]
        image_metadata.additional = step.metadata

        image: Image = Image(metadata=image_metadata)

        file: Path = random.choice(list(self.example_images.iterdir()))

        with open(file, "rb") as f:
            data: bytes = f.read()

        image.data = data

        return [image]

    def _create_video(self, step: TakeVideo):
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

        file: Path = random.choice(list(self.example_videos.iterdir()))

        with open(file, "rb") as f:
            data: bytes = f.read()

        video.data = data

        return [video]

    def _create_thermal_video(self, step: TakeThermalVideo):
        now: datetime = datetime.utcnow()
        thermal_video_metadata: ThermalVideoMetadata = ThermalVideoMetadata(
            start_time=now,
            pose=telemetry.get_pose(),
            file_type="mp4",
            duration=11,
        )
        thermal_video_metadata.tag_id = step.tag_id
        thermal_video_metadata.analysis_type = ["test1", "test2"]
        thermal_video_metadata.additional = step.metadata

        thermal_video: ThermalVideo = ThermalVideo(metadata=thermal_video_metadata)

        file: Path = random.choice(list(self.example_thermal_videos.iterdir()))

        with open(file, "rb") as f:
            data: bytes = f.read()

        thermal_video.data = data

        return [thermal_video]

    def _create_audio(self, step: RecordAudio):
        now: datetime = datetime.utcnow()
        audio_metadata: AudioMetadata = AudioMetadata(
            start_time=now,
            pose=telemetry.get_pose(),
            file_type="wav",
            duration=11,
        )
        audio_metadata.tag_id = step.tag_id
        audio_metadata.analysis_type = ["test1", "test2"]
        audio_metadata.additional = step.metadata

        audio: Audio = Audio(metadata=audio_metadata)

        file: Path = random.choice(list(self.example_thermal_videos.iterdir()))

        with open(file, "rb") as f:
            data: bytes = f.read()

        audio.data = data

        return [audio]
