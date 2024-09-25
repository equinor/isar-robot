from robot_interface.models.mission.mission import Mission
from robot_interface.models.mission.task import Task
from robot_interface.models.mission.task import Localize, ReturnToHome


def is_localization_mission(mission: Mission):
    if len(mission.tasks) != 1:
        return False
    if isinstance(mission.tasks[0], Localize):
        return True
    return False


def is_localization_task(task: Task):
    return isinstance(task, Localize)


def is_return_to_home_mission(mission: Mission):
    if len(mission.tasks) != 1:
        return False
    if isinstance(mission.tasks[0], ReturnToHome):
        return True
    return False


def is_return_to_home_task(task: Task):
    return isinstance(task, ReturnToHome)
