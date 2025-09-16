import logging
from datetime import datetime, timezone
from logging import Logger
from queue import Queue
from threading import Thread
from typing import Callable, List, Optional

from robot_interface.models.exceptions.robot_exceptions import (
    RobotCommunicationException,
)
from robot_interface.models.inspection.inspection import Inspection
from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.status import MissionStatus, RobotStatus, TaskStatus
from robot_interface.models.mission.task import (
    InspectionTask,
    RecordAudio,
    TakeCO2Measurement,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
    TakeVideo,
)
from robot_interface.models.robots.media import MediaConfig
from robot_interface.robot_interface import RobotInterface
from robot_interface.telemetry.mqtt_client import MqttTelemetryPublisher

from isar_robot import inspections, telemetry
from isar_robot.config.settings import settings
from isar_robot.simulation import MissionSimulation


class Robot(RobotInterface):
    def __init__(self) -> None:
        self.telemetry = telemetry.Telemetry()
        self.logger: Logger = logging.getLogger("isar_robot")
        self.last_task_completion_time: datetime = datetime.now(timezone.utc)
        self.robot_is_home: bool = False
        self.mission_simulation: Optional[MissionSimulation] = None

    def initiate_mission(self, mission: Mission) -> None:
        if self.mission_simulation and not self.mission_simulation.mission_done:
            raise RobotCommunicationException(
                error_description="Could not start mission as one is already running"
            )
        elif self.mission_simulation:
            self.mission_simulation.join()
        self.mission_simulation = MissionSimulation(mission)
        self.mission_simulation.start()
        self.robot_is_home = False

    def task_status(self, task_id: str) -> TaskStatus:
        if not self.mission_simulation:
            raise RobotCommunicationException(
                error_description="Could not get task status as no mission is running"
            )

        status = self.mission_simulation.task_status(task_id)
        if status == TaskStatus.Successful and self.mission_simulation.is_return_home:
            self.robot_is_home = True
        return status

    def stop(self) -> None:
        if not self.mission_simulation:
            raise RobotCommunicationException(
                error_description="Attempted to stop non-existent mission"
            )
        self.mission_simulation.stop_mission()

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
        if self.mission_simulation and self.mission_simulation.is_alive():
            mission_status: MissionStatus = self.mission_simulation.mission_status()
            if mission_status == MissionStatus.Paused:
                return RobotStatus.Paused
            elif mission_status in [MissionStatus.InProgress, MissionStatus.NotStarted]:
                return RobotStatus.Busy
        if self.robot_is_home:
            return RobotStatus.Home
        return RobotStatus.Available

    def pause(self) -> None:
        if not self.mission_simulation:
            raise RobotCommunicationException(
                error_description="Attempted to pause non-existent mission"
            )
        self.mission_simulation.pause_mission()

    def resume(self) -> None:
        if not self.mission_simulation:
            raise RobotCommunicationException(
                error_description="Attempted to resume non-existent mission"
            )
        self.mission_simulation.resume_mission()

    def generate_media_config(self) -> Optional[MediaConfig]:
        return None

    def get_battery_level(self):
        return self.telemetry.current_battery_level
