from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.step import Localize, Step


def is_localization_mission(mission: Mission):
    if len(mission.tasks) != 1:
        return False
    if len(mission.tasks[0].steps) != 1:
        return False
    if not isinstance(mission.tasks[0].steps[0], Localize):
        return False
    return True


def is_localization_step(step: Step):
    return isinstance(step, Localize)
