import json
import random
from datetime import datetime, timezone

from alitra import Frame, Orientation, Pose, Position

from isar_robot.config.settings import settings

from robot_interface.models.robots.battery_state import BatteryState
from robot_interface.telemetry.payloads import (
    TelemetryBatteryPayload,
    TelemetryObstacleStatusPayload,
    TelemetryPosePayload,
    TelemetryPressurePayload,
)
from robot_interface.utilities.json_service import EnhancedJSONEncoder

from typing import Optional


def _get_pressure_level() -> float:
    # Return random float in the range [0.011, 0.079]
    min_pressure = 11  # millibar
    max_pressure = 79  # millibar
    millibar_to_bar: float = 1 / 1000
    return random.randint(min_pressure, max_pressure) * millibar_to_bar


def _get_obstacle_status() -> bool:
    return False


def get_pose() -> Pose:
    random_position: Position = Position(
        x=random.uniform(0.1, 10),
        y=random.uniform(0.1, 10),
        z=random.uniform(0.1, 10),
        frame=Frame("asset"),
    )
    orientation: Orientation = Orientation(x=0, y=0, z=0, w=1, frame=Frame("asset"))
    random_pose: Pose = Pose(
        position=random_position,
        orientation=orientation,
        frame=Frame("asset"),
    )
    return random_pose


class Telemetry:
    def __init__(self) -> None:
        self.current_battery_level: float = 75.0
        self.min_battery_level: int = 0
        self.max_battery_level: int = 100
        self.charging_rate: float = 2.0
        self.discharging_rate: float = 0.4

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

    def get_pose_telemetry(self, isar_id: str, robot_name: str) -> str:
        pose_payload: TelemetryPosePayload = TelemetryPosePayload(
            pose=get_pose(),
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
