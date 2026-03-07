import bpy
import math
import mathutils

# -------------------------------------------------------------------
# User Settings
# -------------------------------------------------------------------
ARMATURE_NAME = "37mmFlak"

# Wheels (based on your log)
WHEEL_ACTION_NAME = "Anim_Wheels_RollWorldY"
LEFT_WHEEL_BONE_NAME = "B_LeftWheel"
RIGHT_WHEEL_BONE_NAME = "B_RightWheel"

WHEEL_FRAME_START = 1
WHEEL_FRAME_END = 72
SPIN_DEGREES = 360.0

# Turret / mantlet bones
TURRET_BONE_NAME = "B_Turret"
MANTLET_BONE_NAME = "B_Mantlet"

# Turret pose settings
MAX_PITCH_DEGREES = 35.0
MIN_PITCH_DEGREES = -15.0
YAW_REACH_DEGREES = 90.0

# -------------------------------------------------------------------
# Rotation Axis Settings (IMPORTANT)
# -------------------------------------------------------------------
# These two settings control *which local axis* is used to build the quaternion for each rotation.
#
# How to choose the correct axis:
# - In Blender Pose Mode, select the bone and try rotating with:
#     R then X, R then Y, R then Z
#   The axis that visually matches the rotation you want is the one to use here.
#
# Convention:
# - Turret yaw: "turn left/right" (usually around an UP axis).
# - Mantlet pitch: "aim up/down" (usually around a RIGHT axis).
#
# What to put here:
# - "X", "Y", "Z" for positive local axis
# - "-X", "-Y", "-Z" for negative local axis
#
# Examples:
# - If turret yaws correctly with R+Z in pose mode => TURRET_YAW_AXIS = "Z"
# - If turret yaws correctly with R-Z (i.e., opposite) => TURRET_YAW_AXIS = "-Z"
# - If mantlet pitches correctly with R+Y => MANTLET_PITCH_AXIS = "Y"
# - If mantlet pitches correctly with R-X => MANTLET_PITCH_AXIS = "-X"
TURRET_YAW_AXIS = "Y"
MANTLET_PITCH_AXIS = "Z"

# If your yaw direction is reversed even with the correct axis, flip this sign.
# +1.0 means "positive degrees = rotate along axis"
# -1.0 means "positive degrees = rotate opposite along axis"
TURRET_YAW_SIGN = -1.0

# Pose action length (2 frames so Unreal imports them reliably)
POSE_FRAME_START = 1
POSE_FRAME_END = 2

# NLA (exportable strips without overlaps)
NLA_TRACK_NAME = "Generated_Anim_Strips_Main"
NLA_GAP_FRAMES = 2


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def degrees_to_radians(degrees: float) -> float:
    return math.radians(degrees)


def get_is_valid_armature_object(armature_object: bpy.types.Object) -> bool:
    if armature_object is None:
        print("[AnimGen] Armature object is None.")
        return False
    if armature_object.type != "ARMATURE":
        print(f"[AnimGen] Object '{armature_object.name}' is not an Armature (type={armature_object.type}).")
        return False
    return True


def get_is_valid_pose_bone(armature_object: bpy.types.Object, bone_name: str) -> bool:
    if armature_object is None:
        print(f"[AnimGen] Armature is None while validating bone '{bone_name}'.")
        return False
    if armature_object.pose is None:
        print(f"[AnimGen] Armature '{armature_object.name}' has no pose.")
        return False
    if bone_name not in armature_object.pose.bones:
        print(f"[AnimGen] Pose bone '{bone_name}' not found on armature '{armature_object.name}'.")
        return False
    return True


