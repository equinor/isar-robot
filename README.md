# isar-robot

[ISAR](https://github.com/equinor/isar) - Integration and Supervisory control of Autonomous Robots - is a tool for integrating robot applications into Equinor systems. Through the ISAR API you can send command to a robot to do missions and collect results from the missions.

Running the full ISAR system requires an installation of a robot which satisfies the required [interface](https://github.com/equinor/isar/blob/main/src/robot_interface/robot_interface.py). isar-robot is a default implementation of such a robot.

# Installation

For installation of isar-robot to use with ISAR, please follow the robot integration [installation guide](https://github.com/equinor/isar#robot-integration).

# Run isar-robot

After installing isar-robot, it can be used through [ISAR](https://github.com/equinor/isar).

# Development

Create a fork of the repository and clone the fork to your machine:

```bash
git clone https://github.com/<your-username>/isar-robot
cd isar-robot
```

Choose if you want to run via uv or manually creating venv

## Local development with uv

An easy way to run isar-robot locally is with [uv](https://docs.astral.sh/uv/). The `pyproject.toml` includes a `[tool.uv.sources]` override that points the `isar` dependency to the local `../isar` folder.

Note that this assumes the following folder structure between isar and isar-robot:

```
parent-folder/
├── isar/
└── isar-robot/
```

```bash
uv run isar-start
```

## Configurable variables

Specific mission and task behaviours can be configured as environment variables. These are optional and do not have to be set. These allow for always failing specific mission types, failing specific task types, setting custom task durations, and setting custom mission durations. The following list shows all configurable environment variables. In this case "normal" means non-localization or return to home tasks.

The variable names and types are as follows: 
```env
TASK_DURATION_IN_SECONDS: float
MISSION_DURATION_IN_SECONDS: float
SHOULD_FAIL_NORMAL_TASK: bool
SHOULD_FAIL_RETURN_TO_HOME_TASK: bool
```

Every configuration variable is defined in [settings.py](https://github.com/equinor/isar-robot/blob/main/src/isar_robot/config/settings.py), and they may all be overwritten by specifying the variables in your ".env" file in [ISAR](https://github.com/equinor/isar). Note that the configuration variable must be prefixed with ROBOT_ when specified in the ISAR environment file.

# Dependencies

The dependencies used for this package are listed in `pyproject.toml` and pinned in `uv.lock`. This ensures our builds are predictable and deterministic. This project uses [uv](https://docs.astral.sh/uv/) for dependency management:

```
uv lock
```

To update the dependencies to the latest versions, run:

```
uv lock --upgrade
```

# Contributing

We welcome all kinds of contributions, including code, bug reports, issues, feature requests, and documentation. The preferred way of submitting a contribution is to either make an [issue on github](https://github.com/equinor/isar-robot/issues) or by forking the project on github and making a pull request.
