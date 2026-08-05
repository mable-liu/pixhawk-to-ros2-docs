# Autostart

Running the Micro XRCE-DDS Agent as a systemd service so it starts automatically
whenever the Pi boots.

Without this, every flight requires SSHing into the Pi and starting the agent by
hand, and the ROS 2 bridge dies the moment that SSH session closes. As a service, the
Pixhawk joins the ROS 2 network as soon as the drone powers up, with no laptop
involved.

:::{admonition} Unit file not recovered from the Pi
:class: warning
A working service exists on the lab Pi, but its unit file has not been read back. The
file below is a reconstruction from the manual command in
[Micro XRCE-DDS Agent](xrce-dds-agent.md#2-start-the-agent-on-the-pi) plus standard
systemd practice. Replace it with the real contents of
`/etc/systemd/system/*.service` when you next have access to the hardware.
:::

## The unit file

Create `/etc/systemd/system/micro-xrce-dds-agent.service`:

```bash
sudo nano /etc/systemd/system/micro-xrce-dds-agent.service
```

```ini
[Unit]
Description=Micro XRCE-DDS Agent (PX4 to ROS 2 bridge)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Environment="ROS_DOMAIN_ID=0"
ExecStart=/usr/local/bin/MicroXRCEAgent serial --dev /dev/serial0 -b 921600
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

What each part is doing:

`After` / `Wants=network-online.target`
: Waits for networking before starting. DDS needs a usable network interface to
  advertise on; starting earlier means the agent comes up on a machine with no
  network and never re-advertises.

`User=ubuntu`
: Runs as your normal user rather than root, which works because that user is in the
  `dialout` group from
  [Serial connection](serial-connection.md#3-grant-serial-access-to-your-user). If
  serial permissions were never granted, this is where it fails.

`Environment="ROS_DOMAIN_ID=0"`
: A systemd service does not read your `~/.bashrc`, so the domain ID set there is
  invisible to it. It has to be declared in the unit. **Set this to your lab's actual
  domain ID** — see [Ground station](ground-station.md#domain-id). Leaving it at the
  default while your ground station uses a different value means the agent runs
  perfectly and no one can see it.

`Restart=always` / `RestartSec=5`
: Restarts the agent if it exits — including at boot, when the service may start
  before the Pixhawk has finished powering up and `/dev/serial0` has anything on the
  other end.

## Enabling the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable micro-xrce-dds-agent.service
sudo systemctl start micro-xrce-dds-agent.service
```

`daemon-reload` makes systemd re-read unit files from disk — needed after creating or
editing one. `enable` sets it to start at boot; `start` runs it now without waiting
for a reboot.

## Verifying

Check the service state:

```bash
systemctl status micro-xrce-dds-agent.service
```

Expected: `Active: active (running)`, with recent agent output below.

```text
● micro-xrce-dds-agent.service - Micro XRCE-DDS Agent (PX4 to ROS 2 bridge)
     Loaded: loaded (/etc/systemd/system/micro-xrce-dds-agent.service; enabled)
     Active: active (running) since Mon 2026-08-04 22:10:03 UTC; 5s ago
   Main PID: 1180 (MicroXRCEAgent)
```

Follow the live log:

```bash
journalctl -u micro-xrce-dds-agent.service -f
```

A service stuck in a restart loop shows repeated start/exit lines here — usually a
permissions problem on `/dev/serial0`, or a wrong path in `ExecStart`.

Then confirm the whole chain still works, exactly as when the agent was started by
hand. In the QGroundControl MAVLink console:

```bash
uxrce_dds_client status
```

Expected:

```text
Running, connected
transport: serial
```

And from the [ground station](ground-station.md):

```bash
source /opt/ros/humble/setup.bash
ros2 topic list
ros2 topic echo /fmu/out/vehicle_attitude
```

Tilt the Pixhawk by hand and confirm the quaternion values under `q` change as it
moves. Press {kbd}`Ctrl` + {kbd}`C` to stop.

## The real test

Reboot the Pi and change nothing else:

```bash
sudo reboot
```

Once it comes back, the topics should be visible from the ground station without
opening a single SSH session. That is the point of this page.

## Managing the service

```bash
# Stop it (e.g. to run the agent manually for debugging)
sudo systemctl stop micro-xrce-dds-agent.service

# Stop it starting at boot
sudo systemctl disable micro-xrce-dds-agent.service

# Reload after editing the unit file
sudo systemctl daemon-reload
sudo systemctl restart micro-xrce-dds-agent.service
```
