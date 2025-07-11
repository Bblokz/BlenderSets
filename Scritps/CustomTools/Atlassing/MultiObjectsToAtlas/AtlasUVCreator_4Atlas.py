bl_info = {
    "name": "AtlasUV-er",
    "blender": (2, 80, 0),
    "category": "Object",
    "description": "Arrange the UV islands of four objects into a 2×2 atlas",
}

import bpy
from mathutils import Vector

# Operator: scales and offsets UVs of four selected objects into atlas quadrants
class OBJECT_OT_atlas_uv_operator(bpy.types.Operator):
    bl_idname = "object.atlas_uv_operator"
    bl_label = "Atlas UVs"
    bl_description = "Pack UVs of four objects into the four quadrants of a single atlas"
    
    @classmethod
    def poll(cls, context):
        sc = context.scene
        # All four slots must be set
        return all(getattr(sc, f"atlas_uv_obj{i}") for i in range(1, 5))
    
    def execute(self, context):
        sc = context.scene
        # Gather objects in the order they'll map to: top-left, top-right, bottom-left, bottom-right
        objs = [sc.atlas_uv_obj1, sc.atlas_uv_obj2, sc.atlas_uv_obj3, sc.atlas_uv_obj4]
        
        # Validation: ensure they are distinct, are meshes, have one material, and have UVs
        if len(set(objs)) != 4:
            self.report({'ERROR'}, "Please select four different objects")
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
        
        # Define UV offsets for each quadrant
        offsets = [
            Vector((0.0, 0.5)),   # top-left
            Vector((0.5, 0.5)),   # top-right
            Vector((0.0, 0.0)),   # bottom-left
            Vector((0.5, 0.0)),   # bottom-right
        ]
        
        # For each object, shrink UVs by 0.5 and translate into its quadrant
        for obj, offset in zip(objs, offsets):
            mesh = obj.data
            uv_layer = mesh.uv_layers.active.data
            for uv_elem in uv_layer:
                uv = uv_elem.uv
                uv *= 0.5       # scale down to fit one quadrant
                uv += offset    # move into the correct corner
        
        self.report({'INFO'}, "UV atlas applied to all four objects")
        return {'FINISHED'}


# Panel in the 3D View’s N-menu under the "AtlasUV-er" tab
class VIEW3D_PT_atlas_uv_panel(bpy.types.Panel):
    bl_label = "AtlasUV-er"
    bl_idname = "VIEW3D_PT_atlas_uv_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AtlasUV-er'

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        
        layout.label(text="Select four objects:")
        layout.prop(sc, "atlas_uv_obj1", text="Object 1 (TL)")
        layout.prop(sc, "atlas_uv_obj2", text="Object 2 (TR)")
        layout.prop(sc, "atlas_uv_obj3", text="Object 3 (BL)")
        layout.prop(sc, "atlas_uv_obj4", text="Object 4 (BR)")
        
        layout.separator()
        layout.operator("object.atlas_uv_operator", text="Pack into Atlas")


# Registration
classes = (
    OBJECT_OT_atlas_uv_operator,
    VIEW3D_PT_atlas_uv_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # Four pointers for the user to assign objects
    bpy.types.Scene.atlas_uv_obj1 = bpy.props.PointerProperty(
        name="Object 1", type=bpy.types.Object)
    bpy.types.Scene.atlas_uv_obj2 = bpy.props.PointerProperty(
        name="Object 2", type=bpy.types.Object)
    bpy.types.Scene.atlas_uv_obj3 = bpy.props.PointerProperty(
        name="Object 3", type=bpy.types.Object)
    bpy.types.Scene.atlas_uv_obj4 = bpy.props.PointerProperty(
        name="Object 4", type=bpy.types.Object)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.atlas_uv_obj1
    del bpy.types.Scene.atlas_uv_obj2
    del bpy.types.Scene.atlas_uv_obj3
    del bpy.types.Scene.atlas_uv_obj4

if __name__ == "__main__":
    register()
