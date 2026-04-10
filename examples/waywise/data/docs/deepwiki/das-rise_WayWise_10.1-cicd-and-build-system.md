# Source: https://deepwiki.com/das-rise/WayWise/10.1-cicd-and-build-system

The WayWise build system is centered around **CMake**, utilizing **GitHub Actions** for continuous integration across multiple Ubuntu distributions. The system manages dependencies for both the core library and its primary downstream applications, `RCCar`

and `ControlTower`

, while providing specialized tooling for cross-compiling hardware-specific dependencies like MAVSDK.

The primary CI pipeline is defined in .github/workflows/main.yml1-96 It employs a build matrix to ensure compatibility across different LTS versions of Ubuntu and validates three distinct components: the built-in examples, the `RCCar`

(on-vehicle) application, and the `ControlTower`

(ground station) application.

The workflow runs on a matrix of operating systems:

`ubuntu-22.04`

`ubuntu-24.04`

All builds are performed in `Release`

mode by default, as specified by the `BUILD_TYPE`

environment variable .github/workflows/main.yml11-18

The CI is divided into three parallel jobs:

| Job | Description | Key Dependencies |
|---|---|---|
`build_examples` | Validates the examples provided within the WayWise repository. | `qtbase5-dev` , `libqt5serialport5-dev` , `libboost-program-options-dev` .github/workflows/main.yml22 |
`build_rccar` | Builds the external `RCCar` repository with WayWise as a component. | `libgpiod-dev` , `libqt5serialport5-dev` .github/workflows/main.yml45 |
`build_controltower` | Builds the external `ControlTower` repository (GUI). | `qtmultimedia5-dev` , `libqt5gamepad5-dev` .github/workflows/main.yml75 |

Since WayWise relies heavily on MAVSDK for vehicle communication, the CI manually fetches and installs a specific Debian package (`v2.10.2`

) before triggering CMake .github/workflows/main.yml25 .github/workflows/main.yml48 .github/workflows/main.yml78

The following diagram illustrates how the GitHub Actions runner orchestrates the build across different repository structures.

**CI Build Pipeline**

**Sources:** .github/workflows/main.yml14-96

WayWise uses a standard CMake configuration. While the core library is intended to be included as a subdirectory in larger projects (like `RCCar`

or `ControlTower`

), it maintains its own internal structure for examples.

Standard configuration follows the pattern:

`cmake -S <source_dir> -B <build_dir> -DCMAKE_BUILD_TYPE=Release`

.github/workflows/main.yml32`cmake --build <build_dir> --config Release`

.github/workflows/main.yml35The build system expects submodules to be initialized recursively, particularly for external dependencies like `iso22133`

.github/workflows/main.yml29

While MAVSDK now provides official releases, WayWise includes a suite of scripts in `tools/build_MAVSDK/`

for creating custom Debian packages. This is particularly useful for ARM-based targets (Raspberry Pi, Jetson) where official binaries might not match the required OS version tools/build_MAVSDK/README.md1-7

`create_amd64-deb.sh`

: Builds MAVSDK locally on an x86_64 machine. It disables the MAVSDK server and enables shared libraries tools/build_MAVSDK/create_amd64-deb.sh4-5`docker_create_amd64-deb.sh`

: Wraps the build in a Docker container (`mavsdk/mavsdk-ubuntu-22.04`

) to ensure a clean environment tools/build_MAVSDK/docker_create_amd64-deb.sh2`dockcross_create_arm64-deb.sh`

: Uses `arm64`

(e.g., Debian 11/Ubuntu 22.04 on Raspberry Pi) tools/build_MAVSDK/dockcross_create_arm64-deb.sh3-4`dockcross_create_armv7-deb.sh`

: Similar to the arm64 script, but targets 32-bit `armv7`

architectures tools/build_MAVSDK/dockcross_create_armv7-deb.sh3-4**MAVSDK Build Tooling Entity Map**

**Sources:** tools/build_MAVSDK/README.md9-17 tools/build_MAVSDK/create_amd64-deb.sh1-8 tools/build_MAVSDK/dockcross_create_arm64-deb.sh1-8

This script is a lightweight diagnostic tool used to verify that all `.cpp`

files in the repository can be pre-processed/compiled individually against the required Qt5 headers. It iterates through the source tree and attempts to compile each file into a temporary object `test.o`

tools/try_build_all_cpp.sh1-5

It specifically includes paths for:

`QtCore`

`QtSerialPort`

`QtNetwork`

`QtGui`

`QtWidgets`

**Sources:** tools/try_build_all_cpp.sh2

The project uses GitHub's issue and pull request templates to maintain code quality:

**Sources:** .github/ISSUE_TEMPLATE/bug_report.md1-33 .github/PULL_REQUEST_TEMPLATE.md1-20

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.