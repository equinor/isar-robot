from isar_robot.robotinterface import Robot
from robot_interface.test_robot_interface import interface_test


def test_robotinterface():
    interface_test(Robot())
