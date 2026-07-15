FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG ROS_DISTRO=jazzy
ARG USERNAME=rosuser
ARG USER_UID=1000
ARG USER_GID=1000

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV ROS_DISTRO=${ROS_DISTRO}
ENV ROS_WS=/workspace/ros2_ws

SHELL ["/bin/bash", "-c"]

# Install the minimal tools required to configure Ubuntu
# and ROS package repositories.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        locales \
        lsb-release \
        software-properties-common \
    && locale-gen en_US.UTF-8 \
    && add-apt-repository -y universe \
    && curl -fsSL \
        https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo ${UBUNTU_CODENAME}) main" \
        > /etc/apt/sources.list.d/ros2.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        sudo \
        build-essential \
        cmake \
        git \
        nodejs \
        python3 \
        python3-colcon-common-extensions \
        python3-pip \
        python3-rosdep \
        python3-vcstool \
        ros-${ROS_DISTRO}-ros-base \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep. It may already be initialized in a reused layer.
RUN rosdep init 2>/dev/null || true \
    && rosdep update --rosdistro ${ROS_DISTRO}

# Copy only the package manifest first so dependency installation
# remains cached until package dependencies change.
WORKDIR /tmp/rosdep_workspace

COPY ros2_ws/src/cpp_robotics_sim_ros/package.xml \
    src/cpp_robotics_sim_ros/package.xml

RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
    && apt-get update \
    && rosdep install \
        --from-paths src \
        --ignore-src \
        --rosdistro ${ROS_DISTRO} \
        --as-root apt:false \
        -r \
        -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/rosdep_workspace

# Create or reuse a non-root development user.
# Ubuntu base images may already reserve UID/GID 1000.
RUN if getent group "${USER_GID}" >/dev/null; then \
        DEVELOPMENT_GROUP="$(getent group "${USER_GID}" | cut -d: -f1)"; \
    else \
        groupadd --gid "${USER_GID}" "${USERNAME}"; \
        DEVELOPMENT_GROUP="${USERNAME}"; \
    fi \
    && if getent passwd "${USER_UID}" >/dev/null; then \
        EXISTING_USER="$(getent passwd "${USER_UID}" | cut -d: -f1)"; \
        if [ "${EXISTING_USER}" != "${USERNAME}" ]; then \
            usermod --login "${USERNAME}" "${EXISTING_USER}"; \
            usermod \
                --home "/home/${USERNAME}" \
                --move-home \
                "${USERNAME}"; \
        fi; \
        usermod --gid "${DEVELOPMENT_GROUP}" "${USERNAME}"; \
        usermod --shell /bin/bash "${USERNAME}"; \
    else \
        useradd \
            --uid "${USER_UID}" \
            --gid "${DEVELOPMENT_GROUP}" \
            --create-home \
            --shell /bin/bash \
            "${USERNAME}"; \
    fi \
    && echo \
        "${USERNAME} ALL=(ALL) NOPASSWD:ALL" \
        > "/etc/sudoers.d/${USERNAME}" \
    && chmod 0440 "/etc/sudoers.d/${USERNAME}"

WORKDIR /workspace

COPY --chown=${USER_UID}:${USER_GID} . /workspace

USER ${USERNAME}

# Verify source syntax and compile the ROS 2 package during image creation.
RUN ./scripts/check_syntax.sh \
    && source /opt/ros/${ROS_DISTRO}/setup.bash \
    && cd ${ROS_WS} \
    && colcon build \
        --packages-select cpp_robotics_sim_ros \
        --cmake-args -DBUILD_TESTING=ON \
        --event-handlers console_direct+

# Automatically source ROS and the built workspace in interactive shells.
RUN printf '%s\n' \
    "source /opt/ros/${ROS_DISTRO}/setup.bash" \
    "if [ -f ${ROS_WS}/install/setup.bash ]; then" \
    "  source ${ROS_WS}/install/setup.bash" \
    "fi" \
    >> /home/${USERNAME}/.bashrc

WORKDIR /workspace

CMD ["/bin/bash"]
