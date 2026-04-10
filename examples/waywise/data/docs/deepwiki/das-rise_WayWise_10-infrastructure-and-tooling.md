# Source: https://deepwiki.com/das-rise/WayWise/10-infrastructure-and-tooling

This section provides an overview of the build systems, continuous integration workflows, and external software components that support the WayWise library. The project relies on **CMake** for build configuration and **GitHub Actions** for automated validation across multiple Ubuntu distributions.

WayWise utilizes GitHub Actions to ensure code quality and buildability for the library itself and its primary consumers: the `RCCar`

(on-vehicle autopilot) and `ControlTower`

(ground station) applications.

The CI pipeline is defined in .github/workflows/main.yml1-97 It executes a build matrix targeting **Ubuntu 22.04** and **Ubuntu 24.04** .github/workflows/main.yml18 The workflow automates the following steps:

`qtbase5-dev`

, `libqt5serialport5-dev`

, `libboost-program-options-dev`

, and `libgpiod-dev`

.github/workflows/main.yml22 .github/workflows/main.yml45`libmavsdk-dev`

(v2.10.2) to satisfy communication requirements .github/workflows/main.yml25`iso22133`

) .github/workflows/main.yml29`Release`

mode .github/workflows/main.yml32-35A helper script, `try_build_all_cpp.sh`

, is provided to quickly verify that all `.cpp`

files in the project can be preprocessed correctly with the necessary Qt5 and system headers tools/try_build_all_cpp.sh1-5

For details on the CMake structure and packaging, see **[CI/CD & Build System (#10.1)]**.

**Sources:**

While modern versions of WayWise can use pre-built MAVSDK packages, the codebase includes specialized scripts for generating custom Debian packages (`.deb`

) for various architectures. This is particularly useful for ARM-based embedded systems like the Raspberry Pi.

The tools located in `tools/build_MAVSDK/`

allow for local or containerized builds:

`create_amd64-deb.sh`

builds MAVSDK locally tools/build_MAVSDK/create_amd64-deb.sh1-8 while `docker_create_amd64-deb.sh`

uses a Docker container to ensure a clean environment tools/build_MAVSDK/docker_create_amd64-deb.sh1-3`dockcross_create_arm64-deb.sh`

and `dockcross_create_armv7-deb.sh`

utilize `dockcross`

containers to build packages for 64-bit and 32-bit ARM platforms respectively tools/build_MAVSDK/dockcross_create_arm64-deb.sh1-8 tools/build_MAVSDK/dockcross_create_armv7-deb.sh1-8The following diagram illustrates how the build infrastructure interacts with the MAVSDK dependency required by the `MavsdkVehicleServer`

and `MavsdkStation`

classes.

**Build Tooling Relationship**

**Sources:**

WayWise incorporates several external libraries to handle hardware-specific protocols and sensor fusion. These are primarily located in the `ext/`

or `external/`

directories.

`BNO055`

IMU, `AS5600`

magnetic encoder, and `VL53L0X`

Time-of-Flight sensors.The following diagram maps these external libraries to the internal classes that wrap their functionality.

**External Library Integration**

For a full inventory and licensing information, see **[External Dependencies & Libraries (#10.2)]**.

**Sources:**

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.