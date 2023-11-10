from robot_interface.test_robot_interface import interface_test

from isar_robot.robotinterface import Robot


def test_robotinterface():
    interface_test(Robot())
