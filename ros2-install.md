# ROS 2 installation

Installing ROS 2 Humble on the Pi so it can act as the drone's companion computer,
run higher-level autonomy code, and talk to the Pixhawk and the rest of the lab's
multi-robot system.

All commands run in the SSH session on the Pi.

:::{admonition} Reconstructed from upstream documentation
:class: warning
The original notes recorded this as "configure the ROS 2 apt repository" without the
commands. The sequence below is the current procedure from the
[ROS 2 Humble install guide](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)
and has not been re-run on the lab Pi. It should work as written on a clean 22.04
image, but confirm it before treating this page as authoritative.
:::

## 1. Set the locale

ROS 2 requires a UTF-8 locale. Check what you have, and set one if needed:

```bash
locale  # check for UTF-8

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale  # verify settings
```

## 2. Enable the universe repository

The ROS 2 packages depend on packages from Ubuntu's `universe` component, which is
not enabled on a server image by default:

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
```

## 3. Add the ROS 2 apt repository

This is what lets Ubuntu's package manager find and verify the ROS 2 Humble packages.
ROS now distributes the repository definition and signing key as a `.deb`, rather
than having you add the key and source list by hand:

```bash
sudo apt update && sudo apt install curl -y

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')

curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb
```

The middle command queries GitHub for the newest release tag and the third builds a
download URL from that tag plus your Ubuntu codename (`jammy` on 22.04). If your Pi
has no outbound internet access, both will fail — this step needs working DNS and
HTTPS from the Pi itself, not just from your laptop.

## 4. Install ROS 2

Refresh the package lists against the newly added repository, then upgrade before
installing. The upgrade matters: ROS packages are built against current system
libraries, and installing onto a stale system pulls in conflicting versions.

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-ros-base ros-dev-tools
```

`ros-humble-ros-base`
: The bare ROS 2 install — no desktop tools, no GUI, no RViz. Suited to the limited
  CPU, RAM, and storage of the Pi Zero 2 W. The full `ros-humble-desktop` package
  would pull in visualisation tooling that a headless flight computer cannot use.

`ros-dev-tools`
: Tools for creating, building, and testing ROS 2 packages, including `colcon`,
  which is needed later to build [`px4_msgs`](ground-station.md).

:::{admonition} This step is slow
:class: note
Installing onto a Pi Zero 2 W over Wi-Fi takes a while — the board has a
single-core-class workload profile for `dpkg` unpacking and only 512 MB of RAM.
Leave it running rather than interrupting it.
:::

## 5. Source ROS 2 automatically

The ROS 2 environment has to be sourced in every shell before `ros2` commands work.
Adding it to `.bashrc` makes that happen automatically whenever a new terminal opens.

This snippet appends the line only if it is not already present, so running it twice
does not duplicate the entry:

```bash
LINE='source /opt/ros/humble/setup.bash'
FILE=~/.bashrc
grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
source "$FILE"
```

## 6. Verify

```bash
ros2 --help
```

Expected: a usage message listing the available ROS 2 commands and options
(`action`, `bag`, `node`, `param`, `run`, `topic`, and so on).

If you get `ros2: command not found`, the environment was not sourced — open a new
SSH session, or run `source /opt/ros/humble/setup.bash` by hand and try again.

## Next

Wire the Pixhawk to the Pi → [Serial connection](serial-connection.md)
