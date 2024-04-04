import importlib.resources as pkg_resources

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    def __init__(self) -> None:
        try:
            with pkg_resources.path(f"isar_robot.config", "settings.env") as path:
                env_file_path = path
        except ModuleNotFoundError:
            env_file_path = None
        super().__init__(_env_file=env_file_path)

    STEP_DURATION_IN_SECONDS: float = Field(default=5.0)
    MISSION_DURATION_IN_SECONDS: float = Field(default=5.0)
    SHOULD_FAIL_NORMAL_MISSION: bool = Field(default=False)
    SHOULD_FAIL_LOCALIZATION_MISSION: bool = Field(default=False)
    SHOULD_FAIL_NORMAL_STEP: bool = Field(default=False)
    SHOULD_FAIL_LOCALIZATION_STEP: bool = Field(default=False)
    SHOULD_FAIL_RETURN_TO_HOME_STEP: bool = Field(default=False)
    SHOULD_FAIL_RETURN_TO_HOME_MISSION: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_prefix="ROBOT_",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
