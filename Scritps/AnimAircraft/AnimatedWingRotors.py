import bpy
import math

# ---------------- user-adjustable settings ----------------

# If True, wipe out *all* existing animation (actions + NLA) on the armature
remove_anim = True

# Rotation speeds, in rotations per second
slow_speed_rps = 1    # slow variant
fast_speed_rps = 3    # fast variant
idle_speed_rps = 0.5  # idle variant

# Duration of each animation (in seconds)
duration_seconds = 5.0

# -----------------------------------------------------------

# Calculate frame range based on scene framerate
scene = bpy.context.scene
fps = scene.render.fps / scene.render.fps_base
total_frames = int(duration_seconds * fps)
frame_start = 1
frame_end = frame_start + total_frames

# Define the animations: (name, number_of_rotations)
animations = [
    ("Slow_CW",  -slow_speed_rps  * duration_seconds),
    ("Fast_CW",  -fast_speed_rps  * duration_seconds),
    ("Slow_CCW",  slow_speed_rps  * duration_seconds),
    ("Fast_CCW",  fast_speed_rps  * duration_seconds),
    ("Idle",     -idle_speed_rps  * duration_seconds),
]

# Get the selected armature
arm = bpy.context.view_layer.objects.active
if not arm or arm.type != 'ARMATURE':
    raise Exception("Please select an armature object before running this script.")

# ——— 1) Clear out the armature’s animation_data (actions + NLA) ———
if remove_anim and arm.animation_data:
    bpy.ops.object.mode_set(mode='OBJECT')
    arm.animation_data_clear()
    print("✔ Cleared animation_data on armature")

# ——— 2) Purge *all* Action datablocks ———
if remove_anim:
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    print("✔ Deleted all Action datablocks")

# Ensure we’re operating on that armature
bpy.context.view_layer.objects.active = arm

for name, rot_count in animations:
    # Switch into Pose Mode
    bpy.ops.object.mode_set(mode='POSE')

    # Create new action, named exactly as desired
    new_action = bpy.data.actions.new(name=name)
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = new_action

    # Animate each rotor bone
    for pb in arm.pose.bones:
        if pb.name.startswith("B_WingRotor_R") or pb.name.startswith("B_WingRotor_L"):
            pb.rotation_mode = 'XYZ'
            # Initial keyframe at zero rotation
            pb.rotation_euler = (0.0, 0.0, 0.0)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame_start)
            # Final rotation around Z (blade‑spin axis)
            final_rad = math.radians(rot_count * 360.0)
            pb.rotation_euler = (0.0, final_rad, 0.0)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame_end)

    # Make all keyframes linear
    for fc in new_action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'

    # Push this action into its own NLA strip, named after the action
    track = arm.animation_data.nla_tracks.new()
    strip = track.strips.new(name, frame_start, new_action)
    strip.name = name

    # Return to Object Mode before next action
    bpy.ops.object.mode_set(mode='OBJECT')

# At the end, clear the active action so only NLA strips remain
if arm.animation_data:
    arm.animation_data.action = None

print("✔ Wing rotor animations created and NLA‑strips named: " +
      ", ".join(name for name, _ in animations))
