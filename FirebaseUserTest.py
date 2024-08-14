from Database.users_db import FirebaseUser

# Example usage
user = FirebaseUser()

# Update values
# user.update_user_name('Esad', 1)
# user.update_user_latitude(41.2853, 1)
# user.update_user_online("True", 1)
# user.update_user_longitude(28.7496, 1)
# user.update_user_authority(False, 1)
user.update_marker_compass(185.2)
user.update_marker_latitude(32.3)
user.update_marker_longitude(40.5)
user.update_mission(0)
user.add_target(1,True, 30.5, 40.1, "Database/data/0.jpg")
user.update_target_image("Database/data/0.jpg", 1)

# Get values
print(user.get_name(1))
print(user.get_latitude(1))
print(user.get_online(1))
print(user.get_longitude(1))
print(user.get_authority(1))
print(user.get_image(1))
print(user.get_marker_compass())
print(user.get_marker_latitude())
print(user.get_marker_longitude())


# def on_mission_change(event):
#     # Get the updated data from the event
#
#     # Check if the "Mission" field has changed
#     if mission_value is not None:
#         # Perform your desired actions here
#         print(f"Mission changed to: {mission_value}")
#         # ... (Your custom logic)
#
# # Attach a listener to the reference
# user.ref.listen(on_mission_change)
#
# # Keep the script running to listen for changes
# while True:
#     pass