def ensure_pose_mode_for_armature(armature_object: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = armature_object
    armature_object.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")


def ensure_object_mode() -> None:
    bpy.ops.object.mode_set(mode="OBJECT")


def create_fresh_action(action_name: str) -> bpy.types.Action:
    existing_action = bpy.data.actions.get(action_name)
    if existing_action is not None:
        print(f"[AnimGen][Debug] Removing existing action '{action_name}' to recreate cleanly.")
        bpy.data.actions.remove(existing_action)

    new_action = bpy.data.actions.new(name=action_name)
    new_action.use_fake_user = True
    print(f"[AnimGen][Debug] Created action '{new_action.name}' (use_fake_user=True).")
    return new_action


def assign_action(armature_object: bpy.types.Object, action: bpy.types.Action) -> None:
    armature_object.animation_data_create()
    armature_object.animation_data.action = action
    print(f"[AnimGen][Debug] Assigned action '{action.name}' to '{armature_object.name}'.")


def get_or_create_nla_track(animation_data: bpy.types.AnimData, track_name: str) -> bpy.types.NlaTrack:
    for track in animation_data.nla_tracks:
        if track.name == track_name:
            return track
    new_track = animation_data.nla_tracks.new()
    new_track.name = track_name
    return new_track


def clear_all_strips(track: bpy.types.NlaTrack) -> None:
    while len(track.strips) > 0:
        track.strips.remove(track.strips[0])


def push_action_to_nla_sequential(
    nla_track: bpy.types.NlaTrack,
    action: bpy.types.Action,
    strip_start_frame: int,
    action_length_frames: int
) -> int:
    strip_end_frame = strip_start_frame + action_length_frames - 1
    new_strip = nla_track.strips.new(action.name, strip_start_frame, action)
    new_strip.frame_start = strip_start_frame
    new_strip.frame_end = strip_end_frame
    new_strip.action = action
    print(f"[AnimGen][Debug] NLA strip '{new_strip.name}' placed {strip_start_frame}-{strip_end_frame}.")
    return strip_end_frame + NLA_GAP_FRAMES


def set_linear_interpolation(action: bpy.types.Action) -> None:
    for fcurve in action.fcurves:
        for key_point in fcurve.keyframe_points:
            key_point.interpolation = "LINEAR"


def key_quaternion(bone: bpy.types.PoseBone, frame: int) -> None:
    bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
    print(f"[AnimGen][Debug] Keyed QUAT bone='{bone.name}' frame={frame} quat={tuple(bone.rotation_quaternion)}")


def key_euler(bone: bpy.types.PoseBone, frame: int) -> None:
    bone.keyframe_insert(data_path="rotation_euler", frame=frame)
    print(f"[AnimGen][Debug] Keyed EULER bone='{bone.name}' frame={frame} euler={tuple(bone.rotation_euler)}")


def axis_string_to_vector(axis_string: str) -> mathutils.Vector:
    axis_string_upper = axis_string.strip().upper()

    if axis_string_upper == "X":
        return mathutils.Vector((1.0, 0.0, 0.0))
    if axis_string_upper == "Y":
        return mathutils.Vector((0.0, 1.0, 0.0))
    if axis_string_upper == "Z":
        return mathutils.Vector((0.0, 0.0, 1.0))
    if axis_string_upper == "-X":
        return mathutils.Vector((-1.0, 0.0, 0.0))
    if axis_string_upper == "-Y":
        return mathutils.Vector((0.0, -1.0, 0.0))
    if axis_string_upper == "-Z":
        return mathutils.Vector((0.0, 0.0, -1.0))

    print(f"[AnimGen][Error] Invalid axis string '{axis_string}'. Using 'Z' as fallback.")
    return mathutils.Vector((0.0, 0.0, 1.0))


def set_bone_quat_rotation_local_axis(bone: bpy.types.PoseBone, axis: mathutils.Vector, angle_radians: float) -> None:
    bone.rotation_mode = "QUATERNION"
    bone.rotation_quaternion = mathutils.Quaternion(axis, angle_radians)


# -------------------------------------------------------------------
# Create Wheel Action
# -------------------------------------------------------------------
def create_wheel_roll_action(armature_object: bpy.types.Object) -> bpy.types.Action:
    print("[WheelAnim][Debug] Creating wheel roll action...")

    ensure_pose_mode_for_armature(armature_object)

    action = create_fresh_action(WHEEL_ACTION_NAME)
    assign_action(armature_object, action)

    left_bone = armature_object.pose.bones[LEFT_WHEEL_BONE_NAME]
    right_bone = armature_object.pose.bones[RIGHT_WHEEL_BONE_NAME]

    left_bone.rotation_mode = "XYZ"
    right_bone.rotation_mode = "XYZ"

    spin_radians = degrees_to_radians(SPIN_DEGREES)

    left_bone.rotation_euler = (0.0, 0.0, 0.0)
    key_euler(left_bone, WHEEL_FRAME_START)
    left_bone.rotation_euler = (0.0, +spin_radians, 0.0)
    key_euler(left_bone, WHEEL_FRAME_END)

    right_bone.rotation_euler = (0.0, 0.0, 0.0)
    key_euler(right_bone, WHEEL_FRAME_START)
    right_bone.rotation_euler = (0.0, -spin_radians, 0.0)
    key_euler(right_bone, WHEEL_FRAME_END)

    set_linear_interpolation(action)
    ensure_object_mode()

    print(f"[WheelAnim] Done: '{action.name}'.")
    return action


# -------------------------------------------------------------------
# Create Turret Pose Action (2 frames)
# -------------------------------------------------------------------
def create_turret_pose_action(
    armature_object: bpy.types.Object,
    action_name: str,
    turret_yaw_degrees: float,
    mantlet_pitch_degrees: float
) -> bpy.types.Action:
    print(f"[TurretPose][Debug] Creating pose action '{action_name}'...")

    ensure_pose_mode_for_armature(armature_object)

    action = create_fresh_action(action_name)
    assign_action(armature_object, action)

    turret_bone = armature_object.pose.bones[TURRET_BONE_NAME]
    mantlet_bone = armature_object.pose.bones[MANTLET_BONE_NAME]

    yaw_axis = axis_string_to_vector(TURRET_YAW_AXIS)
    pitch_axis = axis_string_to_vector(MANTLET_PITCH_AXIS)

    yaw_radians = degrees_to_radians(turret_yaw_degrees) * TURRET_YAW_SIGN
    pitch_radians = degrees_to_radians(mantlet_pitch_degrees)

    set_bone_quat_rotation_local_axis(turret_bone, yaw_axis, yaw_radians)
    set_bone_quat_rotation_local_axis(mantlet_bone, pitch_axis, pitch_radians)

    key_quaternion(turret_bone, POSE_FRAME_START)
    key_quaternion(mantlet_bone, POSE_FRAME_START)

    key_quaternion(turret_bone, POSE_FRAME_END)
    key_quaternion(mantlet_bone, POSE_FRAME_END)

    set_linear_interpolation(action)
    ensure_object_mode()

    print(f"[TurretPose] Done: '{action.name}'.")
    return action


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def create_all_animations() -> None:
    print("[AnimGen][Debug] Starting animation generation...")

    armature_object = bpy.data.objects.get(ARMATURE_NAME)
    if armature_object is None:
        print(f"[AnimGen][Error] Could not find object named '{ARMATURE_NAME}'.")
        print(f"[AnimGen][Debug] Available objects: {[obj.name for obj in bpy.data.objects]}")
        return

    if not get_is_valid_armature_object(armature_object):
        return

    required_bones = (
        LEFT_WHEEL_BONE_NAME,
        RIGHT_WHEEL_BONE_NAME,
        TURRET_BONE_NAME,
        MANTLET_BONE_NAME,
    )
    for required_bone in required_bones:
        if not get_is_valid_pose_bone(armature_object, required_bone):
            return

    armature_object.animation_data_create()
    nla_track = get_or_create_nla_track(armature_object.animation_data, NLA_TRACK_NAME)
    clear_all_strips(nla_track)

    strip_cursor = 1

    wheel_action = create_wheel_roll_action(armature_object)
    strip_cursor = push_action_to_nla_sequential(
        nla_track=nla_track,
        action=wheel_action,
        strip_start_frame=strip_cursor,
        action_length_frames=(WHEEL_FRAME_END - WHEEL_FRAME_START + 1),
    )

    turret_actions_to_make = [
        ("Anim_Turret_Base",       0.0,                0.0),
        ("Anim_Turret_BaseUp",     0.0,                MAX_PITCH_DEGREES),
        ("Anim_Turret_BaseDown",   0.0,                MIN_PITCH_DEGREES),

        ("Anim_Turret_Left",       +YAW_REACH_DEGREES,  0.0),
        ("Anim_Turret_LeftUp",     +YAW_REACH_DEGREES,  MAX_PITCH_DEGREES),
        ("Anim_Turret_LeftDown",   +YAW_REACH_DEGREES,  MIN_PITCH_DEGREES),

        ("Anim_Turret_Right",      -YAW_REACH_DEGREES,  0.0),
        ("Anim_Turret_RightUp",    -YAW_REACH_DEGREES,  MAX_PITCH_DEGREES),
        ("Anim_Turret_RightDown",  -YAW_REACH_DEGREES,  MIN_PITCH_DEGREES),
    ]

    for action_name, yaw_deg, pitch_deg in turret_actions_to_make:
        pose_action = create_turret_pose_action(armature_object, action_name, yaw_deg, pitch_deg)
        strip_cursor = push_action_to_nla_sequential(
            nla_track=nla_track,
            action=pose_action,
            strip_start_frame=strip_cursor,
            action_length_frames=(POSE_FRAME_END - POSE_FRAME_START + 1),
        )

    print("[AnimGen][Debug] Done.")
    print("[AnimGen][Debug] Export tip: In FBX export enable either:")
    print("  - Bake Animation > All Actions (exports each Action), OR")
    print("  - Bake Animation > NLA Strips (exports strips we created sequentially).")
    print("[AnimGen][Debug] If yaw is flipped: change TURRET_YAW_AXIS to '-Z' or flip TURRET_YAW_SIGN.")


if __name__ == "__main__":
    create_all_animations()