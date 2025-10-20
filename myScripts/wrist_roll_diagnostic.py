#!/usr/bin/env python3
"""
Diagnostic script for wrist_roll motor issue on SO101 follower
"""

import argparse
import time
import os
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus


def diagnose_wrist_roll(port, motor_id=5):
    """Diagnose wrist_roll motor specifically"""
    print("\n" + "="*60)
    print("WRIST ROLL MOTOR DIAGNOSTIC")
    print("="*60)
    
    # Create motor configuration for wrist_roll only
    motor_config = {
        "wrist_roll": Motor(motor_id, "sts3215", MotorNormMode.DEGREES)
    }
    
    try:
        # Connect without calibration to read raw values
        print(f"\n1. Connecting to motor ID {motor_id} on {port}...")
        bus = FeetechMotorsBus(port=port, motors=motor_config, calibration={})
        bus.connect()
        print("✓ Connected successfully")
        
        # Basic connectivity test
        try:
            model = bus.ping("wrist_roll")
            print(f"✓ Motor responding - Model: {model}")
        except Exception as e:
            print(f"✗ Motor not responding: {e}")
            return
        
        # Read all available registers
        print("\n2. Reading motor registers...")
        registers = {
            "ID": (5, 1),
            "Baudrate": (6, 1),
            "Return_Delay_Time": (7, 1),
            "Response_Status_Level": (8, 1),
            "Min_Angle_Limit": (9, 2),
            "Max_Angle_Limit": (11, 2),
            "Max_Temperature_Limit": (13, 1),
            "Max_Voltage_Limit": (14, 1),
            "Min_Voltage_Limit": (15, 1),
            "Max_Torque_Limit": (16, 2),
            "Torque_Enable": (40, 1),
            "Goal_Position": (42, 2),
            "Present_Position": (56, 2),
            "Present_Speed": (58, 2),
            "Present_Load": (60, 2),
            "Present_Voltage": (62, 1),
            "Present_Temperature": (63, 1),
            "Moving": (66, 1),
            "Lock": (48, 1),
        }
        
        print(f"{'Register':<25} {'Value':<15} {'Notes':<30}")
        print("-" * 70)
        
        for reg_name, (address, size) in registers.items():
            try:
                # Read raw register value
                value = bus._read(reg_name, "wrist_roll", num_retry=1)
                
                # Add interpretation for important registers
                notes = ""
                if reg_name == "Torque_Enable":
                    notes = "Enabled" if value == 1 else "Disabled"
                elif reg_name == "Moving":
                    notes = "Moving" if value == 1 else "Stopped"
                elif reg_name == "Lock":
                    notes = "Locked" if value == 1 else "Unlocked"
                elif reg_name == "Present_Temperature":
                    notes = f"{value}°C"
                elif reg_name == "Present_Voltage":
                    notes = f"{value/10:.1f}V"
                elif reg_name in ["Min_Angle_Limit", "Max_Angle_Limit", "Goal_Position", "Present_Position"]:
                    notes = f"(~{value*360/4095:.1f}°)"
                
                print(f"{reg_name:<25} {str(value):<15} {notes:<30}")
            except Exception as e:
                print(f"{reg_name:<25} {'ERROR':<15} {str(e)[:30]:<30}")
        
        # Test torque enable/disable
        print("\n3. Testing torque control...")
        print("   Disabling torque...")
        bus.disable_torque(["wrist_roll"])
        time.sleep(0.5)
        
        torque_state = bus._read("Torque_Enable", "wrist_roll")
        print(f"   Torque state: {'✓ Disabled' if torque_state == 0 else '✗ Still enabled!'}")
        
        # Check if motor moves freely when torque is disabled
        print("\n4. Checking mechanical freedom (torque disabled)...")
        print("   Reading position changes over 3 seconds...")
        positions = []
        for i in range(6):
            pos = bus.read("Present_Position", "wrist_roll", normalize=False)
            positions.append(pos)
            print(f"   Position {i+1}: {pos}", end='\r')
            time.sleep(0.5)
        
        pos_change = max(positions) - min(positions)
        print(f"\n   Position variation: {pos_change}")
        if pos_change > 50:
            print("   ⚠ Motor is moving while torque is disabled - check mechanical issues")
        else:
            print("   ✓ Motor is stable")
        
        # Test controlled movement
        print("\n5. Testing controlled movement...")
        print("   Enabling torque...")
        bus.enable_torque(["wrist_roll"])
        time.sleep(0.5)
        
        current_pos = bus.read("Present_Position", "wrist_roll", normalize=False)
        print(f"   Current position: {current_pos}")
        
        # Small test movement
        test_positions = [current_pos, current_pos + 100, current_pos - 100, current_pos]
        for i, target in enumerate(test_positions):
            # Ensure we stay in safe range
            target = max(500, min(3500, target))
            print(f"\n   Movement {i+1}: Moving to {target}")
            
            try:
                bus.sync_write("Goal_Position", {"wrist_roll": target}, normalize=False)
                
                # Monitor movement
                start_time = time.time()
                timeout = 3.0
                last_pos = None
                stuck_count = 0
                
                while time.time() - start_time < timeout:
                    current = bus.read("Present_Position", "wrist_roll", normalize=False)
                    is_moving = bus.read("Moving", "wrist_roll", normalize=False)
                    
                    # Check if motor is stuck
                    if last_pos is not None and abs(current - last_pos) < 2:
                        stuck_count += 1
                    else:
                        stuck_count = 0
                    last_pos = current
                    
                    print(f"     Pos: {current}, Target: {target}, Moving: {bool(is_moving)}, Stuck: {stuck_count}", end='\r')
                    
                    if abs(current - target) < 20 and not is_moving:
                        print(f"\n     ✓ Reached target in {time.time()-start_time:.2f}s")
                        break
                        
                    if stuck_count > 5 and is_moving:
                        print(f"\n     ⚠ Motor appears stuck! Position not changing but 'Moving' flag is set")
                        break
                        
                    time.sleep(0.1)
                else:
                    print(f"\n     ✗ Timeout - did not reach target")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"     ✗ Movement failed: {e}")
                break
        
        # Disable torque at the end
        print("\n6. Disabling torque for safety...")
        bus.disable_torque(["wrist_roll"])
        print("✓ Torque disabled")
        
        # Final recommendations
        print("\n" + "="*60)
        print("DIAGNOSTIC SUMMARY")
        print("="*60)
        
        if pos_change > 50:
            print("⚠ MECHANICAL ISSUE DETECTED: Motor moves when torque is disabled")
            print("  Possible causes:")
            print("  - Loose coupling or gears")
            print("  - Damaged internal components")
            print("  - External force on the joint")
        
        print("\nRecommended next steps:")
        print("1. Check physical mounting and coupling of wrist_roll motor")
        print("2. Verify wiring connections are secure")
        print("3. Compare calibration values with a working robot")
        print("4. Test with different control modes if available")
        
    except Exception as e:
        print(f"\n✗ Diagnostic failed: {e}")
    finally:
        if 'bus' in locals():
            bus.disconnect()
            print("\nDisconnected from motor bus")


