from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.step import Localize, ReturnToHome, Step


def is_localization_mission(mission: Mission):
    if mission.start_pose is not None:
        return True

    return False


def is_localization_step(step: Step):
    return isinstance(step, Localize)


def is_return_to_home_mission(mission: Mission):
    if len(mission.tasks) != 1:
        return False
    if len(mission.tasks[0].steps) != 1:
        return False
    if not isinstance(mission.tasks[0].steps[0], ReturnToHome):
        return False
    return True


def is_return_to_home_step(step: Step):
    return isinstance(step, ReturnToHome)
