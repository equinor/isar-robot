from robot_interface.robot_interface import RobotInterface
from isar_robot.robotinterface import Robot
from typing import Tuple


def test_robotinterface():
    robot: Robot = Robot()

    for func in dir(RobotInterface):
        if not callable(getattr(RobotInterface, func)) or func.startswith("__"):
            continue

        arg_robot: int = getattr(Robot, func).__code__.co_argcount
        arg_isar: int = getattr(RobotInterface, func).__code__.co_argcount

        args_robot: Tuple[str] = getattr(Robot, func).__code__.co_varnames[:arg_robot]
        args_isar: Tuple[str] = getattr(RobotInterface, func).__code__.co_varnames[
            :arg_isar
        ]

        assert arg_robot == arg_isar
        assert args_robot == args_isar
