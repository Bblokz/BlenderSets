import bpy

# Base information for the action names
armature_name = "PantherG_Turret"
name_base = "Anim_Turret_"
name_vehicle = "PantherG_"

# Array of recoil animations, each element will generate one animation
# Each element in the array is a tuple: (animation_suffix, recoil_distance)
recoil_animations = [
    ("LightRecoil", 0.1),  # Light recoil
    ("HeavyRecoil", 0.3)   # Heavy recoil
]

bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]
armature = bpy.data.objects[armature_name]

for anim_suffix, recoil_distance in recoil_animations:
    action_name = name_base + name_vehicle + anim_suffix

    bpy.ops.object.mode_set(mode='POSE')

    new_action = bpy.data.actions.new(name=action_name)
    armature.animation_data_create()
    
    # Before assigning the new action, push the existing action to the NLA if there is one
    # (saves unsaved anim data)
    if armature.animation_data.action:
        track = armature.animation_data.nla_tracks.new()
        track.strips.new(armature.animation_data.action.name, 1, armature.animation_data.action)
        armature.animation_data.action.use_fake_user = True

    # Assign the new action to the armature
    armature.animation_data.action = new_action

    # Identify the gun bone
    gun_bone = armature.pose.bones['B_Gun']

    # Frame settings for the recoil
    frame_start = 1
    frame_end = 30

    # Set initial position and insert a keyframe
    gun_bone.location = (0, 0, 0)
    gun_bone.keyframe_insert(data_path="location", frame=frame_start)

    # Set recoil position and insert a keyframe at the middle of the animation
    gun_bone.location[1] -= recoil_distance 
    gun_bone.keyframe_insert(data_path="location", frame=frame_end / 2)

    # Return to the original position and insert a keyframe
    gun_bone.location = (0, 0, 0)
    gun_bone.keyframe_insert(data_path="location", frame=frame_end)

#    # Set interpolation to linear for all keyframes
#    for fcurve in new_action.fcurves:
#        for keyframe_point in fcurve.keyframe_points:
#            keyframe_point.interpolation = 'LINEAR'
                    
    bpy.ops.object.mode_set(mode='OBJECT')

print("All specified recoil animations have been created.")
