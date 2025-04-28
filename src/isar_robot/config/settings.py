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

    TASK_DURATION_IN_SECONDS: float = Field(default=5.0)
    INITIATE_MISSION_DURATION_IN_SECONDS: float = Field(default=0.1)
    SHOULD_FAIL_NORMAL_MISSION: bool = Field(default=False)
    SHOULD_FAIL_NORMAL_TASK: bool = Field(default=False)
    SHOULD_FAIL_RETURN_TO_HOME_TASK: bool = Field(default=False)
    SHOULD_FAIL_RETURN_TO_HOME_MISSION: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_prefix="ROBOT_",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
