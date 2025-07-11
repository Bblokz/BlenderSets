import bpy

# Armature and naming
armature_name = "Armature"
name_base      = "Anim_Tracks_"
name_vehicle   = "PZ38_T_"

# Steering angles (in degrees)
MovingSteer = 20.0
FullSteer   = 45.0

# Conversion from degrees to radians
deg2rad = 0.0174533

# Array of animations: (suffix, #deg left wheels rotation, #deg right wheels rotation)
animations = [
    ("FastFWD",             720,   720),
    ("FastBWD",            -720,  -720),
    ("TPose",                 0,     0),
    ("TurnStationaryLeft",  -360,   720),
    ("TurnStationaryRight",  720,  -360),
    ("TurnLeft",             360,   720),
    ("TurnRight",            720,   360)
]

# Activate our armature
armature = bpy.data.objects[armature_name]
bpy.context.view_layer.objects.active = armature

# Ensure we're in OBJECT mode before we start
bpy.ops.object.mode_set(mode='OBJECT')

for anim_name, rotL_deg, rotR_deg in animations:
    action_name  = f"{name_base}{name_vehicle}{anim_name}"
    frame_start  = 1
    frame_end    = 72

    # Switch into Pose mode
    bpy.ops.object.mode_set(mode='POSE')

    # Create new action and push old one to NLA if present
    new_action = bpy.data.actions.new(name=action_name)
    armature.animation_data_create()
    if armature.animation_data.action:
        track = armature.animation_data.nla_tracks.new()
        track.strips.new(
            armature.animation_data.action.name,
            frame_start,
            armature.animation_data.action
        )
        armature.animation_data.action.use_fake_user = True
    armature.animation_data.action = new_action

    # Precompute radians
    rotL_rad   = rotL_deg   * deg2rad
    rotR_rad   = rotR_deg   * deg2rad
    moving_rad = MovingSteer * deg2rad
    full_rad   = FullSteer   * deg2rad

    for bone in armature.pose.bones:
        if not bone.name.startswith(("W_L", "W_R")):
            continue

        bone.rotation_mode = 'XYZ'
        roll_rad = rotR_rad if bone.name.startswith("W_R") else rotL_rad

        # Front wheels
        if bone.name in ("W_L0", "W_R0"):
            if   anim_name == "TurnStationaryLeft":  steer_rad =  moving_rad
            elif anim_name == "TurnStationaryRight": steer_rad = -moving_rad
            elif anim_name == "TurnLeft":            steer_rad =  full_rad
            elif anim_name == "TurnRight":           steer_rad = -full_rad
            else:                                     steer_rad = 0.0

            # Start: yaw only
            bone.rotation_euler = (0.0, 0.0, steer_rad)
            bone.keyframe_insert(data_path="rotation_euler", frame=frame_start)
            # End: roll + same yaw
            bone.rotation_euler = (0.0, roll_rad, steer_rad)
            bone.keyframe_insert(data_path="rotation_euler", frame=frame_end)

        # Track wheels
        else:
            bone.rotation_euler = (0.0, 0.0, 0.0)
            bone.keyframe_insert(data_path="rotation_euler", frame=frame_start)
            bone.rotation_euler = (0.0, roll_rad, 0.0)
            bone.keyframe_insert(data_path="rotation_euler", frame=frame_end)

    # Make all keyframes linear
    for fcurve in new_action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'LINEAR'

    # Back to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

print("All half-track animations have been created.")
