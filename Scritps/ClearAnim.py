import bpy

# Set the armature object name
armature_name = "PantherTracks"  # Replace with your armature's name

# Ensure the armature is the active object and set to object mode
bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]
bpy.ops.object.mode_set(mode='OBJECT')

# Get the armature object
armature = bpy.data.objects[armature_name]

# Clear NLA Tracks
if armature.animation_data:
    for track in armature.animation_data.nla_tracks:
        armature.animation_data.nla_tracks.remove(track)

    # Remove action
    if armature.animation_data.action:
        bpy.data.actions.remove(armature.animation_data.action)
        armature.animation_data.action = None

    # Clear all actions (including non-active ones) that are not used elsewhere
    for action in bpy.data.actions:
        if action.users == 0:
            bpy.data.actions.remove(action)

    # Remove the animation data itself
    armature.animation_data_clear()

print("All animation data cleared.")
