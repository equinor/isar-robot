# isar-robot
[ISAR](https://github.com/equinor/isar) - Integration and Supervisory control of Autonomous Robots - is a tool for integrating robot applications into Equinor systems. Through the ISAR API you can send command to a robot to do missions and collect results from the missions.

Running the full ISAR system requires an installation of a robot which satisfies the required [interface](https://github.com/equinor/isar/blob/main/src/robot_interface/robot_interface.py). isar-robot is a default implementation of such a robot.

# Installation
For installation of isar-robot to use with ISAR, please follow the robot integration [installation guide](https://github.com/equinor/isar#robot-integration).

# Run isar-robot
After installing isar-robot, it can be used through [ISAR](https://github.com/equinor/isar).

# Development
For local development, please fork the repository. Then, clone and install in the repository root folder:

```bash
$ git clone https://github.com/equinor/isar-robot
$ cd isar-robot
$ pip install -r requirements-dev.txt
$ pip install -e .
```

# Contributing
We welcome all kinds of contributions, including code, bug reports, issues, feature requests, and documentation. The preferred way of submitting a contribution is to either make an issue on github or by forking the project on github and making a pull requests.
