import logging
from logging import Logger
from typing import Any, Optional, Sequence, Tuple

from robot_interface.models.geometry.frame import Frame
from robot_interface.models.geometry.joints import Joints
from robot_interface.models.geometry.orientation import Orientation
from robot_interface.models.geometry.pose import Pose
from robot_interface.models.geometry.position import Position
from robot_interface.models.inspection.inspection import Inspection, InspectionResult
from robot_interface.models.mission import MissionStatus, Step
from robot_interface.robot_interface import RobotInterface


class Robot(RobotInterface):
    def __init__(self):
        self.logger: Logger = logging.getLogger("robot")

    def schedule_step(self, step: Step) -> Tuple[bool, Optional[Any], Optional[Joints]]:
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
        self, mission_id: Any, mission_status: MissionStatus, current_step: Step
    ):
        self.logger.info(f"Mission ID: {mission_id}")
        self.logger.info(f"Mission Status: {mission_status}")
        self.logger.info(f"Current Step: {current_step}")

    def get_inspection_references(
        self, vendor_mission_id: Any, current_step: Step
    ) -> Sequence[Inspection]:
        return []

    def download_inspection_result(
        self, inspection: Inspection
    ) -> Optional[InspectionResult]:
        return None

    def robot_pose(self) -> Pose:
        position: Position = Position(x=1, y=1, z=1, frame=Frame.Robot)
        orientation: Orientation = Orientation(x=0, y=0, z=0, w=1, frame=Frame.Robot)
        return Pose(position=position, orientation=orientation, frame=Frame.Robot)
