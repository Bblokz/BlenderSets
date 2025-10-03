bl_info = {
    "name": "Boolean Multi-Cutter (Target via Dropdown, Cutters from Selection)",
    "blender": (2, 80, 0),
    "category": "Object",
    "description": "Choose a target via dropdown; add unique cutters from selection; apply Boolean Difference per cutter.",
}

import bpy
from bpy.types import Operator, Panel, PropertyGroup, UIList
from bpy.props import PointerProperty, CollectionProperty, IntProperty

# ──────────────────────────────────────────────────────────────────────────────
# Data model: a list item that points to a cutter object
# ──────────────────────────────────────────────────────────────────────────────
class BooleanCutterItem(PropertyGroup):
    object: PointerProperty(
        name="Cutter",
        type=bpy.types.Object,
        description="Object used as Boolean cutter",
    )

# ──────────────────────────────────────────────────────────────────────────────
# UI list to display cutters
# ──────────────────────────────────────────────────────────────────────────────
class OBJECT_UL_boolean_cutters(UIList):
    bl_idname = "OBJECT_UL_boolean_cutters"

    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        obj = item.object
        if obj:
            icon = "MESH_CUBE" if obj.type == "MESH" else "OBJECT_DATA"
            layout.prop(item, "object", text=obj.name, emboss=False, icon=icon)
        else:
            layout.label(text="(None)", icon="ERROR")

# ──────────────────────────────────────────────────────────────────────────────
# Operators: manage the cutter list
# ──────────────────────────────────────────────────────────────────────────────
class OBJECT_OT_boolean_cutters_add_selected(Operator):
    """Add all selected mesh objects as cutters (excludes the chosen target and duplicates)"""
    bl_idname = "object.boolean_cutters_add_selected"
    bl_label = "Add Selected as Cutters"

    def execute(self, context):
        scene = context.scene
        target = scene.boolean_target_obj

        existing = {it.object for it in scene.boolean_cutter_list if it.object}
        added = 0

        for obj in context.selected_objects:
            if obj is None or obj.type != "MESH":
                continue
            if target and obj == target:
                # Never add the target as a cutter
                continue
            if obj in existing:
                continue
            item = scene.boolean_cutter_list.add()
            item.object = obj
            existing.add(obj)
            added += 1

        if added == 0:
            self.report({'INFO'}, "No new cutters added (may be non-mesh, already in list, or is the target).")
        else:
            self.report({'INFO'}, f"Added {added} cutter(s).")

        scene.boolean_cutter_list_index = max(0, len(scene.boolean_cutter_list) - 1)
        return {'FINISHED'}


class OBJECT_OT_boolean_cutters_remove(Operator):
    """Remove the active cutter entry"""
    bl_idname = "object.boolean_cutters_remove"
    bl_label = "Remove Cutter"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return len(scene.boolean_cutter_list) > 0 and 0 <= scene.boolean_cutter_list_index < len(scene.boolean_cutter_list)

    def execute(self, context):
        scene = context.scene
        idx = scene.boolean_cutter_list_index
        scene.boolean_cutter_list.remove(idx)
        scene.boolean_cutter_list_index = min(idx, len(scene.boolean_cutter_list) - 1)
        return {'FINISHED'}


class OBJECT_OT_boolean_cutters_clear(Operator):
    """Clear all cutters"""
    bl_idname = "object.boolean_cutters_clear"
    bl_label = "Clear Cutters"

    def execute(self, context):
        scene = context.scene
        count = len(scene.boolean_cutter_list)
        scene.boolean_cutter_list.clear()
        scene.boolean_cutter_list_index = 0
        self.report({'INFO'}, f"Cleared {count} cutter(s).")
        return {'FINISHED'}

