from isar_robot import robotinterface


def test_robotinterface():
    robot = robotinterface.Robot()

    scheduler = robot.scheduler
    storage = robot.storage
    telemetry = robot.telemetry
