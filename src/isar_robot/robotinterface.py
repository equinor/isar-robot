import logging
import random
import time
from collections.abc import Callable
from datetime import UTC, datetime
from threading import Thread

from alitra import Position
from robot_interface.models.exceptions.robot_exceptions import (
    RobotAlreadyHomeException,
    RobotCommunicationException,
    RobotNoMissionRunningException,
)
from robot_interface.models.inspection.inspection import Inspection
from robot_interface.models.mission.mission import Mission, TaskTypes
from robot_interface.models.mission.status import MissionStatus, RobotStatus, TaskStatus
from robot_interface.models.mission.task import (
    InspectionTask,
    RecordAudio,
    TakeAcousticMeasurement,
    TakeCO2Measurement,
    TakeImage,
    TakeThermalImage,
    TakeThermalVideo,
    TakeVideo,
)
from robot_interface.models.robots.media import MediaConfig
from robot_interface.robot_interface import RobotInterface
from robot_interface.telemetry.mqtt_client import TelemetryParameters

from isar_robot import inspections, telemetry
from isar_robot.config.settings import settings
from isar_robot.simulation import MissionSimulation

logger = logging.getLogger(__name__)


class Robot(RobotInterface):
    def __init__(self, robot_name: str, isar_id: str) -> None:
        super().__init__(robot_name=robot_name, isar_id=isar_id)

        self.telemetry = telemetry.Telemetry()
        self.last_task_completion_time: datetime = datetime.now(UTC)
        self.robot_is_home: bool = settings.SHOULD_START_AT_HOME
        self.mission_simulation: MissionSimulation | None = None

    def initiate_mission(self, mission: Mission) -> None:
        if (
            self.mission_simulation
            and self.mission_simulation.is_alive()
            and not self.mission_simulation.mission_done
        ):
            raise RobotCommunicationException(
                error_description="Could not start mission as one is already running"
            )
        elif self.robot_is_home and mission.tasks[0].type == TaskTypes.ReturnToHome:
            raise RobotAlreadyHomeException(
                error_description="Ignoring initiate of return to home as robot is already home"
            )
        elif self.mission_simulation:
            self.mission_simulation.join()
        self.mission_simulation = MissionSimulation(mission)
        self.mission_simulation.start()
        self.robot_is_home = False
        logger.info(f"Mission initiated: {mission.id}")

    def task_status(self, task_id: str) -> TaskStatus:
        if not self.mission_simulation:
            raise RobotNoMissionRunningException(
                error_description="Could not get task status as no mission is running"
            )

        status = self.mission_simulation.task_status(task_id)
        return status

    def mission_status(self, mission_id):
        status = self.mission_simulation.mission_status()
        if (
            status == MissionStatus.Successful
            and self.mission_simulation.is_return_home
        ):
            self.robot_is_home = True
        return status

    def stop(self) -> None:
        logger.info("Stopping current mission")
        if not self.mission_simulation:
            raise RobotNoMissionRunningException(
                error_description="Attempted to stop non-existent mission"
            )
        try:
            self.mission_simulation.stop_mission()
        finally:
            self.mission_simulation = None

    def get_inspection(self, task: InspectionTask) -> Inspection:
        if type(task) is TakeImage:
            return inspections.create_image(task, self.telemetry)
        elif type(task) is TakeThermalImage:
            return inspections.create_thermal_image(task, self.telemetry)
        elif type(task) is TakeVideo:
            return inspections.create_video(task, self.telemetry)
        elif type(task) is TakeThermalVideo:
            return inspections.create_thermal_video(task, self.telemetry)
        elif type(task) is TakeCO2Measurement:
            return inspections.create_co2_measurement(task, self.telemetry)
        elif type(task) is TakeAcousticMeasurement:
            return inspections.create_acoustic_measurement(task, self.telemetry)
        elif type(task) is RecordAudio:
            return inspections.create_audio(task, self.telemetry)
        else:
            return None

    def register_inspection_callback(
        self, callback_function: Callable[[Inspection, Mission], None]
    ) -> Thread | None:

        if settings.SHOULD_SIMULATE_INSPECTION_CALLBACK_CRASH:
            return None

        def inspection_handler_with_crash():
            crash_after = random.randint(10, 60)  # Random between 10-60 seconds
            logger.info(
                f"Inspection callback thread started - will crash after {crash_after} seconds"
            )
            time.sleep(crash_after)
            logger.warning("Inspection callback thread crashing now...")

        thread = Thread(
            target=inspection_handler_with_crash,
            name="Inspection Callback Handler",
            daemon=True,
        )
        return thread

    def initialize(self) -> None:
        return

    def _get_pose_telemetry(self) -> str:
        current_target: Position | None = None
        if self.mission_simulation:
            current_task = self.mission_simulation.current_task()
            if current_task and isinstance(current_task, InspectionTask):
                current_target = current_task.robot_pose.position

        return self.telemetry.get_pose_telemetry(current_target=current_target)

    def _get_battery_telemetry(self) -> str:
        return self.telemetry.get_battery_telemetry(is_home=self.robot_is_home)

    def get_telemetry_publishers(self) -> list[TelemetryParameters]:
        return [
            TelemetryParameters(
                name="ISAR Robot Pose Publisher",
                method=lambda: self._get_pose_telemetry(),
                topic="pose",
                interval=settings.ROBOT_POSE_PUBLISH_INTERVAL,
            ),
            TelemetryParameters(
                name="ISAR Robot Battery Publisher",
                method=lambda: self._get_battery_telemetry(),
                topic="battery",
                interval=settings.ROBOT_BATTERY_PUBLISH_INTERVAL,
            ),
            TelemetryParameters(
                name="ISAR Robot Obstacle Status Publisher",
                method=lambda: self.telemetry.get_obstacle_status_telemetry(),
                topic="obstacle_status",
                interval=settings.ROBOT_OBSTACLE_STATUS_PUBLISH_INTERVAL,
            ),
            TelemetryParameters(
                name="ISAR Robot Pressure Publisher",
                method=lambda: self.telemetry.get_pressure_telemetry(),
                topic="pressure",
                interval=settings.ROBOT_PRESSURE_PUBLISH_INTERVAL,
            ),
        ]

    def get_utility_threads(self) -> list[Thread]:
        return []

    def robot_status(self) -> RobotStatus:
        if self.mission_simulation and not self.mission_simulation.mission_done:
            mission_status: MissionStatus = self.mission_simulation.mission_status()
            # A paused mission is still the robot's current mission, so the
            # robot is not available to take another one. RobotStatus has no
            # Paused member: pausing is a property of the mission, and ISAR
            # tracks it in its own state machine.
            if mission_status in [
                MissionStatus.Paused,
                MissionStatus.InProgress,
                MissionStatus.NotStarted,
            ]:
                return RobotStatus.Busy
        if self.robot_is_home:
            return RobotStatus.Home
        return RobotStatus.Available

    def pause(self) -> None:
        logger.info("Pausing current mission")
        if not self.mission_simulation:
            raise RobotNoMissionRunningException(
                error_description="Attempted to pause non-existent mission"
            )
        self.mission_simulation.pause_mission()

    def resume(self) -> None:
        logger.info("Resuming current mission")
        if not self.mission_simulation:
            raise RobotNoMissionRunningException(
                error_description="Attempted to resume non-existent mission"
            )
        self.mission_simulation.resume_mission()

    def generate_media_config(self) -> MediaConfig | None:
        return None

    def get_battery_level(self):
        return self.telemetry.current_battery_level
