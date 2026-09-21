# ROS 2 installation

Install ROS 2 Humble on the Pi. This lets it run autonomy code and talk to the
Pixhawk and any other robots on the network.

Run everything here in your SSH session on the Pi. Nothing on this page is specific
to the Raspberry Pi, so it works on any Ubuntu 22.04 machine.

## 1. Set the locale

ROS 2 needs a UTF-8 locale:

```bash
locale  # check for UTF-8

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale  # verify
```

## 2. Enable the universe repository

ROS 2 depends on packages from Ubuntu's `universe` repository, which is off by
default on server images:

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
```

## 3. Add the ROS 2 repository

This tells apt where to find the ROS 2 packages. ROS ships the repository settings
and signing key as a `.deb` file, so you no longer add them by hand:

```bash
sudo apt update && sudo apt install curl -y

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')

curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb
```

The second command looks up the latest version number. The third builds a download
link from that version and your Ubuntu codename (`jammy` for 22.04). Both need
internet access from the Pi itself, not just from your laptop.

## 4. Install ROS 2

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-ros-base ros-dev-tools
```

`ros-humble-ros-base` is ROS 2 without the desktop tools. There is no point
installing RViz and other GUI programs on a headless flight computer, and the Pi Zero
2 W does not have the resources for them.

`ros-dev-tools` gives you the build tools, including `colcon`, which you need later
for [px4_msgs](ground-station.md).

This takes a while on a Pi Zero 2 W. Let it finish.

## 5. Load ROS 2 automatically

You have to load the ROS 2 environment in every terminal before `ros2` commands work.
Adding it to `.bashrc` does that for you.

This only adds the line if it is not already there, so it is safe to run twice:

```bash
LINE='source /opt/ros/humble/setup.bash'
FILE=~/.bashrc
grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
source "$FILE"
```

## 6. Check it worked

```bash
ros2 --help
```

You should see a list of ROS 2 commands.

If you get `ros2: command not found`, the environment did not load. Open a new SSH
session, or run `source /opt/ros/humble/setup.bash` yourself.

## Next

[Wire the Pixhawk to the Pi](serial-connection.md)
