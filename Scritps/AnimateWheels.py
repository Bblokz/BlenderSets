import bpy

# -------------------------------------------------------------------
# User Settings
# -------------------------------------------------------------------
armature_name = "WheeledVehicleArmature"   # The name of your armature object
name_base = "Anim_Wheels_"
name_vehicle = "WheeledVehicle_"

# 720 degrees over 72 frames = 2 full spins at 30FPS
# 360 degrees over 72 frames = 1 full spin at 30FPS
# Steering angles are in degrees; we’ll convert to radians later.
# Format: (suffix, wheel_spin_degrees, front_wheel_steer_degrees)
#   - wheel_spin_degrees: rotation around the Y axis (rolling)
#   - front_wheel_steer_degrees: rotation around the Z axis (yaw for steering)
animations = [
    ("FWD",                720,    0),
    ("BWD",               -720,    0),
    ("TPose",               0,     0),
    ("TurnStationaryLeft", 360,   45),   # half speed spin, +45° steering (left)
    ("TurnStationaryRight",360,  -45),   # half speed spin, -45° steering (right)
    ("TurnLeft",           720,   30),   # full spin, +30° steering
    ("TurnRight",          720,  -30),   # full spin, -30° steering
    ("BackwardsTurnLeft", -720,   30),   # backward spin, +30° steering
    ("BackwardsTurnRight",-720,  -30)    # backward spin, -30° steering
]

# Frames for the animation range
frame_start = 1
frame_end = 72

# Radians conversion factor
deg_to_rad = 0.0174533

# -------------------------------------------------------------------
# Helper: Gather wheel bones and identify front wheels
# -------------------------------------------------------------------
def identify_front_wheels(armature_obj):
    """
    Returns:
        all_wheels  : list of all wheel bone names (both L and R)
        front_wheels: set of bone names considered front wheels
    """
    pose_bones = armature_obj.pose.bones

    # Collect all wheel bones
    all_wheels = [bone.name for bone in pose_bones 
                  if bone.name.startswith("W_L") or bone.name.startswith("W_R")]
    
    # Count total wheels
    total_wheels = len(all_wheels)
    
    # Sort wheel names to ensure consistent ordering
    all_wheels.sort()
    
    # Identify front wheels based on total wheel count
    if total_wheels == 8:
        # If 8 wheels total, front wheels are W_L1, W_L2, W_R1, W_R2
        front_wheels = {"W_L1", "W_L2", "W_R1", "W_R2"}
    elif total_wheels == 6:
        # If 6 wheels total, front wheels are W_L1, W_R1
        front_wheels = {"W_L1", "W_R1"}
    elif total_wheels == 4:
        # If 4 wheels total, front wheels are W_L1, W_R1
        front_wheels = {"W_L1", "W_R1"}
    else:
        # Fallback (just assume the first wheel on each side are front wheels)
        front_wheels = {"W_L1", "W_R1"}
    
    return all_wheels, front_wheels

# -------------------------------------------------------------------
# Main: Create the animations
# -------------------------------------------------------------------
def create_wheel_animations():
    # Ensure we have a valid armature object
    if armature_name not in bpy.data.objects:
        print(f"Armature '{armature_name}' not found in the scene.")
        return
    
    armature = bpy.data.objects[armature_name]
    
    # Identify all wheel bones and which ones are front wheels
    all_wheels, front_wheels = identify_front_wheels(armature)
    print("All wheel bones:", all_wheels)
    print("Front wheel bones:", front_wheels)

    # Make the armature the active object
    bpy.context.view_layer.objects.active = armature
    
    # Go through each animation
    for (anim_suffix, spin_deg, steer_deg) in animations:
        action_name = name_base + name_vehicle + anim_suffix
        
        # Switch to Pose Mode
        bpy.ops.object.mode_set(mode='POSE')
        
        # Create a new Action
        new_action = bpy.data.actions.new(name=action_name)
        armature.animation_data_create()
        
        # If there's an existing action on the armature, push it to NLA
        if armature.animation_data.action:
            track = armature.animation_data.nla_tracks.new()
            old_action = armature.animation_data.action
            track.strips.new(old_action.name, frame_start, old_action)
            old_action.use_fake_user = True
        
        # Assign the new action
        armature.animation_data.action = new_action
        
        # Keyframe each wheel bone
        for bone in armature.pose.bones:
            if bone.name.startswith("W_L") or bone.name.startswith("W_R"):
                bone.rotation_mode = 'XYZ'
                
                # Calculate spin & steering in radians
                spin_rad = spin_deg * deg_to_rad
                # Steering only applies if this is a front wheel
                final_steer_deg = steer_deg if bone.name in front_wheels else 0.0
                steer_rad = final_steer_deg * deg_to_rad
                
                # We want the wheel’s steering to be *full* at the start
                # So from frame_start to frame_end, the Z axis is constant at steer_rad
                # Meanwhile, the Y axis goes from 0 to spin_rad to simulate wheel rolling.
                
                # Key at start frame
                bone.rotation_euler = (0.0, 0.0, steer_rad)
                bone.keyframe_insert(data_path="rotation_euler", frame=frame_start)
                
                # Key at end frame
                bone.rotation_euler = (0.0, spin_rad, steer_rad)
                bone.keyframe_insert(data_path="rotation_euler", frame=frame_end)
        
        # Set linear interpolation for all FCurves in this new action
        for fcurve in new_action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'LINEAR'
        
        # Switch back to Object Mode at the end of each loop
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"Created animation: {action_name}")
    
    print("All specified wheeled animations have been created.")

# -------------------------------------------------------------------
# Run it
# -------------------------------------------------------------------
if __name__ == "__main__":
    create_wheel_animations()
