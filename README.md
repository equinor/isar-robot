# isar-robot

[ISAR](https://github.com/equinor/isar) - Integration and Supervisory control of Autonomous Robots - is a tool for integrating robot applications into Equinor systems. Through the ISAR API you can send command to a robot to do missions and collect results from the missions.

Running the full ISAR system requires an installation of a robot which satisfies the required [interface](https://github.com/equinor/isar/blob/main/src/robot_interface/robot_interface.py). isar-robot is a default implementation of such a robot.

# Installation

For installation of isar-robot to use with ISAR, please follow the robot integration [installation guide](https://github.com/equinor/isar#robot-integration).

# Run isar-robot

After installing isar-robot, it can be used through [ISAR](https://github.com/equinor/isar).

# Development

For local development, create a fork of the repository and clone the fork to your machine:

```bash
git clone https://github.com/<your-username>/isar-robot
cd isar-robot
```

It is recommended to create a virtual environment, see a guide for this here: https://docs.python.org/3/library/venv.html.

Then install the requirements and the package:

```bash
pip install -r requirements.txt -e .[dev]
```

## Configurable variables

Specific mission and step behaviours can be configured as enviorment variables. These are optional and do not have to be set. These allow for always failing specific mission types, failing specific step types, setting custom step durations, and setting custom mission durations. The following list shows all configurable environment variables. In this case "normal" means non-localization or return to home tasks.

The variable names and types are as follows: 
```env
STEP_DURATION_IN_SECONDS: float
MISSION_DURATION_IN_SECONDS: float
SHOULD_FAIL_NORMAL_STEP: bool
SHOULD_FAIL_NORMAL_MISSION: bool
SHOULD_FAIL_LOCALIZATION_STEP: bool
SHOULD_FAIL_LOCALIZATION_MISSION: bool
SHOULD_FAIL_RETURN_TO_HOME_STEP: bool 
SHOULD_FAIL_RETURN_TO_HOME_MISSION: bool
```

Every configuration variable is defined in [settings.py](https://github.com/equinor/isar-robot/blob/main/src/isar_robot/config/settings.py), and they may all be overwritten by specifying the variables in your ".env" file in [ISAR](https://github.com/equinor/isar). Note that the configuration variable must be prefixed with ROBOT_ when specified in the ISAR environment file.

# Dependencies

The dependencies used for this package are listed in `pyproject.toml` and pinned in `requirements.txt`. This ensures our builds are predictable and deterministic. This project uses `pip-compile` (from [`pip-tools`](https://github.com/jazzband/pip-tools)) for this:

```
pip-compile --output-file=requirements.txt pyproject.toml
```

To update the requirements to the latest versions, run the same command with the `--upgrade` flag:

```
pip-compile --output-file=requirements.txt pyproject.toml --upgrade
```

# Contributing

We welcome all kinds of contributions, including code, bug reports, issues, feature requests, and documentation. The preferred way of submitting a contribution is to either make an [issue on github](https://github.com/equinor/isar-robot/issues) or by forking the project on github and making a pull request.
