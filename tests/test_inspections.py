from alitra import Frame, Position
from robot_interface.models.mission.step import TakeImage

from isar_robot import inspections


def test_create_image():
    target = Position(x=0, y=0, z=0, frame=Frame("robot"))
    step = TakeImage(target=target)

    inspections.create_image(step=step)
