import logging
import os
import random
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Any, Optional, Sequence, Tuple

from robot_interface.models.geometry.frame import Frame
from robot_interface.models.geometry.joints import Joints
from robot_interface.models.geometry.orientation import Orientation
from robot_interface.models.geometry.pose import Pose
from robot_interface.models.geometry.position import Position
from robot_interface.models.inspection.formats import Image
from robot_interface.models.inspection.inspection import (
    Inspection,
    InspectionResult,
    TimeIndexedPose,
)
from robot_interface.models.inspection.metadata import ImageMetadata
from robot_interface.models.inspection.references import ImageReference
from robot_interface.models.mission import MissionStatus, Task
from robot_interface.robot_interface import RobotInterface


class Robot(RobotInterface):
    def __init__(self):
        self.logger: Logger = logging.getLogger("robot")
        self.inspection_id: int = 1

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

    def schedule_task(self, task: Task) -> Tuple[bool, Optional[Any], Optional[Joints]]:
        mission_id: int = 1
        scheduled: bool = True
        return scheduled, mission_id, None

    def mission_scheduled(self) -> bool:
        return False

    def mission_status(self, mission_id: Any) -> MissionStatus:
        return MissionStatus.Completed

    def abort_mission(self) -> bool:
        return True

    def log_status(
        self, mission_id: Any, mission_status: MissionStatus, current_task: Task
    ):
        self.logger.info(f"Mission ID: {mission_id}")
        self.logger.info(f"Mission Status: {mission_status}")
        self.logger.info(f"Current task: {current_task}")

    def get_inspection_references(
        self, vendor_mission_id: Any, current_task: Task
    ) -> Sequence[Inspection]:
        now: datetime = datetime.utcnow()
        image_metadata: ImageMetadata = ImageMetadata(
            start_time=now,
            time_indexed_pose=TimeIndexedPose(pose=self.pose, time=now),
            file_type="jpg",
            tag_id="123-AB-4567",
        )
        image_ref: ImageReference = ImageReference(
            id=self.inspection_id, metadata=image_metadata
        )

        return [image_ref]

    def download_inspection_result(
        self, inspection: Inspection
    ) -> Optional[InspectionResult]:
        file: Path = random.choice(list(self.example_images.iterdir()))

        with open(file, "rb") as f:
            data: bytes = f.read()

        image: Image = Image(
            id=self.inspection_id, metadata=inspection.metadata, data=data
        )
        return image

    def robot_pose(self) -> Pose:
        return self.pose
