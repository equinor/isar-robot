from robot_interface.models.mission.status import MissionStatus, RobotStatus
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


def test_robot_status_is_busy_while_a_mission_is_paused(mocker):
    """A paused mission must not be reported with a status that does not exist.

    RobotStatus has no Paused member, so returning one raises AttributeError.
    That is not a RobotException, so it escapes the handler in ISAR's robot
    status thread, the thread dies, and ISAR's watchdog shuts the process down.
    """
    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")

    simulation = mocker.Mock()
    simulation.mission_done = False
    simulation.mission_status.return_value = MissionStatus.Paused
    robot.mission_simulation = simulation

    assert robot.robot_status() == RobotStatus.Busy


def test_robot_status_is_busy_while_a_mission_is_running(mocker):
    robot = Robot(robot_name="Robot", isar_id="00000000-0000-0000-0000-000000000000")

    simulation = mocker.Mock()
    simulation.mission_done = False
    simulation.mission_status.return_value = MissionStatus.InProgress
    robot.mission_simulation = simulation

    assert robot.robot_status() == RobotStatus.Busy
