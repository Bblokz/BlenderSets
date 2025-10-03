import bpy
import math

# ---------------- user‑adjustable settings ----------------

# If True, wipe out *all* existing animation (actions + NLA) on the armature
remove_anim = True

# Default rotor spin speed (CW is negative rotation)
rotor_speed_rps = 3.0

# Two extra “fly straight” variants
straight_speed1_rps = 1.5
straight_speed2_rps = 4.5

# Duration of each animation (in seconds)
duration_seconds = 5.0

# -----------------------------------------------------------

# Compute frame range
scene = bpy.context.scene
fps = scene.render.fps / scene.render.fps_base
total_frames = int(duration_seconds * fps)
frame_start = 1
frame_end = frame_start + total_frames

# Define flight animations: (name, horiz_angle_deg, vert_angle_deg, rotor_speed_rps)
# horiz_angle: positive = stabilizers pitched up (world +Z)
# vert_angle: positive = stabilizer yawed to right (world +Y)
flight_anims = [
    ("Fly_Straight_Default",  0.0,   0.0, rotor_speed_rps),
    ("Fly_Straight_Slow",     0.0,   0.0, straight_speed1_rps),
    ("Fly_Straight_Fast",     0.0,   0.0, straight_speed2_rps),
    ("Dive",                 30.0,   0.0, rotor_speed_rps),
    ("Climb",               -30.0,   0.0, rotor_speed_rps),
    ("Bank_Left",             0.0, -35.0, rotor_speed_rps),
    ("Bank_Right",            0.0,  35.0, rotor_speed_rps),
]

# Get the active armature
arm = bpy.context.view_layer.objects.active
if not arm or arm.type != 'ARMATURE':
    raise Exception("Please select an armature before running the script.")

# ——— 1) Clear existing animation_data ———
if remove_anim and arm.animation_data:
    bpy.ops.object.mode_set(mode='OBJECT')
    arm.animation_data_clear()
    print("✔ Cleared animation_data on armature")

# ——— 2) Delete all Action datablocks ———
if remove_anim:
    for act in list(bpy.data.actions):
        bpy.data.actions.remove(act)
    print("✔ Deleted all Action datablocks")

# Re‑activate armature
bpy.context.view_layer.objects.active = arm

for name, horiz_deg, vert_deg, speed_rps in flight_anims:
    # Switch into Pose Mode and create a fresh Action
    bpy.ops.object.mode_set(mode='POSE')
    action = bpy.data.actions.new(name=name)
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = action

    # Precompute rotor spin
    rot_deg = -speed_rps * duration_seconds * 360.0
    rot_rad = math.radians(rot_deg)

    # Keyframe each relevant bone
    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'

        # 1) Rotors: spin around local Z (blade axis)
        if pb.name.startswith("B_Rotor"):
            # start
            pb.rotation_euler = (0.0, 0.0, 0.0)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame_start)
            # end
            pb.rotation_euler = (rot_rad, 0.0, 0.0)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame_end)

        # 2) Horizontal stabilizers: rotate around local Y
        elif pb.name.startswith("B_HorizontalStabilizer_L") or pb.name.startswith("B_HorizontalStabilizer_R"):
            # banking special‑case
            if name == "Bank_Left":
                # left up (+30°), right down (‑30°)
                if pb.name.startswith("B_HorizontalStabilizer_L"):
                    angle_h = math.radians(30.0)
                else:
                    angle_h = math.radians(-30.0)
            elif name == "Bank_Right":
                # right up (+30°), left down (‑30°)
                if pb.name.startswith("B_HorizontalStabilizer_R"):
                    angle_h = math.radians(30.0)
                else:
                    angle_h = math.radians(-30.0)
            else:
                # default pitch for dive/climb/straight
                angle_h = math.radians(horiz_deg)

            # insert keyframes
            pb.rotation_euler = (0.0, angle_h, 0.0)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame_start)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame_end)

        # 3) Vertical stabilizer: rotate around local Z
        elif pb.name.startswith("B_VerticalStabilizer1"):
            angle_v = math.radians(vert_deg)
            pb.rotation_euler = (0.0, 0.0, angle_v)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame_start)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame_end)

    # Make the keyframes linear
    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'

    # Return to Object Mode, push into NLA with matching strip name
    bpy.ops.object.mode_set(mode='OBJECT')
    track = arm.animation_data.nla_tracks.new()
    strip = track.strips.new(name, frame_start, action)
    strip.name = name

# Finally clear the active action so only NLA strips remain
if arm.animation_data:
    arm.animation_data.action = None

print("✔ Created animations:", ", ".join(a[0] for a in flight_anims))
