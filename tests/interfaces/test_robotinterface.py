from alitra import Frame, Orientation, Pose, Position
from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.status import MissionStatus, RobotStatus, TaskStatus
from robot_interface.models.mission.task import TakeImage
from robot_interface.test_robot_interface import interface_test

from isar_robot.config.settings import settings
from isar_robot.robotinterface import Robot


def test_robotinterface():
    interface_test(
        Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")
    )


def test_get_telemetry_publishers():
    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")
    publishers = robot.get_telemetry_publishers()
    assert len(publishers) == 4


def test_pose_telemetry():
    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")
    pose_telemetry = robot._get_pose_telemetry()
    assert pose_telemetry is not None


def test_battery_telemetry():
    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")
    battery_telemetry = robot._get_battery_telemetry()
    assert battery_telemetry is not None


def test_obstacle_status_telemetry():
    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")
    obstacle_status_telemetry = robot.telemetry.get_obstacle_status_telemetry()
    assert obstacle_status_telemetry is not None


def test_pressure_telemetry():
    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")
    pressure_telemetry = robot.telemetry.get_pressure_telemetry()
    assert pressure_telemetry is not None


def test_initial_robot_status_defaults_to_available():
    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")
    assert robot.robot_status() == RobotStatus.Available


def test_initial_robot_status_is_home_when_should_start_at_home(mocker):
    mocker.patch.object(settings, "SHOULD_START_AT_HOME", True)
    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")
    assert robot.robot_status() == RobotStatus.Home


def test_mission_and_task_status_are_available_after_mission_is_stopped(mocker):
    mocker.patch.object(settings, "MISSION_SIMULATION_TIME_TO_START", 0.0)
    mocker.patch.object(settings, "MISSION_SIMULATION_TIME_TO_STOP", 0.0)
    mocker.patch.object(settings, "MISSION_SIMULATION_MISSION_COMPLETION_DELAY", 0.0)
    mocker.patch.object(settings, "MISSION_SIMULATION_TASK_DURATION", 10.0)

    robot_pose = Pose(
        Position(0, 0, 0, Frame("asset")),
        Orientation(x=0, y=0, z=0, w=1, frame=Frame("asset")),
        Frame("asset"),
    )
    task = TakeImage(
        id="task-id",
        target=Position(x=0, y=0, z=0, frame=Frame("robot")),
        robot_pose=robot_pose,
    )
    mission = Mission(id="mission-id", name="Mission", tasks=[task])

    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")
    robot.initiate_mission(mission)
    robot.stop()

    task_status = robot.task_status(task.id)
    mission_status = robot.mission_status(mission.id)

    assert task_status == TaskStatus.Cancelled
    assert mission_status == MissionStatus.Cancelled
    assert robot.robot_status() == RobotStatus.Available
