bl_info = {
    "name": "UV Hepta Atlas",
    "blender": (2, 80, 0),
    "category": "Object",
    "description": "Arrange UVs of seven objects into a custom 2×2 atlas with subdivided bottom-right quadrant",
}

import bpy
from mathutils import Vector

# Operator: scales and offsets UVs of seven selected objects into atlas layout
class OBJECT_OT_uv_hepta_atlas_operator(bpy.types.Operator):
    bl_idname = "object.uv_hepta_atlas_operator"
    bl_label = "Pack 7 into Hepta Atlas"
    bl_description = "Pack UVs of seven objects: three full quadrants + four subdivided in the last quadrant"
    
    @classmethod
    def poll(cls, context):
        sc = context.scene
        # Ensure all seven slots are set
        return all(getattr(sc, f"hepta_obj{i}") for i in range(1, 8))
    
    def execute(self, context):
        sc = context.scene
        # Collect objects in order
        objs = [sc.hepta_obj1, sc.hepta_obj2, sc.hepta_obj3,
                sc.hepta_obj4, sc.hepta_obj5, sc.hepta_obj6, sc.hepta_obj7]
        
        # Validation: distinct meshes with one material and a UV map
        if len(set(objs)) != 7:
            self.report({'ERROR'}, "Please select seven different objects")
            return {'CANCELLED'}
        for obj in objs:
            if obj.type != 'MESH':
                self.report({'ERROR'}, f"{obj.name} is not a mesh")
                return {'CANCELLED'}
            if len(obj.material_slots) != 1:
                self.report({'ERROR'}, f"{obj.name} must have exactly one material slot")
                return {'CANCELLED'}
            if not obj.data.uv_layers:
                self.report({'ERROR'}, f"{obj.name} has no UV map")
                return {'CANCELLED'}
        
        # Offsets for first three (full quadrants, scale=0.5)
        full_offsets = [
            Vector((0.0, 0.5)),  # top-left
            Vector((0.5, 0.5)),  # top-right
            Vector((0.0, 0.0)),  # bottom-left
        ]
        # Offsets for last four (sub-quadrants of bottom-right quarter, scale=0.25)
        sub_offsets = [
            Vector((0.5, 0.25)),  # subdivided top-left of bottom-right
            Vector((0.75, 0.25)), # subdivided top-right
            Vector((0.5, 0.0)),   # subdivided bottom-left
            Vector((0.75, 0.0)),  # subdivided bottom-right
        ]
        
        # Process first three objects: scale=0.5 then apply their offsets
        for obj, offset in zip(objs[:3], full_offsets):
            mesh = obj.data
            uv_data = mesh.uv_layers.active.data
            for luv in uv_data:
                luv.uv *= 0.5
                luv.uv += offset
        
        # Process last four: scale=0.25 then apply sub-offsets
        for obj, offset in zip(objs[3:], sub_offsets):
            mesh = obj.data
            uv_data = mesh.uv_layers.active.data
            for luv in uv_data:
                luv.uv *= 0.25
                luv.uv += offset
        
        self.report({'INFO'}, "Hepta atlas UVs applied")
        return {'FINISHED'}


# Panel: N-menu under "UV Hepta Atlas"
class VIEW3D_PT_uv_hepta_atlas_panel(bpy.types.Panel):
    bl_label = "UV Hepta Atlas"
    bl_idname = "VIEW3D_PT_uv_hepta_atlas_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UV Hepta Atlas'

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        
        layout.label(text="Select seven objects:")
        for i, corner in enumerate([
            "TL", "TR", "BL", 
            "Sub TL", "Sub TR", "Sub BL", "Sub BR"
        ], start=1):
            layout.prop(sc, f"hepta_obj{i}", text=f"Object {i} ({corner})")
        
        layout.separator()
        layout.operator("object.uv_hepta_atlas_operator", text="Pack Hepta Atlas")


# Registration
classes = (
    OBJECT_OT_uv_hepta_atlas_operator,
    VIEW3D_PT_uv_hepta_atlas_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    for i in range(1, 8):
        bpy.types.Scene.__dict__[f"hepta_obj{i}"] = bpy.props.PointerProperty(
            name=f"Object {i}", type=bpy.types.Object)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    for i in range(1, 8):
        delattr(bpy.types.Scene, f"hepta_obj{i}")

if __name__ == "__main__":
    register()
