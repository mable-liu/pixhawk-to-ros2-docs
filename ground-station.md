# Ground station

How to read the PX4 topics from a computer other than the Pi. This is what makes the
Pi useful as part of a larger system instead of an isolated board.

You need two things: the PX4 message definitions, and working ROS 2 discovery across
your network.

## Requirements

The other computer needs **Ubuntu 22.04 with ROS 2 Humble**, the same as the Pi. ROS
2 versions do not talk to each other, so a machine running Jazzy or Foxy will not
work.

Install it the same way as on the Pi, see [ROS 2 installation](ros2-install.md). On a
desktop you can use `ros-humble-desktop` instead of `ros-humble-ros-base` to get RViz
and the other GUI tools.

(px4-msgs-install)=
## Install px4_msgs

`ros2 topic list` works without any message packages because it only reads topic
names. Actually reading a topic needs its definition. Any computer that subscribes to
PX4 topics needs `px4_msgs` installed.

:::{admonition} Match the version to your firmware
:class: important
PX4's message definitions change between releases. If you build `px4_msgs` from the
wrong branch, the topics will show up in `ros2 topic list` but you will not be able to
read them. `ros2 topic echo` will print nothing, or garbage, or an error.

Get your firmware version with `ver all` in the QGroundControl MAVLink console
([details](xrce-dds-agent.md#check-your-px4-version)), then use the matching
`release/x.y` branch.
:::

```bash
mkdir -p ~/ws_px4/src
cd ~/ws_px4/src

# Change release/1.15 to match your PX4 version
git clone -b release/1.15 https://github.com/PX4/px4_msgs.git

cd ~/ws_px4
source /opt/ros/humble/setup.bash
colcon build
```

Then load it on top of the base ROS 2 environment:

```bash
source ~/ws_px4/install/local_setup.bash
```

To do that automatically in new terminals:

```bash
echo 'source ~/ws_px4/install/local_setup.bash' >> ~/.bashrc
```

:::{note}
Build `px4_msgs` on the ground station, not the Pi. The Pi only runs the agent, which
does not need the message definitions, and `colcon build` is painfully slow on 512 MB
of RAM.
:::

## ROS 2 discovery

For the ground station to see the Pi's topics, both machines need to be on the same
network and agree on their discovery settings.

### Domain ID

ROS 2 splits the network up using `ROS_DOMAIN_ID`. Machines with different IDs cannot
see each other, even on the same network. If you do not set it, it defaults to `0`.

```bash
export ROS_DOMAIN_ID=<id>
```

:::{important}
Any number from 0 to 101 works. What matters is that every machine that needs to see
the others uses the same one.

If you are running several robots on one network, give each robot its own ID so they
do not interfere with each other. To check what a machine is currently using, run
`env | grep ROS`.
:::

Add the same line to `~/.bashrc` on both machines. The
[systemd service](autostart.md) needs it too, since services do not read `.bashrc`.

### Multicast on the Wi-Fi network

ROS 2 finds other machines using multicast. Many routers and access points block
multicast between wireless devices, which causes a confusing problem: everything
works over Ethernet or on one machine, but topics never appear over Wi-Fi.

To check whether multicast gets through:

```bash
# On the ground station
ros2 multicast receive

# On the Pi, in another terminal
ros2 multicast send
```

If the receiver prints the message, discovery will work. If it hangs, your network is
blocking multicast and you will need a discovery server or a list of peer addresses.
Ask whoever runs the network which approach to use.

## Check you are getting real data

With the [agent running on the Pi](xrce-dds-agent.md), on the ground station:

```bash
source /opt/ros/humble/setup.bash
source ~/ws_px4/install/local_setup.bash
ros2 topic list
```

The `/fmu/...` topics should appear. Now check that data is actually flowing:

```bash
ros2 topic echo /fmu/out/vehicle_attitude
```

Tilt the Pixhawk or the drone by hand. The numbers under `q` should change as you
move it:

```text
timestamp: 1754353900123456
q:
- 0.9987
- 0.0142
- -0.0451
- 0.0033
```

If those numbers move, the whole chain works: sensor to PX4, down the serial cable,
through the agent, across the network, into your terminal.

If the numbers do not change, or nothing prints, see
[Troubleshooting](troubleshooting.md#topics-appear-but-echo-is-empty).

Press {kbd}`Ctrl` + {kbd}`C` to stop.
