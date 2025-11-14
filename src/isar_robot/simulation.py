import logging
import random
import time
from threading import Event, Thread

from robot_interface.models.exceptions.robot_exceptions import (
    RobotTaskStatusException,
    RobotMissionStatusException,
    RobotNoMissionRunningException,
)
from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.status import MissionStatus, TaskStatus
from robot_interface.models.mission.task import ReturnToHome

from isar_robot.config.settings import settings


class MissionSimulation(Thread):
    def __init__(
        self,
        mission: Mission,
    ):
        time.sleep(settings.MISSION_SIMULATION_TIME_TO_START)
        self.logger = logging.getLogger("isar robot mission simulation")
        self.mission: Mission = mission
        self.task_index: int = 0
        self.n_tasks: int = len(mission.tasks)
        self.robot_is_home: bool = False
        self.task_statuses: list[TaskStatus] = list(
            map(lambda _: TaskStatus.NotStarted, self.mission.tasks)
        )
        self.task_id_mapping = {}
        for i, task in enumerate(self.mission.tasks):
            self.task_id_mapping[task.id] = i

        self.is_return_home: bool = len(self.mission.tasks) == 1 and isinstance(
            self.mission.tasks[0], ReturnToHome
        )
        self.task_failure_probability: float = (
            settings.MISSION_SIMULATION_TASK_FAILURE_PROBABILITY
        )
        self.return_home_task_failure_probability: float = (
            settings.MISSION_SIMULATION_RETURN_HOME_TASK_FAILURE_PROBABILITY
        )
        self.api_delay_modifier: float = settings.MISSION_SIMULATION_API_DELAY_MODIFIER

        self.mission_done: bool = False
        self.all_tasks_done: bool = False
        self.mission_started: bool = False

        self.signal_resume_mission: Event = Event()
        self.signal_resume_mission.set()
        self.signal_stop_mission: Event = Event()
        Thread.__init__(self, name="Mission simulation thread")

    def stop(self) -> None:
        return

    def _simulate_api_call_delay(self):
        time.sleep(random.random() * self.api_delay_modifier)

    def pause_mission(self):
        if self.mission_done:
            raise RobotNoMissionRunningException(
                error_description="Could not pause non-existent mission"
            )
        self.signal_resume_mission.clear()

    def resume_mission(self):
        if self.mission_done:
            raise RobotNoMissionRunningException(
                error_description="Could not resume non-existent mission"
            )
        self.signal_resume_mission.set()

    def stop_mission(self):
        if self.mission_done:
            raise RobotNoMissionRunningException(
                error_description="Could not stop non-existent mission"
            )
        time.sleep(settings.MISSION_SIMULATION_TIME_TO_STOP)
        self.signal_stop_mission.set()
        self.signal_resume_mission.set()
        self.join()

    def task_status(self, task_id: str):
        task_index = self.task_id_mapping[task_id]
        if task_index < 0 or task_index > self.n_tasks - 1:
            raise RobotTaskStatusException(
                error_description="Task ID did not match any ongoing tasks"
            )
        return self.task_statuses[task_index]

    def current_task(self):
        if self.task_index < self.n_tasks:
            return self.mission.tasks[self.task_index]
        return None

    def mission_status(self):
        if not self.signal_resume_mission.wait(0):
            return MissionStatus.Paused
        if all(map(lambda status: status == TaskStatus.NotStarted, self.task_statuses)):
            return MissionStatus.NotStarted
        if not self.mission_done:
            return MissionStatus.InProgress
        if all(map(lambda status: status == TaskStatus.Successful, self.task_statuses)):
            return MissionStatus.Successful
        if any(
            map(
                lambda status: status in [TaskStatus.InProgress, TaskStatus.NotStarted],
                self.task_statuses,
            )
        ):
            return MissionStatus.InProgress
        if all(map(lambda status: status == TaskStatus.Failed, self.task_statuses)):
            return MissionStatus.Failed
        if any(map(lambda status: status == TaskStatus.Cancelled, self.task_statuses)):
            return MissionStatus.Cancelled
        if any(map(lambda status: status == TaskStatus.Failed, self.task_statuses)):
            return MissionStatus.PartiallySuccessful
        raise RobotMissionStatusException("Unhandled mission status detected")

    def _complete_task(self, task_status: TaskStatus):
        if self.task_index < self.n_tasks:
            self.task_statuses[self.task_index] = task_status
            self.task_index = self.task_index + 1
        if self.task_index >= self.n_tasks:
            self.all_tasks_done = True
        else:
            self.task_statuses[self.task_index] = TaskStatus.InProgress

    def run(self):
        self.mission_started = True

        if self.signal_stop_mission.is_set():
            self.mission_done = True
            return

        thread_check_interval = settings.MISSION_SIMULATION_TASK_DURATION
        self.task_statuses[0] = TaskStatus.InProgress
        while not self.signal_stop_mission.wait(thread_check_interval):
            if self.all_tasks_done:
                break
            time.sleep(settings.MISSION_SIMULATION_MISSION_COMPLETION_DELAY)

            self.signal_resume_mission.wait()

            if self.signal_stop_mission.is_set():
                break

            if self.is_return_home:
                # evaluate is return home failure probability
                if random.random() < self.return_home_task_failure_probability:
                    self._complete_task(TaskStatus.Failed)
                continue

            # evaluate task failure probability
            if random.random() < self.task_failure_probability:
                self._complete_task(TaskStatus.Failed)

            self._complete_task(TaskStatus.Successful)

        time.sleep(settings.MISSION_SIMULATION_MISSION_COMPLETION_DELAY)
        self.mission_done = True
        self.logger.info("Exiting mission simulation thread")
