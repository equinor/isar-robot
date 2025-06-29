import logging
import time
from datetime import datetime, timezone
from logging import Logger
from queue import Queue
from threading import Thread
from typing import Callable, List, Optional

from robot_interface.models.inspection.inspection import Inspection
from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.status import RobotStatus, TaskStatus
from robot_interface.models.mission.task import (
    InspectionTask,
    RecordAudio,
    ReturnToHome,
    TakeCO2Measurement,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
    TakeVideo,
    Task,
)
from robot_interface.models.robots.media import MediaConfig
from robot_interface.robot_interface import RobotInterface
from robot_interface.telemetry.mqtt_client import MqttTelemetryPublisher

from isar_robot import inspections, telemetry
from isar_robot.config.settings import settings


class Robot(RobotInterface):
    def __init__(self) -> None:
        self.telemetry = telemetry.Telemetry()
        self.logger: Logger = logging.getLogger("isar_robot")
        self.current_mission: Optional[Mission] = None
        self.current_task: Optional[Task] = None
        self.last_task_completion_time: datetime = datetime.now(timezone.utc)
        self.robot_is_home: bool = False

    def initiate_mission(self, mission: Mission) -> None:
        time.sleep(settings.INITIATE_MISSION_DURATION_IN_SECONDS)
        self.current_mission = mission
        self.current_task_ix = 0
        self.current_task = mission.tasks[self.current_task_ix]
        self.task_len = len(mission.tasks)
        self.last_task_completion_time = datetime.now(timezone.utc)
        self.robot_is_home = False

    def task_status(self, task_id: str) -> TaskStatus:
        now: datetime = datetime.now(timezone.utc)
        if (
            now - self.last_task_completion_time
        ).total_seconds() < settings.TASK_DURATION_IN_SECONDS:
            return TaskStatus.InProgress
        self.last_task_completion_time = now

        next_task: Task = None
        if self.current_mission:
            if self.current_task_ix < self.task_len - 1:
                self.current_task_ix = self.current_task_ix + 1
                next_task = self.current_mission.tasks[self.current_task_ix]

        # This only happens for last task in mission
        if isinstance(self.current_task, ReturnToHome):
            self.current_task = None
            if settings.SHOULD_FAIL_RETURN_TO_HOME_TASK:
                return TaskStatus.Failed
            self.robot_is_home = True
            return TaskStatus.Successful

        if next_task:
            self.current_task = next_task
        else:
            self.current_task = None
        if settings.SHOULD_FAIL_NORMAL_TASK:
            return TaskStatus.Failed
        return TaskStatus.Successful

    def stop(self) -> None:
        return

    def get_inspection(self, task: InspectionTask) -> Inspection:
        if type(task) in [TakeImage, TakeThermalImage]:
            return inspections.create_image(task)
        elif type(task) is TakeVideo:
            return inspections.create_video(task)
        elif type(task) is TakeThermalVideo:
            return inspections.create_thermal_video(task)
        elif type(task) is TakeCO2Measurement:
            return inspections.create_co2_measurement(task)
        elif type(task) is RecordAudio:
            return inspections.create_audio(task)
        else:
            return None

    def register_inspection_callback(
        self, callback_function: Callable[[Inspection], None]
    ) -> None:
        raise NotImplementedError

    def initialize(self) -> None:
        return

    def _get_battery_telemetry(self, isar_id: str, robot_name: str) -> str:
        return self.telemetry.get_battery_telemetry(
            isar_id=isar_id, robot_name=robot_name, is_home=self.robot_is_home
        )

    def get_telemetry_publishers(
        self, queue: Queue, isar_id: str, robot_name: str
    ) -> List[Thread]:
        publisher_threads: List[Thread] = []

        pose_publisher: MqttTelemetryPublisher = MqttTelemetryPublisher(
            mqtt_queue=queue,
            telemetry_method=self.telemetry.get_pose_telemetry,
            topic=f"isar/{isar_id}/pose",
            interval=settings.ROBOT_POSE_PUBLISH_INTERVAL,
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
            telemetry_method=self._get_battery_telemetry,
            topic=f"isar/{isar_id}/battery",
            interval=settings.ROBOT_BATTERY_PUBLISH_INTERVAL,
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
            telemetry_method=self.telemetry.get_obstacle_status_telemetry,
            topic=f"isar/{isar_id}/obstacle_status",
            interval=settings.ROBOT_OBSTACLE_STATUS_PUBLISH_INTERVAL,
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
            telemetry_method=self.telemetry.get_pressure_telemetry,
            topic=f"isar/{isar_id}/pressure",
            interval=settings.ROBOT_PRESSURE_PUBLISH_INTERVAL,
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
        if self.robot_is_home:
            return RobotStatus.Home
        return RobotStatus.Available

    def pause(self) -> None:
        return

    def resume(self) -> None:
        return

    def generate_media_config(self) -> Optional[MediaConfig]:
        return None
