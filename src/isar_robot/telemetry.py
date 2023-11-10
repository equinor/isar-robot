import json
import random
from datetime import datetime

from alitra import Frame, Orientation, Pose, Position
from robot_interface.telemetry.payloads import (
    TelemetryBatteryPayload,
    TelemetryObstacleStatusPayload,
    TelemetryPosePayload,
    TelemetryPressurePayload,
)
from robot_interface.utilities.json_service import EnhancedJSONEncoder


def _get_battery_level() -> float:
    return 100 - random.randrange(0, 100) * 0.5


def _get_pressure_level() -> float:
    millibar_to_bar: float = 1 / 1000
    return (100 - random.randrange(0, 100) * 0.5) * millibar_to_bar


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


def get_pose_telemetry(isar_id: str, robot_name: str) -> str:
    pose_payload: TelemetryPosePayload = TelemetryPosePayload(
        pose=get_pose(),
        isar_id=isar_id,
        robot_name=robot_name,
        timestamp=datetime.utcnow(),
    )
    return json.dumps(pose_payload, cls=EnhancedJSONEncoder)


def get_battery_telemetry(isar_id: str, robot_name: str) -> str:
    battery_payload: TelemetryBatteryPayload = TelemetryBatteryPayload(
        battery_level=_get_battery_level(),
        isar_id=isar_id,
        robot_name=robot_name,
        timestamp=datetime.utcnow(),
    )
    return json.dumps(battery_payload, cls=EnhancedJSONEncoder)


def get_obstacle_status_telemetry(isar_id: str, robot_name: str) -> str:
    obstacle_status_payload: TelemetryObstacleStatusPayload = (
        TelemetryObstacleStatusPayload(
            obstacle_status=_get_obstacle_status(),
            isar_id=isar_id,
            robot_name=robot_name,
            timestamp=datetime.utcnow(),
        )
    )
    return json.dumps(obstacle_status_payload, cls=EnhancedJSONEncoder)


def get_pressure_telemetry(isar_id: str, robot_name: str) -> str:
    pressure_payload: TelemetryPressurePayload = TelemetryPressurePayload(
        pressure_level=_get_pressure_level(),
        isar_id=isar_id,
        robot_name=robot_name,
        timestamp=datetime.utcnow(),
    )
    return json.dumps(pressure_payload, cls=EnhancedJSONEncoder)
