import bpy

TARGET_NAME = "LightMapUV"

def set_active_uv_name(obj):
    data = getattr(obj, "data", None)
    if data is None or not hasattr(data, "uv_layers"):
        print(f"{obj.name}: no UV layers on this data-block.")
        return

    uv_layers = data.uv_layers
    if len(uv_layers) == 0:
        print(f"{obj.name}: has no UV maps.")
        return

    # Use index (reliable) rather than identity for the active UV
    active_index = uv_layers.active_index
    active_uv = uv_layers[active_index]

    # 1) Remove INACTIVE UV maps already named TARGET_NAME (avoid name conflict)
    #    Use indices and remove in reverse order to avoid index shifting.
    dup_indices = [i for i, uv in enumerate(uv_layers) if i != active_index and uv.name == TARGET_NAME]
    for i in sorted(dup_indices, reverse=True):
        try:
            uv_layers.remove(uv_layers[i])
        except RuntimeError as e:
            print(f"{obj.name}: couldn't remove duplicate '{TARGET_NAME}' at index {i} ({e}).")

    # 2) Rename the active UV map only if needed
    if active_uv.name != TARGET_NAME:
        try:
            active_uv.name = TARGET_NAME
            print(f"{obj.name}: active UV renamed to '{TARGET_NAME}'.")
        except RuntimeError as e:
            print(f"{obj.name}: failed to rename active UV ({e}).")
    else:
        # Already correct; nothing changed
        print(f"{obj.name}: active UV already named '{TARGET_NAME}', no changes made.")

# Ensure we're in Object Mode (as you run it from object mode)
if bpy.context.mode != 'OBJECT':
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except Exception:
        pass  # Proceed even if mode change isn't possible

# Process every object in the current scene (no selection assumptions)
for obj in bpy.context.scene.objects:
    set_active_uv_name(obj)

print("Done: primary/active UV maps set to 'LightMapUV' (inactive duplicates removed; no unnecessary changes).")
