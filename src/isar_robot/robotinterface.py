import logging
import os
import random
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Sequence

from alitra import Frame, Orientation, Pose, Position
from robot_interface.models.inspection.inspection import (
    Image,
    ImageMetadata,
    Inspection,
    TimeIndexedPose,
)
from robot_interface.models.mission import InspectionStep, Step, StepStatus
from robot_interface.robot_interface import RobotInterface


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
