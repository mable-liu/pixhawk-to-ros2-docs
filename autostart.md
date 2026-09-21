# Autostart

Set the agent up as a systemd service so it starts on its own when the Pi boots.

Without this you have to SSH in and start the agent by hand every time, and the
bridge dies as soon as you close that session. As a service, the Pixhawk joins the
ROS 2 network as soon as the drone powers on, with no laptop needed.

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

What the settings do:

`After` and `Wants` wait for the network, since the agent needs a connection to
announce itself on.

`User=ubuntu` runs the agent as your normal account rather than root. That works
because the account is in the `dialout` group from
[the serial setup](serial-connection.md#3-give-your-user-access-to-the-serial-port).

`Environment="ROS_DOMAIN_ID=0"` sets the domain ID. Services do not read your
`.bashrc`, so it has to go here. **Use the same ID as your ground station**, see
[Ground station](ground-station.md#domain-id). If they differ, the agent runs
perfectly and nobody can see it.

`Restart=always` restarts the agent if it stops, which matters at boot when the
service may come up before the Pixhawk has finished powering on.

## Turn it on

```bash
sudo systemctl daemon-reload
sudo systemctl enable micro-xrce-dds-agent.service
sudo systemctl start micro-xrce-dds-agent.service
```

`daemon-reload` makes systemd read your new file. `enable` sets it to start at boot.
`start` runs it now, so you do not have to reboot to test it.

## Check it worked

```bash
systemctl status micro-xrce-dds-agent.service
```

You want to see `Active: active (running)`:

```text
● micro-xrce-dds-agent.service - Micro XRCE-DDS Agent (PX4 to ROS 2 bridge)
     Loaded: loaded (/etc/systemd/system/micro-xrce-dds-agent.service; enabled)
     Active: active (running) since Mon 2026-08-04 22:10:03 UTC; 5s ago
   Main PID: 1180 (MicroXRCEAgent)
```

To watch the log as it runs:

```bash
journalctl -u micro-xrce-dds-agent.service -f
```

If the service keeps restarting, you will see it here. Usually it is a permissions
problem with the serial port or a wrong path in `ExecStart`.

Then check the bridge itself. `uxrce_dds_client status` in the QGroundControl MAVLink
console should still say `Running, connected`, and
`ros2 topic echo /fmu/out/vehicle_attitude` on the
[ground station](ground-station.md) should still respond when you tilt the Pixhawk.

## Test a reboot

This is the part that actually matters. Reboot the Pi:

```bash
sudo reboot
```

When it comes back, the topics should appear on the ground station without you
opening a single SSH session.

## Managing the service

```bash
# Stop it, for example to run the agent by hand while debugging
sudo systemctl stop micro-xrce-dds-agent.service

# Stop it starting at boot
sudo systemctl disable micro-xrce-dds-agent.service

# Apply changes after editing the file
sudo systemctl daemon-reload
sudo systemctl restart micro-xrce-dds-agent.service
```
