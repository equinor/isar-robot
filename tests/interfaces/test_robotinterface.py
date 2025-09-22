from alitra import Frame, Position

from robot_interface.test_robot_interface import interface_test
from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.task import TakeImage

from isar_robot.robotinterface import Robot

from time import sleep

dummy_position = Position(x=0, y=0, z=0, frame=Frame("asset"))
dummy_inspection_task = TakeImage(id="dummy_task", target=dummy_position)
dummy_mission = Mission(id="dummy", tasks=[dummy_inspection_task], name="Dummy Mission")


def test_robotinterface():
    interface_test(Robot())


def test_initiate_mission():
    robot = Robot()
    robot.initiate_mission(mission=dummy_mission)
    assert robot.mission_simulation is not None


def test_task_status():
    robot = Robot()
    robot.initiate_mission(mission=dummy_mission)
    status = robot.task_status(task_id="dummy_task")
    assert status is not None


def test_stop():
    robot = Robot()
    robot.initiate_mission(mission=dummy_mission)
    sleep(2)  # Give some time for the mission to start
    robot.stop()
    sleep(2)  # Give some time for the mission to stop
    assert robot.mission_simulation.mission_done is True


def test_get_inspection():
    robot = Robot()
    robot.initiate_mission(mission=dummy_mission)
    inspection = robot.get_inspection(task=dummy_inspection_task)
    assert inspection is not None


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


def test_robot_status():
    robot = Robot()
    status = robot.robot_status()
    assert status is not None


def test_pause() -> None:
    robot = Robot()
    robot.initiate_mission(mission=dummy_mission)
    robot.pause()
    assert robot.mission_simulation.mission_done is False


def test_resume() -> None:
    robot = Robot()
    robot.initiate_mission(mission=dummy_mission)
    robot.pause()
    robot.resume()
    assert robot.mission_simulation.mission_done is False
