from Database.users_db import FirebaseUser

# Example usage
user = FirebaseUser()

# Update values
user.update_name(0, 'Esad')
user.update_latitude(0, 41.2853)
user.update_online(0, "True")
user.update_longitude(0, 28.7496)
user.update_authority(0, False)

# Get values
print(user.get_name(0))
print(user.get_latitude(0))
print(user.get_online(0))
print(user.get_longitude(0))
print(user.get_authority(0))
print(user.get_mission())
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
