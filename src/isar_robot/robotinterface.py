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
from typing import List, Sequence

from alitra import Frame, Orientation, Pose, Position
from robot_interface.models.initialize import InitializeParams
from robot_interface.models.inspection.inspection import (
    Image,
    ImageMetadata,
    Inspection,
    TimeIndexedPose,
)
from robot_interface.models.mission import InspectionStep, Step, StepStatus
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
        now: datetime = datetime.utcnow()
        image_metadata: ImageMetadata = ImageMetadata(
            start_time=now,
            time_indexed_pose=TimeIndexedPose(pose=self.pose, time=now),
            file_type="jpg",
        )
        image_metadata.tag_id = step.tag_id

        image: Image = Image(metadata=image_metadata)

        file: Path = random.choice(list(self.example_images.iterdir()))

        with open(file, "rb") as f:
            data: bytes = f.read()

        image.data = data

        return [image]

    def initialize(self, params: InitializeParams) -> None:
        return

    def get_telemetry_publishers(self, queue: Queue, robot_id: str) -> List[Thread]:
        publisher_threads: List[Thread] = []

        pose_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=self._get_pose_telemetry,
            topic=f"isar/{robot_id}/pose",
            interval=1,
            retain=True,
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
            retain=True,
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
        pose_payload: TelemetryPosePayload = TelemetryPosePayload(
            pose=self.pose, robot_id=robot_id, timestamp=datetime.utcnow()
        )
        return json.dumps(pose_payload, cls=EnhancedJSONEncoder)

    def _get_battery_telemetry(self, robot_id: str) -> str:
        battery_payload: TelemetryBatteryPayload = TelemetryBatteryPayload(
            battery_level=randrange(0, 1000) * 0.1,
            robot_id=robot_id,
            timestamp=datetime.utcnow(),
        )
        return json.dumps(battery_payload, cls=EnhancedJSONEncoder)
