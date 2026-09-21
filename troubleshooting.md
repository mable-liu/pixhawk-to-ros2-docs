# Troubleshooting

Problems grouped by where they show up.

## Cannot SSH to the Pi

**`ssh: Could not resolve hostname ubuntu.local`**

Your network cannot resolve `.local` names. Find the Pi's IP address from your
router or with `arp -a` and connect to that instead. See
[Raspberry Pi setup](pi-setup.md#if-ubuntulocal-does-not-resolve).

**The Pi never shows up on the network**

- Check the Wi-Fi details you entered in Imager, including the exact network name and
  the country code.
- The Pi Zero 2 W is **2.4 GHz only**. If your network is 5 GHz, the Pi cannot join
  it.
- Give the first boot a couple of minutes.
- Look at the green LED. If it stays dark, the card probably did not boot. Try
  flashing it again.

**`Permission denied (publickey,password)`**

The username or password does not match what you set in Imager. The username is part
of the SD card image, so you cannot change it over SSH.

## ROS 2 will not install

**`E: Unable to locate package ros-humble-ros-base`**

Either the repository was not added properly, or you are on the wrong Ubuntu version:

```bash
lsb_release -a            # should say 22.04, jammy
dpkg --print-architecture # should say arm64
```

If it says `armhf`, you flashed the 32-bit image and there are no ROS 2 Humble
packages for it. Reflash with the 64-bit image, see
[Raspberry Pi setup](pi-setup.md).

**The `curl` commands fail**

They need internet access from the Pi itself. Test with `curl -I https://github.com`.
A Pi that joined the Wi-Fi but did not get DNS settings will fail here while still
letting you SSH in.

**`ros2: command not found` after installing**

The environment is not loaded. Run `source /opt/ros/humble/setup.bash`, then check
that line is in your `~/.bashrc`.

## No MAVLink heartbeat

MAVProxy sits on `Waiting for heartbeat from /dev/serial0` and never connects.

Check these in order. The first two are the usual culprits:

1. **TX and RX are not crossed.** The most common wiring mistake. The Pixhawk's TX
   must go to the Pi's RX (pin 10) and the other way around. See the
   [pinout](serial-connection.md#pinout).

2. **You did not reboot the flight controller** after setting
   `MAV_1_CONFIG = TELEM2`. PX4 only reads that at startup.

3. **No ground connection.** Check continuity between TELEM2 pin 6 and the Pi's pin
   6.

4. **`/dev/serial0` is missing or points to `ttyS0`.**

   ```bash
   ls -l /dev/serial0
   ```

   It should point to `ttyAMA0`. If not, the boot file changes did not work. See
   [Serial connection](serial-connection.md#enabling-the-uart-on-the-pi).

5. **The login console is still using the port.** Check that
   `console=serial0,115200` is gone from `/boot/firmware/cmdline.txt`.

6. **ModemManager is interfering:**

   ```bash
   sudo apt remove modemmanager
   ```

7. **Speeds do not match.** `SER_TEL2_BAUD` must match the `--baudrate` you passed.
   Both should be `57600` for this test.

8. **Permission denied.** Run `groups` and check `dialout` is there. You need to log
   out and back in after adding it.

9. **A bad solder joint.** Check the cable with a multimeter before blaming the
   software.

## The agent will not build

**`c++: fatal error: Killed signal terminated program cc1plus`**

The Pi ran out of memory. Use plain `make` instead of `make -j4`, and add swap if
needed. See [Micro XRCE-DDS Agent](xrce-dds-agent.md#build-the-agent).

**`MicroXRCEAgent: command not found` after installing**

Either the install did not finish or the system cannot find the new libraries:

```bash
sudo ldconfig /usr/local/lib/
which MicroXRCEAgent
```

## PX4 says "Running" but not "connected"

PX4 is sending data but nothing is answering. The agent has to be running first.

- Check the agent is actually running.
- Check `SER_TEL2_BAUD = 921600` matches the `-b 921600` you passed.
- Check `UXRCE_DDS_CFG = 102` and that you **rebooted** afterwards.
- Check `MAV_1_CONFIG = 0`. If MAVLink still has TELEM2, the DDS client has nowhere
  to go.
- If MAVLink worked at 57600 but this fails at 921600, the Pi is probably using the
  weaker UART. Check that `/dev/serial0` points to `ttyAMA0`.

## No topics in `ros2 topic list`

**Only `/parameter_events` and `/rosout` show up**

ROS 2 is fine, but PX4 is not connected to the agent. Check
`uxrce_dds_client status` in the MAVLink console.

**The Pi sees the topics but the ground station does not**

This is a discovery problem, not a bridge problem.

- **Different `ROS_DOMAIN_ID`.** Run `echo $ROS_DOMAIN_ID` on both machines. The
  [service](autostart.md) needs it set in its unit file, not just in `.bashrc`.
- **Multicast is blocked.** Test with `ros2 multicast send` and
  `ros2 multicast receive`. See
  [Ground station](ground-station.md#multicast-on-the-wi-fi-network).
- **Different ROS 2 versions.** Both machines need Humble.

## Topics appear but echo is empty

`ros2 topic list` shows the `/fmu/out/...` topics, but `ros2 topic echo` prints
nothing or errors out.

- **`px4_msgs` is not loaded.** Run `source ~/ws_px4/install/local_setup.bash` in the
  same terminal.
- **`px4_msgs` does not match your PX4 version.** Check with `ver all` and rebuild
  from the matching `release/x.y` branch. See
  {ref}`Ground station <px4-msgs-install>`.
- **The numbers are there but frozen.** The Pixhawk may still be starting up. Give it
  a moment to finish initialising its sensors.

## The service keeps restarting

```bash
journalctl -u micro-xrce-dds-agent.service -n 50
```

Usually one of:

- **Permission denied on `/dev/serial0`.** The account in `User=` is not in the
  `dialout` group.
- **Wrong path in `ExecStart`.** Check with `which MicroXRCEAgent`.
- **It started before the Pixhawk was ready.** `Restart=always` should sort this out
  within a few seconds.
