import cv2
import argparse

# Get arguments for camera device id if needed
arg_parser = argparse.ArgumentParser(description="Test Camera Stream")
arg_parser.add_argument('--device', type=int, default=6, help='Camera device ID (default: 6)')
args = arg_parser.parse_args()

cam_id = args.device

# Use your camera device path
camera_path = f"/dev/video{cam_id}"

# Open the camera stream
cap = cv2.VideoCapture(camera_path, cv2.CAP_V4L2)
if not cap.isOpened():
    print(f"Error: Could not open camera {camera_path}")
    exit(1)

# Optionally set resolution and FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Press 'q' to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Display the image
    cv2.imshow("Camera Preview", frame)

    # Quit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
