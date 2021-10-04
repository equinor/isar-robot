from robot_interfaces.robot_interface import (
    RobotInterface,
    RobotSchedulerInterface,
    RobotStorageInterface,
    RobotTelemetryInterface,
)


class Robot(RobotInterface):
    def __init__(self):
        self.scheduler = Scheduler()
        self.storage = Storage()
        self.telemetry = Telemetry()


class Scheduler(RobotSchedulerInterface):
    def schedule_step(self):
        raise NotImplementedError

    def mission_scheduled(self):
        raise NotImplementedError

    def mission_status(self):
        raise NotImplementedError

    def abort_mission(self):
        raise NotImplementedError

    def log_status(self):
        raise NotImplementedError



class Storage(RobotStorageInterface):
    def get_inspection_references(self):
        raise NotImplementedError

    def download_inspection_result(self):
        raise NotImplementedError



class Telemetry(RobotTelemetryInterface):
    def robot_pose(self):
        raise NotImplementedError

    def robot_joints(self):
        raise NotImplementedError
