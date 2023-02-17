import json
import logging
import os
import random
import time
from datetime import datetime
from logging import Logger
from pathlib import Path
from queue import Queue
from random import randrange
from threading import Thread
from typing import List, Sequence, Union

from alitra import Frame, Orientation, Pose, Position
from robot_interface.models.initialize import InitializeParams
from robot_interface.models.inspection.inspection import (
    Image,
    ImageMetadata,
    Inspection,
    TimeIndexedPose,
    Video,
    VideoMetadata,
)
from robot_interface.models.mission import (
    InspectionStep,
    Step,
    StepStatus,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
    TakeVideo,
)
from robot_interface.models.mission.status import RobotStatus
from robot_interface.robot_interface import RobotInterface
from robot_interface.telemetry.mqtt_client import MqttTelemetryPublisher
from robot_interface.telemetry.payloads import (
    TelemetryBatteryPayload,
    TelemetryPosePayload,
)
from robot_interface.utilities.json_service import EnhancedJSONEncoder

STEP_DURATION_IN_SECONDS = 5


class Robot(RobotInterface):
    def __init__(self):
        self.logger: Logger = logging.getLogger("robot")

        self.position: Position = Position(x=1, y=1, z=1, frame=Frame("asset"))
        self.orientation: Orientation = Orientation(
            x=0, y=0, z=0, w=1, frame=Frame("asset")
        )
        self.pose: Pose = Pose(
            position=self.position, orientation=self.orientation, frame=Frame("asset")
        )

        self.example_images: Path = Path(
            os.path.dirname(os.path.realpath(__file__)), "example_images"
        )

    def initiate_step(self, step: Step) -> bool:
        time.sleep(STEP_DURATION_IN_SECONDS)
        return True

    def step_status(self) -> StepStatus:
        return StepStatus.Successful

    def stop(self) -> bool:
        return True

    def get_inspections(self, step: InspectionStep) -> Sequence[Inspection]:
        if type(step) in [TakeImage, TakeThermalImage]:
            return self._create_image(step)
        elif type(step) in [TakeVideo, TakeThermalVideo]:
            return self._create_video(step)
        else:
            return None

    def initialize(self, params: InitializeParams) -> None:
        return

    def get_telemetry_publishers(self, queue: Queue, robot_id: str) -> List[Thread]:
        publisher_threads: List[Thread] = []

        pose_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=self._get_pose_telemetry,
            topic=f"isar/{robot_id}/pose",
            interval=1,
            retain=False,
        )
        pose_thread: Thread = Thread(
            target=pose_publisher.run,
            args=[robot_id],
            name="ISAR Robot Pose Publisher",
            daemon=True,
        )
        publisher_threads.append(pose_thread)

        battery_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=self._get_battery_telemetry,
            topic=f"isar/{robot_id}/battery",
            interval=5,
            retain=False,
        )
        battery_thread: Thread = Thread(
            target=battery_publisher.run,
            args=[robot_id],
            name="ISAR Robot Battery Publisher",
            daemon=True,
        )
        publisher_threads.append(battery_thread)

        return publisher_threads

    def _get_pose_telemetry(self, robot_id: str) -> str:
        random_position: Position = Position(
            x=random.uniform(0.1, 10),
            y=random.uniform(0.1, 10),
            z=random.uniform(0.1, 10),
            frame=Frame("asset"),
        )
        random_pose: Pose = Pose(
            position=random_position,
            orientation=self.pose.orientation,
            frame=Frame("asset"),
        )
        pose_payload: TelemetryPosePayload = TelemetryPosePayload(
            pose=random_pose, robot_id=robot_id, timestamp=datetime.utcnow()
        )
        return json.dumps(pose_payload, cls=EnhancedJSONEncoder)

    def _get_battery_telemetry(self, robot_id: str) -> str:
        battery_payload: TelemetryBatteryPayload = TelemetryBatteryPayload(
            battery_level=randrange(0, 1000) * 0.1,
            robot_id=robot_id,
            timestamp=datetime.utcnow(),
        )
        return json.dumps(battery_payload, cls=EnhancedJSONEncoder)

    def robot_status(self) -> RobotStatus:
        return RobotStatus.Available

    def _create_image(self, step: Union[TakeImage, TakeThermalImage]):
        now: datetime = datetime.utcnow()
        image_metadata: ImageMetadata = ImageMetadata(
            start_time=now,
            time_indexed_pose=TimeIndexedPose(pose=self.pose, time=now),
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

    def _create_video(self, step: Union[TakeVideo, TakeThermalVideo]):
        now: datetime = datetime.utcnow()
        video_metadata: VideoMetadata = VideoMetadata(
            start_time=now,
            time_indexed_pose=TimeIndexedPose(pose=self.pose, time=now),
            file_type="mp4",
            duration=11,
        )
        video_metadata.tag_id = step.tag_id
        video_metadata.analysis = ["test1", "test2"]
        video_metadata.additional = step.metadata

        video: Video = Video(metadata=video_metadata)

        file: Path = random.choice(list(self.example_images.iterdir()))

        with open(file, "rb") as f:
            data: bytes = f.read()

        video.data = data

        return [video]
