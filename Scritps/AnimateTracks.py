import bpy

armature_name = "PantherTracks"
name_base = "Anim_Tracks_"
name_vehicle = "PantherG_"

# Array of animations, each elements will generate one animation with elm = ("suffix", #DegreesLeftWheelsTurn, #DegreesRightWheelsTurn)
# 720 degrees = 2*360 with 72 frames correlates to one full wheel turn / 30 FPS 
# So, 720 versus 360 allows for the left wheels to move twice as fast as the right ones.
animations = [
    ("FastFWD", 720, 720),
    ("SlowFWD", 360, 360),
    ("FastBWD", -720, -720),
    ("SlowBWD", -360, -360),
    ("TurnStationaryLeft", -360, 720),
    ("TurnStationaryRight", 720, -360),
    ("TurnLeft", 360, 720),
    ("TurnRight", 720, 360)
]

bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]
armature = bpy.data.objects[armature_name]

for anim_name, rotation_angleL, rotation_angleR in animations:
    action_name = name_base + name_vehicle + anim_name

    bpy.ops.object.mode_set(mode='POSE')

    # Create a new action
    new_action = bpy.data.actions.new(name=action_name)
    armature.animation_data_create()
    
    # Before assigning the new action, push the existing action to the NLA if there is one (saves unused data)
    if armature.animation_data.action:
        track = armature.animation_data.nla_tracks.new()
        track.strips.new(armature.animation_data.action.name, frame_start, armature.animation_data.action)
        armature.animation_data.action.use_fake_user = True  # Optional: prevent action from being unlinked

    # Assign the new action to the armature
    armature.animation_data.action = new_action

    # Frame settings
    frame_start = 1
    frame_end = 72

    # Animate each relevant bone
    for bone in armature.pose.bones:
        if bone.name.startswith("W_L") or bone.name.startswith("W_R"):
            bone.rotation_mode = 'XYZ'
            # Set initial rotation and insert a keyframe
            bone.rotation_euler = (0, 0, 0)
            bone.keyframe_insert(data_path="rotation_euler", frame=frame_start)
            # Set final rotation based on whether it's left or right
            final_rotation = rotation_angleR if bone.name.startswith("W_R") else rotation_angleL
            bone.rotation_euler = (0, final_rotation * 0.0174533, 0)
            bone.keyframe_insert(data_path="rotation_euler", frame=frame_end)

            # Change interpolation to linear!! for all keyframes in this action
            for fcurve in new_action.fcurves:
                for keyframe_point in fcurve.keyframe_points:
                    keyframe_point.interpolation = 'LINEAR'
                    
    bpy.ops.object.mode_set(mode='OBJECT')

print("All specified animations have been created.")
