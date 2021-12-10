import logging
import os
import random
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Optional, Sequence
from uuid import UUID

from robot_interface.models.geometry.frame import Frame
from robot_interface.models.geometry.orientation import Orientation
from robot_interface.models.geometry.pose import Pose
from robot_interface.models.geometry.position import Position
from robot_interface.models.inspection.inspection import (
    Image,
    ImageMetadata,
    Inspection,
    TimeIndexedPose,
)
from robot_interface.models.mission import Task, TaskStatus
from robot_interface.robot_interface import RobotInterface


class Robot(RobotInterface):
    def __init__(self):
        self.logger: Logger = logging.getLogger("robot")

        self.position: Position = Position(x=1, y=1, z=1, frame=Frame.Robot)
        self.orientation: Orientation = Orientation(
            x=0, y=0, z=0, w=1, frame=Frame.Robot
        )
        self.pose: Pose = Pose(
            position=self.position, orientation=self.orientation, frame=Frame.Robot
        )

        self.example_images: Path = Path(
            os.path.dirname(os.path.realpath(__file__)), "example_images"
        )

    def schedule_task(self, task: Task) -> bool:
        scheduled: bool = True
        return scheduled

    def mission_scheduled(self) -> bool:
        return False

    def task_status(self, task_id: Optional[UUID]) -> TaskStatus:
        return TaskStatus.Completed

    def abort_mission(self) -> bool:
        return True

    def log_status(self, task_status: TaskStatus, current_task: Task):
        self.logger.info(f"Task Status: {task_status}")
        self.logger.info(f"Current task: {current_task}")

    def get_inspection_references(self, inspection_task: Task) -> Sequence[Inspection]:
        now: datetime = datetime.utcnow()
        image_metadata: ImageMetadata = ImageMetadata(
            start_time=now,
            time_indexed_pose=TimeIndexedPose(pose=self.pose, time=now),
            file_type="jpg",
        )
        image_metadata.tag_id = "123-AB-4567"

        image: Image = Image(metadata=image_metadata)

        return [image]

    def download_inspection_result(self, inspection: Inspection) -> Inspection:
        file: Path = random.choice(list(self.example_images.iterdir()))

        with open(file, "rb") as f:
            data: bytes = f.read()

        inspection.data = data
        return inspection

    def robot_pose(self) -> Pose:
        return self.pose
