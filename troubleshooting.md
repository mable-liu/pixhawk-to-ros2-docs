# Troubleshooting

Failure modes grouped by the stage where they show up.

## Cannot SSH to the Pi

**`ssh: Could not resolve hostname ubuntu.local`**

mDNS is not resolving. Find the Pi's IP from your router's client list or with
`arp -a`, and connect by address instead. See
[Raspberry Pi setup](pi-setup.md#if-ubuntulocal-does-not-resolve).

**The Pi never appears on the network at all**

- Confirm the Wi-Fi credentials entered in Raspberry Pi Imager, including the SSID's
  exact spelling and the country code.
- The Pi Zero 2 W is **2.4 GHz only**. If the SSID is 5 GHz or uses band steering,
  the Pi may never associate.
- Give first boot a couple of minutes — cloud-init runs before SSH comes up.
- Check the green activity LED. Steady dark after power-on suggests the card did not
  boot; re-flash it.

**`Permission denied (publickey,password)`**

The username or password does not match what was set in Imager. The username is part
of the image configuration, not something you can change over SSH.

## ROS 2 installation fails

**`E: Unable to locate package ros-humble-ros-base`**

The apt repository was not added successfully, or the Ubuntu release is wrong. Check:

```bash
lsb_release -a          # must be 22.04, codename jammy
dpkg --print-architecture # must be arm64
```

A 32-bit `armhf` image has no ROS 2 Humble packages available. That means re-flashing
with the 64-bit image — see [Raspberry Pi setup](pi-setup.md).

**The `curl` commands in the repository step fail**

Both need working DNS and outbound HTTPS *from the Pi*. Test with
`curl -I https://github.com`. A Pi that associated to Wi-Fi but got no DNS server
will fail here while still accepting SSH from the local network.

**`ros2: command not found` after installing**

The environment is not sourced in this shell. Run
`source /opt/ros/humble/setup.bash`, then check that the line is present in
`~/.bashrc` so new sessions pick it up automatically.

## No MAVLink heartbeat

MAVProxy sits at `Waiting for heartbeat from /dev/serial0` and never connects.

Work through these in order — the first two account for most cases:

1. **TX and RX not crossed.** The single most common wiring error. The Pixhawk's TX
   must reach the Pi's RX (pin 10) and vice versa. Recheck against the
   [pinout table](serial-connection.md#pinout).

2. **The flight controller was not rebooted** after setting `MAV_1_CONFIG = TELEM2`.
   Port assignments are read at boot. Reboot and retry.

3. **Ground not connected.** Serial needs a shared reference. Verify continuity
   between TELEM2 pin 6 and the Pi's pin 6.

4. **`/dev/serial0` does not exist or points at `ttyS0`.**

   ```bash
   ls -l /dev/serial0
   ```

   It should symlink to `ttyAMA0`. If it is missing or points elsewhere, the UART
   configuration did not apply — see
   [Serial connection](serial-connection.md#enabling-the-uart-on-the-pi).

5. **The serial console is still attached.** If `console=serial0,115200` remains in
   `/boot/firmware/cmdline.txt`, Linux is transmitting login prompts down the same
   wires.

6. **ModemManager is interfering.** It probes serial devices and corrupts framing:

   ```bash
   sudo apt remove modemmanager
   ```

7. **Baud mismatch.** `SER_TEL2_BAUD` in QGroundControl must match the
   `--baudrate` argument. For the MAVLink test both are `57600`.

8. **Permission denied on `/dev/serial0`.** Run `groups` and confirm `dialout` is
   listed. Group changes need a fresh login to take effect.

9. **Cold solder joint.** The harness is hand-made. Check continuity end to end with
   a multimeter before assuming a software cause.

## Agent build fails

**`c++: fatal error: Killed signal terminated program cc1plus`**

Out of memory, not a compiler bug — the kernel's OOM killer terminated the build. The
Pi Zero 2 W has 512 MB of RAM. Build single-threaded with plain `make`, and add swap
if needed. See
[Micro XRCE-DDS Agent](xrce-dds-agent.md#building-the-agent).

**`MicroXRCEAgent: command not found` after `sudo make install`**

Either the install step did not complete, or the linker cache is stale:

```bash
sudo ldconfig /usr/local/lib/
which MicroXRCEAgent
```

## uxrce_dds_client reports "Running" but not "connected"

PX4 is transmitting but nothing is answering. The agent must be running on the Pi
before the client reports a connection.

- Confirm `MicroXRCEAgent` is actually running (`systemctl status` if using the
  [service](autostart.md), otherwise check the terminal).
- Confirm `SER_TEL2_BAUD = 921600` matches the `-b 921600` flag.
- Confirm `UXRCE_DDS_CFG = 102` and that the flight controller was **rebooted**
  afterwards.
- Confirm `MAV_1_CONFIG = 0`. MAVLink and uXRCE-DDS cannot share one UART, and if
  MAVLink still owns TELEM2 the DDS client has no port.
- If the link worked at 57600 for MAVLink but fails at 921600, suspect the UART. The
  mini-UART (`ttyS0`) is unreliable at that rate — confirm `/dev/serial0` points at
  `ttyAMA0`.

## No topics from `ros2 topic list`

**Only `/parameter_events` and `/rosout` appear**

ROS 2 is working but no PX4 client is attached. Check
`uxrce_dds_client status` in the MAVLink console and work back from there.

**Nothing appears from the ground station, but the Pi sees the topics**

A discovery problem rather than a bridge problem.

- **`ROS_DOMAIN_ID` mismatch.** Run `echo $ROS_DOMAIN_ID` on both machines — they must
  match. Remember the [systemd service](autostart.md) needs it set in the unit file,
  not just in `.bashrc`.
- **Multicast blocked on the Wi-Fi.** Test with `ros2 multicast send` on one machine
  and `ros2 multicast receive` on the other. See
  [Ground station](ground-station.md#multicast-on-the-wi-fi-network).
- **Different ROS 2 distributions.** Both machines must run Humble.

## Topics appear but echo is empty

`ros2 topic list` shows `/fmu/out/...`, but `ros2 topic echo` prints nothing or
errors.

- **`px4_msgs` not sourced.** Run
  `source ~/ws_px4/install/local_setup.bash` in the same terminal.
- **`px4_msgs` branch does not match the PX4 firmware version.** Message definitions
  change between releases, and a mismatch fails to deserialise. Get the version with
  `ver all` in the MAVLink console and rebuild against the matching `release/x.y`
  branch. See {ref}`Ground station <px4-msgs-install>`.
- **Values present but frozen.** The topic is being published but the sensor is not
  updating. Confirm the Pixhawk is fully booted and has completed sensor
  initialisation.

## Service will not stay running

`systemctl status` shows repeated restarts.

```bash
journalctl -u micro-xrce-dds-agent.service -n 50
```

Common causes:

- **Permission denied on `/dev/serial0`** — the `User=` in the unit file is not in the
  `dialout` group.
- **Wrong `ExecStart` path** — verify with `which MicroXRCEAgent`.
- **Started before the Pixhawk powered up.** `Restart=always` should recover this
  within seconds; if it does not, check that `RestartSec` is set.
