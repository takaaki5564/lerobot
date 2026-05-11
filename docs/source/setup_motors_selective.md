# Motor Setup with Skip Functionality

The `lerobot-setup-motors-selective` script is an enhanced version of the standard motor setup tool that allows you to skip motors you've already configured or set up only specific motors.

## Features

- **Interactive Mode**: Prompts for each motor individually, allowing you to skip already-configured ones
- **Selective Mode**: Configure only specific motors by name using the `--motors` option
- **Scan Only**: Discover motors on the port without configuring them
- **Error Recovery**: Retry failed setups without having to restart

## Usage

### Interactive Mode (Skip Motors You've Already Set Up)

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0
```

For each motor, you'll see a prompt:
```
Configure 'shoulder' motor?
(y)es / (s)kip / (q)uit? [y/s/q]:
```

- Press `y` or Enter to configure this motor
- Press `s` to skip this motor
- Press `q` to quit entirely

### Selective Mode (Configure Specific Motors Only)

If you only want to configure certain motors, list them by name:

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --motors=shoulder,elbow,gripper
```

This will configure **only** the shoulder, elbow, and gripper motors in non-interactive mode.

Available motor names depend on your robot/teleop type. Common examples:
- `shoulder`, `elbow`, `wrist`, `gripper` (SO-100 follower)
- `shoulder`, `elbow`, `wrist`, `roll`, `gripper` (SO-101 follower)
- `motor_0`, `motor_1`, etc. (other types)

### Scan Only Mode (Find Motors Without Configuring)

To discover which motors are currently on the port:

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --scan-only
```

This will display all motors found at each baudrate, helping you identify which ones are already configured.

## Typical Workflow

### Scenario: Adding a Motor to an Existing Setup

1. **Scan to check current state**:
   ```bash
   lerobot-setup-motors-selective \
       --robot.type=so100_follower \
       --robot.port=/dev/ttyUSB0 \
       --scan-only
   ```
   This shows you which motors are already on the bus.

2. **Set up only the new motor**:
   ```bash
   lerobot-setup-motors-selective \
       --robot.type=so100_follower \
       --robot.port=/dev/ttyUSB0 \
       --motors=wrist
   ```

### Scenario: Re-setting a Single Motor

If you need to reconfigure just one motor among several:

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --motors=shoulder
```

The script will set up only the shoulder motor without touching the others.

### Scenario: Gradual Setup with Skipping

If setting up multiple motors but some fail:

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0
```

When prompted for each motor, skip ones that are already OK and configure only the ones that need attention. The script will offer to retry on error.

## Supported Devices

The script supports the same devices as the standard `lerobot-setup-motors`:

- `so100_follower` / `so100_leader`
- `so101_follower` / `so101_leader`
- `koch_follower` / `koch_leader`
- `lekiwi`

## Troubleshooting

### Motor Not Found on Port

If a motor doesn't appear when you try to set it up:

1. Run `--scan-only` to see what's currently on the bus
2. Check physical connections (USB, power, communication wires)
3. Verify the motor's current baudrate matches the bus scanner's attempt

### Motor Already Has the Target ID

The motor bus will skip setting the ID if it's already correct. This is safe and expected.

### Script Hangs at Input Prompt

- On interactive mode: this is normal. The script waits for your input (y/s/q)
- On selective mode: connect the hardware first, then press Enter
