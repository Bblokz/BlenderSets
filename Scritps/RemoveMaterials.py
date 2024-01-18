import bpy
from bpy.types import WorkSpaceTool


def unregister_tool(idname, space_type, context_mode):
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    tools = cls._tools[context_mode]
            
    for i, tool_group in enumerate(tools):        
        if isinstance(tool_group, tuple):
            for t in tool_group:
                if 'ToolDef' in str(type(t)) and t.idname == idname:
                    if len(tools[i]) == 1:
                        # it's a group with a single item, just remove it from the tools list.
                        tools.pop(i)
                    else:
                        tools[i] = tuple(x for x in tool_group if x.idname != idname)
                    break
        elif tool_group is not None:
            if tool_group.idname == idname:
                tools.pop(i)
                break
    
    # cleanup any doubled up separators left over after removing a tool
    for i, p in enumerate(reversed(tools)):
        if i < len(tools)-2 and tools[i] is None and tools[i+1] is None:
            tools.pop(i)

class RemoveMaterialSlotsOperator(bpy.types.Operator):
    """Operator to remove all material slots from all meshes in the scene"""
    bl_idname = "object.remove_material_slots"
    bl_label = "Remove All Material Slots"

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for _ in range(len(obj.material_slots)):
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.material_slot_remove()
        self.report({'INFO'}, "All material slots removed from meshes")
        return {'FINISHED'}

class RemoveMaterialSlotsTool(WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "my_template.remove_material_slots"
    bl_label = "Remove Material Slots"
    bl_description = "Remove all material slots from all meshes in the scene"
    bl_icon = "ops.generic.delete"
    bl_widget = None
    bl_keymap = (
        ("object.remove_material_slots", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
    )

    def draw_settings(context, layout, tool):
        layout.label(text="Click to remove all materials from meshes")
        
        
def register():
    bpy.utils.register_class(RemoveMaterialSlotsOperator)
    bpy.utils.register_tool(RemoveMaterialSlotsTool, after={"builtin.scale_cage"}, separator=True, group=True)

def unregister():
    unregister_tool(RemoveMaterialSlotsTool.bl_idname, 'VIEW_3D', 'OBJECT')
    bpy.utils.unregister_class(RemoveMaterialSlotsOperator)
    bpy.utils.unregister_tool(RemoveMaterialSlotsTool)

if __name__ == "__main__":
    register()