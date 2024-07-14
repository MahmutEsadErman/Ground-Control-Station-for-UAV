from Database.users_db import FirebaseUser

# Example usage
user = FirebaseUser('1')

# Update values
user.update_name('John Doe')
user.update_latitude(37.7749)
user.update_online("True")
user.update_longitude(37.9999)
user.update_authority(False)
user.update_mission(1)
user.update_marker_latitude(40)
user.update_marker_longitude(40)

# Get values
print(user.get_name())
print(user.get_latitude())
print(user.get_online())
print(user.get_longitude())
print(user.get_authority())
print(user.get_mission())
print(user.get_marker_latitude())
print(user.get_marker_longitude())


def on_mission_change(event):
    # Get the updated data from the event

    # Check if the "Mission" field has changed
    if mission_value is not None:
        # Perform your desired actions here
        print(f"Mission changed to: {mission_value}")
        # ... (Your custom logic)

# Attach a listener to the reference
user.ref.listen(on_mission_change)

# Keep the script running to listen for changes
while True:
    pass
