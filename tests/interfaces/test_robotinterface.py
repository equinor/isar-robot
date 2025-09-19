from robot_interface.test_robot_interface import interface_test

from isar_robot.robotinterface import Robot


def test_robotinterface():
    interface_test(Robot())


def test_get_telemetry_publishers():
    robot = Robot()
    publishers = robot.get_telemetry_publishers(
        queue=None, isar_id="test_id", robot_name="test_robot"
    )
    assert len(publishers) == 4


def test_pose_telemetry():
    robot = Robot()
    pose_telemetry = robot._get_pose_telemetry(
        isar_id="test_id", robot_name="test_robot"
    )
    assert pose_telemetry is not None


def test_battery_telemetry():
    robot = Robot()
    battery_telemetry = robot._get_battery_telemetry(
        isar_id="test_id", robot_name="test_robot"
    )
    assert battery_telemetry is not None


def test_obstacle_status_telemetry():
    robot = Robot()
    obstacle_status_telemetry = robot.telemetry.get_obstacle_status_telemetry(
        isar_id="test_id", robot_name="test_robot"
    )
    assert obstacle_status_telemetry is not None


def test_pressure_telemetry():
    robot = Robot()
    pressure_telemetry = robot.telemetry.get_pressure_telemetry(
        isar_id="test_id", robot_name="test_robot"
    )
    assert pressure_telemetry is not None
