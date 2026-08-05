# Ground station

Reading the PX4 topics from a computer other than the Pi. This is what makes the Pi
useful as part of the lab's multi-robot system rather than an isolated board — once
DDS discovery works, any machine on the network can subscribe to the drone's
telemetry.

Two things are needed: the `px4_msgs` message definitions, and working ROS 2
discovery across the Wi-Fi network.

## Requirements

The ground station must run **Ubuntu 22.04 with ROS 2 Humble**, matching the Pi. ROS 2
distributions are not wire-compatible across releases, so a machine running Jazzy or
Foxy will not interoperate cleanly.

Install ROS 2 Humble on it the same way as on the Pi — see
[ROS 2 installation](ros2-install.md). On a desktop machine you can use
`ros-humble-desktop` instead of `ros-humble-ros-base` to get RViz and the GUI tools.

(px4-msgs-install)=
## Installing px4_msgs

`ros2 topic list` works without any message packages, because it only reads topic
names. Actually *reading* a topic needs its message definition. Any computer that
inspects, subscribes to, or publishes PX4 topics needs a matching `px4_msgs` build.

:::{admonition} The branch must match your PX4 version
:class: warning
PX4's message definitions change between releases. A `px4_msgs` built from the wrong
branch produces topics that appear in `ros2 topic list` but fail to deserialise —
`ros2 topic echo` then prints nothing, or garbage, or a type mismatch error.

The correct branch was not recorded for this setup. Get the firmware version with
`ver all` in the QGroundControl MAVLink console
([details](xrce-dds-agent.md#confirming-the-px4-version)), then check out the
matching `release/x.y` branch below.
:::

```bash
mkdir -p ~/ws_px4/src
cd ~/ws_px4/src

# Replace release/1.15 with the branch matching your PX4 firmware version
git clone -b release/1.15 https://github.com/PX4/px4_msgs.git

cd ~/ws_px4
source /opt/ros/humble/setup.bash
colcon build
```

Then source the workspace on top of the base ROS 2 environment:

```bash
source ~/ws_px4/install/local_setup.bash
```

To make that automatic in new terminals:

```bash
echo 'source ~/ws_px4/install/local_setup.bash' >> ~/.bashrc
```

:::{admonition} Build px4_msgs on the ground station, not the Pi
:class: note
`colcon build` on 512 MB of RAM is painful and mostly unnecessary — the Pi runs the
agent, which does not need the message definitions. Build `px4_msgs` on the machine
that will actually subscribe.
:::

## ROS 2 discovery across the network

For the ground station to see the Pi's topics, both must be on the same Wi-Fi network
*and* agree on their DDS discovery settings.

### Domain ID

ROS 2 partitions the network by `ROS_DOMAIN_ID`. Nodes on different domain IDs are
invisible to each other even on the same LAN. It defaults to `0` if unset, so an
unconfigured machine only talks to other unconfigured machines.

```bash
export ROS_DOMAIN_ID=<id>
```

Add the same line to `~/.bashrc` on **both** the Pi and the ground station, and note
that the [systemd service](autostart.md) needs it too — a service does not read your
`.bashrc`.

:::{admonition} Lab domain ID not recorded
:class: warning
This lab runs a multi-robot system, so the domain ID is likely set deliberately to
keep robots from interfering with each other. The value in use has not been captured.
Run `env | grep ROS` on the Pi to find it, and record it here.
:::

### Multicast on the lab Wi-Fi

Default DDS discovery relies on UDP multicast. Many managed access points block or
rate-limit multicast between wireless clients, which produces the most confusing
failure in this whole setup: everything works when both machines are on Ethernet, or
when both run on the Pi itself, but topics never appear across the wireless link.

Test whether multicast reaches between the machines:

```bash
# On the ground station
ros2 multicast receive

# On the Pi, in another terminal
ros2 multicast send
```

If the receiver prints the message, discovery will work. If it hangs, the network is
dropping multicast and you will need a discovery server or an explicit peers list —
ask whoever administers the lab network which approach the other robots use.

## Verifying real data

With the [agent running on the Pi](xrce-dds-agent.md), on the ground station:

```bash
source /opt/ros/humble/setup.bash
source ~/ws_px4/install/local_setup.bash
ros2 topic list
```

The `/fmu/...` topics should appear. Then confirm the data is live rather than just
the topic existing:

```bash
ros2 topic echo /fmu/out/vehicle_attitude
```

Tilt the Pixhawk or the drone by hand. The quaternion values under `q` should change
as you move it:

```text
timestamp: 1754353900123456
q:
- 0.9987
- 0.0142
- -0.0451
- 0.0033
```

Values that update as you move the airframe confirm the whole chain end to end —
sensor to uORB to serial link to agent to DDS to your terminal.

Static values, or no output at all, mean the topic exists but nothing is flowing. See
[Troubleshooting → Topics appear but echo is empty](troubleshooting.md#topics-appear-but-echo-is-empty).

Press {kbd}`Ctrl` + {kbd}`C` to stop.
