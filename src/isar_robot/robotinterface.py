from typing import Any, Optional, Sequence, Tuple

from robot_interface.models.geometry.joints import Joints
from robot_interface.models.geometry.pose import Pose
from robot_interface.models.inspection.inspection import Inspection, InspectionResult
from robot_interface.models.mission import MissionStatus, Step
from robot_interface.robot_interface import RobotInterface


class Robot(RobotInterface):
    def schedule_step(self, step: Step) -> Tuple[bool, Optional[Any], Optional[Joints]]:
        raise NotImplementedError

    def mission_scheduled(self) -> bool:
        raise NotImplementedError

    def mission_status(self, mission_id: Any) -> MissionStatus:
        raise NotImplementedError

    def abort_mission(self) -> bool:
        raise NotImplementedError

    def log_status(
        self, mission_id: Any, mission_status: MissionStatus, current_step: Step
    ):
        raise NotImplementedError

    def get_inspection_references(
        self, vendor_mission_id: Any, current_step: Step
    ) -> Sequence[Inspection]:
        raise NotImplementedError

    def download_inspection_result(
        self, inspection: Inspection
    ) -> Optional[InspectionResult]:
        raise NotImplementedError

    def robot_pose(self) -> Pose:
        raise NotImplementedError
