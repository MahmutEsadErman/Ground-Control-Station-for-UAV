import cv2

def record_video(output_file, duration_seconds):
    # Open the default camera (usually 0)
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Unable to open camera.")
        return

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    fps = 30  # Frames per second
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

    # Record video
    start_time = cv2.getTickCount() / cv2.getTickFrequency()  # Current time in seconds
    while (cv2.getTickCount() / cv2.getTickFrequency()) - start_time < duration_seconds:
        ret, frame = cap.read()  # Read a frame from the camera
        if not ret:
            print("Error: Unable to read frame.")
            break
        out.write(frame)  # Write the frame to the output video

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Example usage: record video for 10 seconds and save as "output.mp4"
record_video("output.mp4", 10)