def compare_calibration(follower_id="my_awesome_follower_arm", leader_id="my_awesome_leader_arm"):
    """Compare calibration files for leader and follower"""
    print("\n" + "="*60)
    print("CALIBRATION COMPARISON")
    print("="*60)
    
    import json
    from pathlib import Path
    
    home = Path.home()
    cache_dir = home / ".cache" / "lerobot" / "calibration"
    
    # Check follower calibration
    follower_file = cache_dir / f"so101_follower_{follower_id}.json"
    leader_file = cache_dir / f"so101_leader_{leader_id}.json"
    
    print(f"\nChecking calibration files:")
    print(f"Follower: {follower_file}")
    print(f"Leader: {leader_file}")
    
    if follower_file.exists():
        print("\n✓ Follower calibration found")
        with open(follower_file) as f:
            follower_cal = json.load(f)
            
        if "wrist_roll" in follower_cal:
            print(f"\nFollower wrist_roll calibration:")
            for key, value in follower_cal["wrist_roll"].items():
                print(f"  {key}: {value}")
        else:
            print("✗ No wrist_roll calibration found for follower!")
    else:
        print("✗ Follower calibration file not found!")
        
    if leader_file.exists():
        print("\n✓ Leader calibration found")
        with open(leader_file) as f:
            leader_cal = json.load(f)
            
        if "wrist_roll" in leader_cal:
            print(f"\nLeader wrist_roll calibration:")
            for key, value in leader_cal["wrist_roll"].items():
                print(f"  {key}: {value}")
        else:
            print("✗ No wrist_roll calibration found for leader!")
    else:
        print("✗ Leader calibration file not found!")


def main():
    parser = argparse.ArgumentParser(description="Diagnose wrist_roll motor issues")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port for follower")
    parser.add_argument("--motor-id", type=int, default=5, help="Motor ID for wrist_roll (default: 5)")
    parser.add_argument("--check-calibration", action="store_true", help="Compare calibration files")
    parser.add_argument("--follower-id", default="my_awesome_follower_arm", help="Follower robot ID")
    parser.add_argument("--leader-id", default="my_awesome_leader_arm", help="Leader robot ID")
    
    args = parser.parse_args()
    
    if args.check_calibration:
        compare_calibration(args.follower_id, args.leader_id)
    else:
        diagnose_wrist_roll(args.port, args.motor_id)


if __name__ == "__main__":
    main()