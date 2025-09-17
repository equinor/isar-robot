import json
import random
from datetime import datetime, timezone
from typing import Optional

from alitra import Frame, Orientation, Pose, Position
from robot_interface.models.robots.battery_state import BatteryState
from robot_interface.telemetry.payloads import (
    TelemetryBatteryPayload,
    TelemetryObstacleStatusPayload,
    TelemetryPosePayload,
    TelemetryPressurePayload,
)
from robot_interface.utilities.json_service import EnhancedJSONEncoder

from isar_robot.config.settings import settings


def _get_pressure_level() -> float:
    # Return random float in the range [0.011, 0.079]
    min_pressure = 11  # millibar
    max_pressure = 79  # millibar
    millibar_to_bar: float = 1 / 1000
    return random.randint(min_pressure, max_pressure) * millibar_to_bar


def _get_obstacle_status() -> bool:
    return False


class Telemetry:
    def __init__(self) -> None:
        self.current_battery_level: float = 75.0
        self.min_battery_level: int = 0
        self.max_battery_level: int = 100
        self.charging_rate: float = 2.0
        self.discharging_rate: float = 0.4

        self.current_pose = Pose(
            Position(
                x=1,
                y=1,
                z=1,
                frame=Frame("asset"),
            ),
            Orientation(x=0, y=0, z=0, w=1, frame=Frame("asset")),
            frame=Frame("asset"),
        )
        self.movement_percentage: float = 0.5

    def get_pose(self) -> Pose:
        return self.current_pose

    def _get_pose(self, current_target: Optional[Position]) -> Pose:
        if not current_target:
            return self.current_pose

        self.current_pose.position.x += self.movement_percentage * (
            current_target.x - self.current_pose.position.x
        )
        self.current_pose.position.y += self.movement_percentage * (
            current_target.y - self.current_pose.position.y
        )
        self.current_pose.position.z += self.movement_percentage * (
            current_target.z - self.current_pose.position.z
        )
        return self.current_pose

    def _get_battery_level(self, is_home: Optional[bool] = None) -> float:
        if settings.SHOULD_HAVE_RANDOM_BATTERY_LEVEL or is_home is None:
            # Return random float in the range [50, 100]
            return random.randint(500, 1000) / 10.0

        if is_home:
            self.current_battery_level = min(
                self.max_battery_level, self.current_battery_level + self.charging_rate
            )
        else:
            self.current_battery_level = max(
                self.min_battery_level,
                self.current_battery_level - self.discharging_rate,
            )
        return self.current_battery_level

    def _get_battery_state(self, is_home: Optional[bool] = None) -> BatteryState:
        if settings.SHOULD_HAVE_RANDOM_BATTERY_LEVEL or is_home is None:
            return BatteryState.Normal

        return BatteryState.Charging if is_home else BatteryState.Normal

    def get_battery_telemetry(
        self, isar_id: str, robot_name: str, is_home: Optional[bool] = None
    ) -> str:
        battery_payload: TelemetryBatteryPayload = TelemetryBatteryPayload(
            battery_level=self._get_battery_level(is_home=is_home),
            battery_state=self._get_battery_state(is_home=is_home),
            isar_id=isar_id,
            robot_name=robot_name,
            timestamp=datetime.now(timezone.utc),
        )
        return json.dumps(battery_payload, cls=EnhancedJSONEncoder)

    def get_pose_telemetry(
        self, isar_id: str, robot_name: str, current_target: Optional[Position]
    ) -> str:
        pose_payload: TelemetryPosePayload = TelemetryPosePayload(
            pose=self._get_pose(current_target=current_target),
            isar_id=isar_id,
            robot_name=robot_name,
            timestamp=datetime.now(timezone.utc),
        )
        return json.dumps(pose_payload, cls=EnhancedJSONEncoder)

    def get_obstacle_status_telemetry(self, isar_id: str, robot_name: str) -> str:
        obstacle_status_payload: TelemetryObstacleStatusPayload = (
            TelemetryObstacleStatusPayload(
                obstacle_status=_get_obstacle_status(),
                isar_id=isar_id,
                robot_name=robot_name,
                timestamp=datetime.now(timezone.utc),
            )
        )
        return json.dumps(obstacle_status_payload, cls=EnhancedJSONEncoder)

    def get_pressure_telemetry(self, isar_id: str, robot_name: str) -> str:
        pressure_payload: TelemetryPressurePayload = TelemetryPressurePayload(
            pressure_level=_get_pressure_level(),
            isar_id=isar_id,
            robot_name=robot_name,
            timestamp=datetime.now(timezone.utc),
        )
        return json.dumps(pressure_payload, cls=EnhancedJSONEncoder)
