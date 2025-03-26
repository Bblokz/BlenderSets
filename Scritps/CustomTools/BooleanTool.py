bl_info = {
    "name": "Boolean Tool Addon",
    "blender": (2, 80, 0),
    "category": "Object",
    "description": "Register a reference object and use it to apply a boolean difference on another object",
}

import bpy

# Operator to add and apply the boolean modifier
class OBJECT_OT_boolean_apply_operator(bpy.types.Operator):
    bl_idname = "object.boolean_apply_operator"
    bl_label = "Apply Boolean Difference"
    bl_description = "Apply a boolean difference using the registered reference object"
    
    @classmethod
    def poll(cls, context):
        # Ensure an active object exists and a reference object is set in the scene.
        return context.active_object is not None and context.scene.boolean_tool_ref is not None

    def execute(self, context):
        obj = context.active_object
        ref = context.scene.boolean_tool_ref

        if obj == ref:
            self.report({'ERROR'}, "Active object and reference object cannot be the same")
            return {'CANCELLED'}
        
        # Add a boolean modifier to the active object.
        mod = obj.modifiers.new(name="Boolean_Difference", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = ref
        
        # Ensure we are in Object mode before applying the modifier.
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply modifier: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, "Boolean applied successfully")
        return {'FINISHED'}

# Panel in the 3D View’s N-panel
class VIEW3D_PT_boolean_tool_panel(bpy.types.Panel):
    bl_label = "Boolean Tool"
    bl_idname = "VIEW3D_PT_boolean_tool_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Boolean Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # UI for selecting the reference object.
        layout.label(text="Register Reference Object:")
        layout.prop(scene, "boolean_tool_ref", text="")

        layout.separator()

        # Button to apply the boolean modifier.
        layout.label(text="Boolean Operation:")
        layout.operator("object.boolean_apply_operator", text="Apply Boolean Difference")

# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_boolean_apply_operator)
    bpy.utils.register_class(VIEW3D_PT_boolean_tool_panel)
    bpy.types.Scene.boolean_tool_ref = bpy.props.PointerProperty(type=bpy.types.Object)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_boolean_apply_operator)
    bpy.utils.unregister_class(VIEW3D_PT_boolean_tool_panel)
    del bpy.types.Scene.boolean_tool_ref

if __name__ == "__main__":
    register()
