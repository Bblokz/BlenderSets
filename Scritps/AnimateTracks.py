import bpy

# Set the armature object name
armature_name = "PantherTracks"  # Replace with your armature's name
bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]
bpy.ops.object.mode_set(mode='POSE')

# Set frame start and end
frame_start = 1
frame_end = 30
rotation_angle = 360  # degrees

# Get the armature object
armature = bpy.data.objects[armature_name]

# Iterate over pose bones and animate those starting with 'W_L'
for bone in armature.pose.bones:
    if bone.name.startswith("W_L"):
        # Insert a keyframe at the start with initial rotation
        bone.rotation_mode = 'XYZ'
        bone.rotation_euler = (0, 0, 0)
        bone.keyframe_insert(data_path="rotation_euler", frame=frame_start)
        
        # Insert a keyframe at the end with final rotation (360 degrees around the y-axis)
        bone.rotation_euler = (0, rotation_angle * 0.0174533, 0)  # Convert degrees to radians
        bone.keyframe_insert(data_path="rotation_euler", frame=frame_end)

# Return to object mode
bpy.ops.object.mode_set(mode='OBJECT')
