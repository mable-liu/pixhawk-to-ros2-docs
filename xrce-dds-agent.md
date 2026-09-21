# Micro XRCE-DDS Agent

This is the bridge between PX4 and ROS 2. PX4 sends its internal messages down the
serial cable, and the agent turns them into ROS 2 topics. It works both ways, so ROS
2 nodes can also send commands back to PX4.

This replaces the [MAVLink setup](mavlink-bridge.md) on TELEM2.

## Check your PX4 version

The part of PX4 that does this only exists in **v1.14 and later**. On older firmware,
none of this will work.

Open QGroundControl's **Analyze → MAVLink Console** and run:

```bash
ver all
```

:::{important}
Write the version down. You need it later to pick the right version of `px4_msgs` in
[Ground station](ground-station.md), and getting that wrong causes problems that are
hard to track down.
:::

## PX4 settings

In QGroundControl over USB, go to **Vehicle Setup → Parameters** and change:

| Parameter | Value | What it does |
|---|---|---|
| `MAV_1_CONFIG` | `0` (Disabled) | Frees TELEM2 from MAVLink |
| `UXRCE_DDS_CFG` | `102` (TELEM2) | Runs the DDS client on TELEM2 |
| `SER_TEL2_BAUD` | `921600` | Speeds up the link |

The speed goes up because the DDS client sends far more data than MAVLink does.

:::{important}
Reboot the flight controller again. As before, PX4 only reads these settings at
startup.
:::

This higher speed is also why you disabled Bluetooth back in
[Serial connection](serial-connection.md#2-turn-on-the-uart-and-free-up-ttyama0). The
weaker UART cannot keep up at 921600 baud.

## Build the agent

The agent is not available as an Ubuntu package, so you build it yourself:

```bash
sudo apt install cmake git

git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
mkdir build && cd build
cmake ..
make
sudo make install
sudo ldconfig /usr/local/lib/
```

:::{admonition} Watch out on low-memory boards
:class: important
This is the step most likely to fail on a Pi Zero 2 W, which only has 512 MB of RAM.
If you speed up the build with `make -j4`, it will run out of memory and the build
will die with a confusing message about `cc1plus` being killed.

Use plain `make`, and if that still fails, add temporary swap space first:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

The swap disappears when you reboot, which is fine since you only need it for this
build. Remove it afterwards with `sudo swapoff /swapfile && sudo rm /swapfile` so it
does not wear out the SD card.

Either way, expect the build to be slow.
:::

Check it installed:

```bash
which MicroXRCEAgent
```

You should get `/usr/local/bin/MicroXRCEAgent`.

## Test the bridge

### 1. Check the PX4 side

In QGroundControl's **MAVLink console**:

```bash
uxrce_dds_client status
```

You should see:

```text
Running, connected
transport: serial
```

If it says running but not connected, PX4 is sending data but nothing is listening.
Start the agent and check again.

### 2. Start the agent

In your SSH session, run this and leave it going:

```bash
MicroXRCEAgent serial --dev /dev/serial0 -b 921600
```

You should see the session start, then a long list of topics being created:

```text
[1754353821.123456] info     | TermiosAgentLinux.cpp | init                     | running...             | fd: 3
[1754353822.456789] info     | Root.cpp           | create_client            | create                 | client_key: 0x00000001
[1754353822.567890] info     | SessionManager.hpp | establish_session        | session established    | client_key: 0x00000001
```

If you get a permission error, you skipped
[step 3 of the serial setup](serial-connection.md#3-give-your-user-access-to-the-serial-port).

### 3. List the topics

Open a **second** SSH session, leaving the agent running in the first:

```bash
source /opt/ros/humble/setup.bash
ros2 topic list
```

If it worked, the PX4 topics appear:

```text
/fmu/in/offboard_control_mode
/fmu/in/trajectory_setpoint
/fmu/in/vehicle_command
/fmu/out/failsafe_flags
/fmu/out/sensor_combined
/fmu/out/timesync_status
/fmu/out/vehicle_attitude
/fmu/out/vehicle_status
/parameter_events
/rosout
```

`/fmu/out/` topics come from PX4. `/fmu/in/` topics are ones you can publish to in
order to send commands.

If you only see `/parameter_events` and `/rosout`, the agent is running but PX4 is
not connected to it. Go back to step 1.

Press {kbd}`Ctrl` + {kbd}`C` to stop the agent.

## Next

Starting the agent by hand every time is impractical on a drone, so
[make it start automatically](autostart.md).

To read the topics from another computer, see [Ground station](ground-station.md).