# ──────────────────────────────────────────────────────────────────────────────
# Apply: add & apply Boolean(DIFFERENCE) for each cutter to the TARGET (from dropdown)
# ──────────────────────────────────────────────────────────────────────────────
class OBJECT_OT_boolean_apply_from_cutters(Operator):
    bl_idname = "object.boolean_apply_from_cutters"
    bl_label = "Apply Difference From All Cutters"
    bl_description = "Apply a Boolean Difference for each cutter to the chosen target"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        target = scene.boolean_target_obj
        return (target is not None) and (target.type == 'MESH') and (len(scene.boolean_cutter_list) > 0)

    def execute(self, context):
        scene = context.scene
        target = scene.boolean_target_obj

        if target is None:
            self.report({'ERROR'}, "No target chosen.")
            return {'CANCELLED'}
        if target.type != "MESH":
            self.report({'ERROR'}, f"Target must be a Mesh. Current: {target.name} ({target.type})")
            return {'CANCELLED'}

        view_layer = context.view_layer
        prev_active = view_layer.objects.active
        prev_mode = context.mode

        # Ensure Object Mode
        if prev_mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception as e:
                self.report({'ERROR'}, f"Failed to switch to Object mode: {e}")
                return {'CANCELLED'}

        view_layer.objects.active = target

        applied = 0
        skipped = 0

        for item in list(scene.boolean_cutter_list):
            cutter = item.object
            if cutter is None:
                skipped += 1
                continue
            if cutter == target:
                # Shouldn't happen (we filtered on add), but double-safeguard
                skipped += 1
                continue
            if cutter.type != 'MESH':
                skipped += 1
                continue

            # Add Boolean Difference modifier
            try:
                mod_name = f"BoolDiff_{cutter.name}"
                mod = target.modifiers.new(name=mod_name, type='BOOLEAN')
                mod.operation = 'DIFFERENCE'
                mod.object = cutter
                # If you prefer: mod.solver = 'EXACT'
            except Exception:
                skipped += 1
                continue

            # Apply it
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
                applied += 1
            except Exception:
                # Cleanup best-effort
                try:
                    target.modifiers.remove(mod)
                except Exception:
                    pass
                skipped += 1

        # Restore previous active object if still valid
        try:
            if prev_active is not None:
                view_layer.objects.active = prev_active
        except Exception:
            pass

        self.report({'INFO'}, f"Done: {applied} applied, {skipped} skipped.")
        return {'FINISHED'}

# ──────────────────────────────────────────────────────────────────────────────
# UI Panel
# ──────────────────────────────────────────────────────────────────────────────
class VIEW3D_PT_boolean_multi_cutter_panel(Panel):
    bl_label = "Boolean Multi-Cutter"
    bl_idname = "VIEW3D_PT_boolean_multi_cutter_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Boolean Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Target via dropdown (cached; independent from selection)
        box = layout.box()
        box.label(text="Target (choose via dropdown):")
        box.prop(scene, "boolean_target_obj", text="Target Object")

        layout.separator()

        # Cutters list (add only from selection; no picker button)
        row = layout.row()
        row.template_list(
            "OBJECT_UL_boolean_cutters",
            "",
            scene, "boolean_cutter_list",
            scene, "boolean_cutter_list_index",
            rows=6,
        )
        col = row.column(align=True)
        col.operator("object.boolean_cutters_add_selected", text="", icon="ADD")
        col.operator("object.boolean_cutters_remove", text="", icon="REMOVE")
        col.separator()
        col.operator("object.boolean_cutters_clear", text="", icon="TRASH")

        layout.separator()
        layout.operator("object.boolean_apply_from_cutters",
                        text="Apply Difference From All Cutters",
                        icon="MOD_BOOLEAN")

# ──────────────────────────────────────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────────────────────────────────────
classes = (
    BooleanCutterItem,
    OBJECT_UL_boolean_cutters,
    OBJECT_OT_boolean_cutters_add_selected,
    OBJECT_OT_boolean_cutters_remove,
    OBJECT_OT_boolean_cutters_clear,
    OBJECT_OT_boolean_apply_from_cutters,
    VIEW3D_PT_boolean_multi_cutter_panel,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.boolean_target_obj = PointerProperty(
        type=bpy.types.Object,
        name="Boolean Target",
        description="Target object that will receive Boolean Difference",
    )
    bpy.types.Scene.boolean_cutter_list = CollectionProperty(type=BooleanCutterItem)
    bpy.types.Scene.boolean_cutter_list_index = IntProperty(default=0)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.boolean_target_obj
    del bpy.types.Scene.boolean_cutter_list
    del bpy.types.Scene.boolean_cutter_list_index

if __name__ == "__main__":
    register()
