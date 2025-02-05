from robot_interface.models.mission.task import Task
from robot_interface.models.mission.task import ReturnToHome


def is_return_to_home_task(task: Task):
    return isinstance(task, ReturnToHome)
