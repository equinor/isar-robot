import logging
import time
from logging import Logger
from queue import Queue
from threading import Thread
from typing import List, Optional, Sequence

from robot_interface.models.initialize import InitializeParams
from robot_interface.models.inspection.inspection import Inspection
from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.status import MissionStatus, RobotStatus, StepStatus
from robot_interface.models.mission.step import (
    InspectionStep,
    RecordAudio,
    Step,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
    TakeVideo,
)
from robot_interface.robot_interface import RobotInterface
from robot_interface.telemetry.mqtt_client import MqttTelemetryPublisher

from isar_robot import inspections, telemetry
from isar_robot.config.settings import settings
from isar_robot.utilities import (
    is_localization_mission,
    is_localization_step,
    is_return_to_home_mission,
    is_return_to_home_step,
)


class Robot(RobotInterface):
    def __init__(self) -> None:
        self.logger: Logger = logging.getLogger("isar_robot")
        self.current_mission: Optional[Mission] = None
        self.current_step: Optional[Step] = None

    def initiate_mission(self, mission: Mission) -> None:
        time.sleep(settings.MISSION_DURATION_IN_SECONDS)
        self.current_mission = mission

    def mission_status(self) -> MissionStatus:
        if is_localization_mission(self.current_mission):
            self.current_mission = None
            if settings.SHOULD_FAIL_LOCALIZATION_MISSION:
                return MissionStatus.Failed
            return MissionStatus.Successful

        if is_return_to_home_mission(self.current_mission):
            self.current_step = None
            if settings.SHOULD_FAIL_RETURN_TO_HOME_MISSION:
                return MissionStatus.Failed
            return MissionStatus.Successful

        self.current_mission = None
        if settings.SHOULD_FAIL_NORMAL_MISSION:
            return MissionStatus.Failed
        return MissionStatus.Successful

    def initiate_step(self, step: Step) -> None:
        self.logger.info(f"Initiated step of type {step.__class__.__name__}")
        self.current_step = step
        time.sleep(settings.STEP_DURATION_IN_SECONDS)

    def step_status(self) -> StepStatus:
        if is_localization_step(self.current_step):
            self.current_step = None
            if settings.SHOULD_FAIL_LOCALIZATION_STEP:
                return StepStatus.Failed
            return StepStatus.Successful

        if is_return_to_home_step(self.current_step):
            self.current_step = None
            if settings.SHOULD_FAIL_RETURN_TO_HOME_STEP:
                return StepStatus.Failed
            return StepStatus.Successful

        self.current_step = None
        if settings.SHOULD_FAIL_NORMAL_STEP:
            return StepStatus.Failed
        return StepStatus.Successful

    def stop(self) -> None:
        return

    def get_inspections(self, step: InspectionStep) -> Sequence[Inspection]:
        if type(step) in [TakeImage, TakeThermalImage]:
            return inspections.create_image(step)
        elif type(step) is TakeVideo:
            return inspections.create_video(step)
        elif type(step) is TakeThermalVideo:
            return inspections.create_thermal_video(step)
        elif type(step) is RecordAudio:
            return inspections.create_audio(step)
        else:
            return None

    def initialize(self, params: InitializeParams) -> None:
        return

    def get_telemetry_publishers(
        self, queue: Queue, isar_id: str, robot_name: str
    ) -> List[Thread]:
        publisher_threads: List[Thread] = []

        pose_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=telemetry.get_pose_telemetry,
            topic=f"isar/{isar_id}/pose",
            interval=5,
            retain=False,
        )
        pose_thread: Thread = Thread(
            target=pose_publisher.run,
            args=[isar_id, robot_name],
            name="ISAR Robot Pose Publisher",
            daemon=True,
        )
        publisher_threads.append(pose_thread)

        battery_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=telemetry.get_battery_telemetry,
            topic=f"isar/{isar_id}/battery",
            interval=30,
            retain=False,
        )
        battery_thread: Thread = Thread(
            target=battery_publisher.run,
            args=[isar_id, robot_name],
            name="ISAR Robot Battery Publisher",
            daemon=True,
        )
        publisher_threads.append(battery_thread)

        obstacle_status_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=telemetry.get_obstacle_status_telemetry,
            topic=f"isar/{isar_id}/obstacle_status",
            interval=10,
            retain=False,
        )
        obstacle_status_thread: Thread = Thread(
            target=obstacle_status_publisher.run,
            args=[isar_id, robot_name],
            name="ISAR Robot Obstacle Status Publisher",
            daemon=True,
        )
        publisher_threads.append(obstacle_status_thread)

        pressure_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=telemetry.get_pressure_telemetry,
            topic=f"isar/{isar_id}/pressure",
            interval=20,
            retain=False,
        )
        pressure_thread: Thread = Thread(
            target=pressure_publisher.run,
            args=[isar_id, robot_name],
            name="ISAR Robot Pressure Publisher",
            daemon=True,
        )
        publisher_threads.append(pressure_thread)

        return publisher_threads

    def robot_status(self) -> RobotStatus:
        return RobotStatus.Available

    def pause(self) -> None:
        return

    def resume(self) -> None:
        return
