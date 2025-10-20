#!/usr/bin/env python3
"""
Simple motor diagnostics script for LeRobot
Tests individual motors one by one for SO101 follower arm
"""

import argparse
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus


def test_single_motor(bus, motor_name, motor, large_movement=False):
    """Test a single motor with basic movements"""
    print(f"\n{'='*60}")
    print(f"Testing Motor: {motor_name} (ID: {motor.id})")
    print(f"{'='*60}")
    
    try:
        # Check if motor is connected
        try:
            model_number = bus.ping(motor_name)
            print(f"Motor connected - Model: {model_number}")
        except Exception as e:
            print(f"WARNING: Motor {motor_name} is not responding to ping: {e}")
            return False
            
        # Read current position (raw value, no normalization)
        current_pos = bus.read("Present_Position", motor_name, normalize=False)
        print(f"Current position (raw): {current_pos}")
        
        # Wait a moment for any previous operations to complete
        time.sleep(0.5)
        
        # Enable torque
        bus.enable_torque([motor_name])
        print("Torque enabled")
        
        # Wait for torque to be fully enabled
        time.sleep(0.5)
        
        # Test movements (use raw values for testing)
        # Note: STS3215 has a range typically from 0-4095 (12-bit), center around 2048
        if large_movement:
            test_offsets = [0, 600, -600, 400, -400, 200, -200, 0]  # Large movements for full testing
            safe_min, safe_max = 200, 3800  # Wider range for large movements
            print("Using LARGE movement mode - monitor carefully!")
        else:
            test_offsets = [0, 300, -300, 150, -150, 0]  # Medium movements for testing  
            safe_min, safe_max = 500, 3500  # Safe range for normal testing
        
        for i, offset in enumerate(test_offsets):
            target_pos = current_pos + offset
            # Clamp to safe range
            target_pos = max(safe_min, min(safe_max, target_pos))
            
            print(f"\nMovement {i+1}: Moving to raw position {target_pos} (offset: {offset})")
            
            try:
                # Use sync_write for more reliable communication
                bus.sync_write("Goal_Position", {motor_name: target_pos}, normalize=False)
                print("  Command sent successfully")
                
                # Monitor movement
                start_time = time.time()
                while time.time() - start_time < 5.0:  # Longer timeout
                    try:
                        current_pos = bus.read("Present_Position", motor_name, normalize=False)
                        is_moving = bus.read("Moving", motor_name, normalize=False)
                        print(f"  Position: {current_pos} (moving: {bool(is_moving)})", end='\r')
                        
                        # Check if reached target (within reasonable range)
                        if abs(current_pos - target_pos) < 30 and not is_moving:
                            print(f"\n  ✓ Reached target position in {time.time()-start_time:.2f}s")
                            break
                            
                    except Exception as e:
                        print(f"\n  Warning: Read error during movement: {e}")
                        
                    time.sleep(0.2)  # Slower polling to reduce communication load
                else:
                    print(f"\n  ⚠ Timeout - movement may not have completed")
                    
                # Wait between movements
                time.sleep(1.0)
                
            except Exception as e:
                print(f"  ❌ Failed to send movement command: {e}")
                # Try to read current position to check if motor is still responsive
                try:
                    current_pos = bus.read("Present_Position", motor_name, normalize=False)
                    print(f"  Motor still responsive, current position: {current_pos}")
                except:
                    print(f"  Motor may have stopped responding")
                    break
        
        # Read additional diagnostics (raw values)
        try:
            temp = bus.read("Present_Temperature", motor_name, normalize=False)
            print(f"\nTemperature (raw): {temp}")
        except Exception as e:
            print(f"Could not read temperature: {e}")
            
        try:
            voltage = bus.read("Present_Voltage", motor_name, normalize=False)
            print(f"Voltage (raw): {voltage}")
        except Exception as e:
            print(f"Could not read voltage: {e}")
            
        try:
            load = bus.read("Present_Load", motor_name, normalize=False)
            print(f"Load (raw): {load}")
        except Exception as e:
            print(f"Could not read load: {e}")
            
        # Disable torque
        bus.disable_torque([motor_name])
        print("\nTorque disabled")
        
        return True
        
    except Exception as e:
        print(f"ERROR testing motor {motor_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Motor diagnostics for LeRobot SO101 follower")
    parser.add_argument("--port", default="/dev/ttyACM1", help="Serial port for motor bus")
    parser.add_argument("--motor", help="Test specific motor by name (e.g., shoulder_pan)")
    parser.add_argument("--list", action="store_true", help="List all available motors")
    parser.add_argument("--with-calibration", action="store_true", help="Use existing calibration (requires calibrated robot)")
    parser.add_argument("--large-movement", action="store_true", help="Use larger test movements (use with caution)")
    args = parser.parse_args()
    
    # Define motor configuration for SO101 follower
    motor_config = {
        "shoulder_pan": Motor(1, "sts3215", MotorNormMode.DEGREES),
        "shoulder_lift": Motor(2, "sts3215", MotorNormMode.DEGREES),
        "elbow_flex": Motor(3, "sts3215", MotorNormMode.DEGREES),
        "wrist_flex": Motor(4, "sts3215", MotorNormMode.DEGREES),
        "wrist_roll": Motor(5, "sts3215", MotorNormMode.DEGREES),
        "gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100),
    }
    
    if args.list:
        print("\nAvailable motors:")
        for name, motor in motor_config.items():
            print(f"  {name}: ID={motor.id}")
        return
    
    # Connect to motor bus
    print(f"Connecting to motor bus on {args.port}...")
    try:
        if args.with_calibration:
            # Use existing calibration (requires pre-calibrated robot)
            bus = FeetechMotorsBus(port=args.port, motors=motor_config)
            bus.connect()
            print("Connected successfully with existing calibration!")
        else:
            # Create bus without calibration for testing purposes
            bus = FeetechMotorsBus(port=args.port, motors=motor_config, calibration={})
            bus.connect()
            print("Connected successfully!")
            print("Note: Running without calibration - raw motor values will be used")
    except Exception as e:
        print(f"ERROR: Failed to connect to motor bus: {e}")
        return
    
    try:
        if args.motor:
            # Test specific motor
            if args.motor not in motor_config:
                print(f"ERROR: Motor '{args.motor}' not found. Use --list to see available motors.")
                return
                
            motor = motor_config[args.motor]
            test_single_motor(bus, args.motor, motor, args.large_movement)
        else:
            # Test all motors one by one
            print(f"\nTesting all {len(motor_config)} motors...")
            input("Press Enter to start (Ctrl+C to cancel)...")
            
            failed_motors = []
            for name, motor in motor_config.items():
                if not test_single_motor(bus, name, motor, args.large_movement):
                    failed_motors.append(name)
                    
                if name != list(motor_config.keys())[-1]:  # Not the last motor
                    input("\nPress Enter to test next motor...")
            
            # Summary
            print(f"\n{'='*60}")
            print("DIAGNOSTIC SUMMARY")
            print(f"{'='*60}")
            print(f"Total motors: {len(motor_config)}")
            print(f"Passed: {len(motor_config) - len(failed_motors)}")
            print(f"Failed: {len(failed_motors)}")
            
            if failed_motors:
                print("\nFailed motors:")
                for motor in failed_motors:
                    print(f"  - {motor}")
                    
    except KeyboardInterrupt:
        print("\nDiagnostics interrupted by user")
    finally:
        bus.disconnect()
        print("\nDisconnected from motor bus")


if __name__ == "__main__":
    main()