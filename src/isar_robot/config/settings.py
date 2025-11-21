from importlib.resources import as_file, files

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    def __init__(self) -> None:
        try:
            source = files("isar_robot").joinpath("config").joinpath("settings.env")
            with as_file(source) as eml:
                env_file = eml
        except ModuleNotFoundError:
            env_file = None
        super().__init__(_env_file=env_file)

    MISSION_SIMULATION_TASK_DURATION: float = Field(default=5.0)
    INITIATE_MISSION_DURATION_IN_SECONDS: float = Field(default=0.1)
    SHOULD_HAVE_RANDOM_BATTERY_LEVEL: bool = Field(default=False)
    ROBOT_POSE_PUBLISH_INTERVAL: float = Field(default=1)
    ROBOT_BATTERY_PUBLISH_INTERVAL: float = Field(default=2)
    ROBOT_OBSTACLE_STATUS_PUBLISH_INTERVAL: float = Field(default=10)
    ROBOT_PRESSURE_PUBLISH_INTERVAL: float = Field(default=20)
    MISSION_SIMULATION_TIME_TO_START: float = Field(default=5.0)
    MISSION_SIMULATION_TIME_TO_STOP: float = Field(default=2.0)
    SHOULD_SIMULATE_INSPECTION_CALLBACK_CRASH: bool = Field(default=False)

    # This is the time from the last task finishing to the mission finishing
    MISSION_SIMULATION_MISSION_COMPLETION_DELAY: float = Field(default=2.0)
    MISSION_SIMULATION_SHOULD_FAIL_RETURN_TO_HOME_TASK: bool = Field(default=False)
    MISSION_SIMULATION_SHOULD_FAIL_NORMAL_TASK: bool = Field(default=False)
    MISSION_SIMULATION_TASK_FAILURE_PROBABILITY: float = Field(default=0.0)

    # This will cause delay between 0 and 5 seconds
    MISSION_SIMULATION_API_DELAY_MODIFIER: float = Field(default=5.0)

    model_config = SettingsConfigDict(
        env_prefix="ROBOT_",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
