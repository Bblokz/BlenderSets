import bpy

armature_name = "Armor"
name_base = "Anim_"
name_object = "SKDFZ-7_Sides_"

# Default offset for moving the bones
offset = 1.5

# Frame settings for animation
frame_start = 1
frame_end = 30  # For a 30 FPS animation, 1 second long

bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]
armature = bpy.data.objects[armature_name]

# Function to animate bones
def animate_bone(bone_name, animation_name, is_up):
    action_name = name_base + name_object + animation_name

    bpy.ops.object.mode_set(mode='POSE')

    # Create a new action
    new_action = bpy.data.actions.new(name=action_name)
    armature.animation_data_create()
    
    # Before assigning the new action, push the existing action to the NLA if there is one
    if armature.animation_data.action:
        track = armature.animation_data.nla_tracks.new()
        track.strips.new(armature.animation_data.action.name, frame_start, armature.animation_data.action)
        armature.animation_data.action.use_fake_user = True

    # Assign the new action to the armature
    armature.animation_data.action = new_action

    bone = armature.pose.bones[bone_name]

    # Insert initial keyframe
    bone.location = (0, 0, 0) if is_up else (0, 0, -offset)
    bone.keyframe_insert(data_path="location", frame=frame_start)

    # Insert final keyframe
    bone.location = (0, 0, 0) if not is_up else (0, 0, -offset)
    bone.keyframe_insert(data_path="location", frame=frame_end)

    # Change interpolation to ease in/out for a fast-to-slow movement
    for fcurve in new_action.fcurves:
        for keyframe_point in fcurve.keyframe_points:
            keyframe_point.interpolation = 'SINE' if is_up else 'BEZIER'
    
    bpy.ops.object.mode_set(mode='OBJECT')

# Animate both bones going down
animate_bone('B_Left', 'Down', False)
animate_bone('B_Right', 'Down', False)

# Animate both bones going up
animate_bone('B_Left', 'Up', True)
animate_bone('B_Right', 'Up', True)

print("All specified animations have been created and saved to NLA.")
