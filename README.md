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
