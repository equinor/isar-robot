FROM isar-base:latest

ARG ROBOT_REPOSITORY_CLONE_URL=https://github.com/equinor/isar-robot.git

RUN pip install git+${ROBOT_REPOSITORY_CLONE_URL}@main

RUN useradd -ms /bin/bash --uid 1001 isar
RUN chown -R 1001 /app
RUN chmod 755 /app
USER 1001
