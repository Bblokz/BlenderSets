import bpy
import math

# -------------------------------------------------------------------
# User Settings
# -------------------------------------------------------------------
ARMATURE_NAME = "Armature"   # <-- set this to your armature object name
ACTION_NAME   = "Anim_Wheels_RollWorldY"

LEFT_BONE_NAME  = "B_LeftWheel"
RIGHT_BONE_NAME = "B_RightWheel"

FRAME_START = 1
FRAME_END   = 72

# 360 degrees over 72 frames = 1 full spin at 30FPS (if you interpret 72f as 2.4s)
SPIN_DEGREES = 360.0


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def get_is_valid_armature_object(armature_object: bpy.types.Object) -> bool:
    if armature_object is None:
        print("[WheelAnim] Armature object is None.")
        return False
    if armature_object.type != 'ARMATURE':
        print(f"[WheelAnim] Object '{armature_object.name}' is not an Armature (type={armature_object.type}).")
        return False
    return True


def get_is_valid_pose_bone(armature_object: bpy.types.Object, bone_name: str) -> bool:
    if bone_name not in armature_object.pose.bones:
        print(f"[WheelAnim] Pose bone '{bone_name}' not found on armature '{armature_object.name}'.")
        return False
    return True


def set_linear_interpolation(action: bpy.types.Action) -> None:
    for fcurve in action.fcurves:
        for key_point in fcurve.keyframe_points:
            key_point.interpolation = 'LINEAR'


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def create_single_wheel_roll_animation() -> None:
    armature_object = bpy.data.objects.get(ARMATURE_NAME)
    if not get_is_valid_armature_object(armature_object):
        return

    if not get_is_valid_pose_bone(armature_object, LEFT_BONE_NAME):
        return
    if not get_is_valid_pose_bone(armature_object, RIGHT_BONE_NAME):
        return

    left_wheel_bone = armature_object.pose.bones[LEFT_BONE_NAME]
    right_wheel_bone = armature_object.pose.bones[RIGHT_BONE_NAME]

    # Make armature active & enter pose mode
    bpy.context.view_layer.objects.active = armature_object
    armature_object.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')

    # Create / assign action
    action = bpy.data.actions.new(name=ACTION_NAME)
    armature_object.animation_data_create()
    armature_object.animation_data.action = action

    spin_radians = math.radians(SPIN_DEGREES)

    # Keyframes:
    # We rotate around the Y direction, but since the right wheel bone points -Y,
    # we invert the spin sign so both wheels roll the same way visually.
    #
    # Assumption: both bones roll around their *local* Y axis.
    # Left bone points +Y => +spin
    # Right bone points -Y => -spin

    for wheel_bone, wheel_spin_sign in (
        (left_wheel_bone,  +1.0),
        (right_wheel_bone, -1.0),
    ):
        wheel_bone.rotation_mode = 'XYZ'

        # Start (no roll)
        wheel_bone.rotation_euler = (0.0, 0.0, 0.0)
        wheel_bone.keyframe_insert(data_path="rotation_euler", frame=FRAME_START)

        # End (rolled)
        final_spin = wheel_spin_sign * spin_radians
        wheel_bone.rotation_euler = (0.0, final_spin, 0.0)
        wheel_bone.keyframe_insert(data_path="rotation_euler", frame=FRAME_END)

    set_linear_interpolation(action)

    # Back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    print(f"[WheelAnim] Created action '{ACTION_NAME}' on armature '{ARMATURE_NAME}'.")
    print(f"[WheelAnim] Bones: {LEFT_BONE_NAME} (spin +Y), {RIGHT_BONE_NAME} (spin -Y).")


if __name__ == "__main__":
    create_single_wheel_roll_animation()