bl_info = {
    "name": "Object UV Remaster",
    "author": "ChatGPT",
    "version": (3, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > UV Remaster",
    "description": "Remap UVs of selected material slots into a texture atlas layout and consolidate materials into an atlas material",
    "category": "UV",
}

import bpy
from mathutils import Vector


class UVRemasterProperties(bpy.types.PropertyGroup):
    def update_atlas(self, context):
        size = self.atlas_size
        if size == 'FOUR':
            self.slot1_pos = 'TL'
            self.slot2_pos = 'TR'
            self.slot3_pos = 'BL'
            self.slot4_pos = 'BR'
        elif size == 'SEVEN':
            self.slot1_pos = 'TL'
            self.slot2_pos = 'TR'
            self.slot3_pos = 'BR'
            self.slot4_pos = 'BR_TL'
            self.slot5_pos = 'BR_TR'
            self.slot6_pos = 'BR_BL'
            self.slot7_pos = 'BR_BR'
        elif size == 'TEN':
            self.slot1_pos = 'TL'
            self.slot2_pos = 'TR'
            self.slot3_pos = 'BL_TL'
            self.slot4_pos = 'BL_TR'
            self.slot5_pos = 'BL_BL'
            self.slot6_pos = 'BL_BR'
            self.slot7_pos = 'BR_TL'
            self.slot8_pos = 'BR_TR'
            self.slot9_pos = 'BR_BL'
            self.slot10_pos = 'BR_BR'
        else:  # SIXTEEN
            for i in range(1, 17):
                row = (i - 1) // 4
                col = (i - 1) % 4
                setattr(self, f"slot{i}_pos", f"R{row+1}C{col+1}")

    atlas_size: bpy.props.EnumProperty(
        name="Atlas Size",
        items=[
            ('FOUR','4 Slots','2x2 atlas'),
            ('SEVEN','7 Slots','3+4 atlas'),
            ('TEN','10 Slots','2+8 atlas'),
            ('SIXTEEN','16 Slots','4x4 atlas'),
        ],
        default='FOUR',
        update=update_atlas
    )

    def mat_slot_items(self, context):
        items = [('NONE','None','No remapping')]
        obj = context.object
        if obj and obj.type == 'MESH':
            for i, slot in enumerate(obj.material_slots):
                items.append((str(i), slot.name or f"Slot {i}", ""))
        return items

    def pos_slot_items(self, context):
        size = self.atlas_size
        if size == 'FOUR':
            return [('TL','Top Left',''),('TR','Top Right',''),('BL','Bottom Left',''),('BR','Bottom Right','')]
        if size == 'SEVEN':
            return [
                ('TL','Top Left',''),('TR','Top Right',''),('BR','Bottom Right',''),
                ('BR_TL','BR: Top Left',''),('BR_TR','BR: Top Right',''),('BR_BL','BR: Bottom Left',''),('BR_BR','BR: Bottom Right','')
            ]
        if size == 'TEN':
            return [
                ('TL','Top Left',''),('TR','Top Right',''),
                ('BL_TL','BL: Top Left',''),('BL_TR','BL: Top Right',''),('BL_BL','BL: Bottom Left',''),('BL_BR','BL: Bottom Right',''),
                ('BR_TL','BR: Top Left',''),('BR_TR','BR: Top Right',''),('BR_BL','BR: Bottom Left',''),('BR_BR','BR: Bottom Right','')
            ]
        # SIXTEEN: generate 4x4 grid
        slots = []
        for r in range(1, 5):
            for c in range(1, 5):
                key = f"R{r}C{c}"
                slots.append((key, key, ""))
        return slots

    # explicit EnumProperty declarations for slots using mat_slot_items
    slot1_mat: bpy.props.EnumProperty(name="Slot 1 Mat", items=mat_slot_items)
    slot1_pos: bpy.props.EnumProperty(name="Slot 1 Pos", items=pos_slot_items)
    slot2_mat: bpy.props.EnumProperty(name="Slot 2 Mat", items=mat_slot_items)
    slot2_pos: bpy.props.EnumProperty(name="Slot 2 Pos", items=pos_slot_items)
    slot3_mat: bpy.props.EnumProperty(name="Slot 3 Mat", items=mat_slot_items)
    slot3_pos: bpy.props.EnumProperty(name="Slot 3 Pos", items=pos_slot_items)
    slot4_mat: bpy.props.EnumProperty(name="Slot 4 Mat", items=mat_slot_items)
    slot4_pos: bpy.props.EnumProperty(name="Slot 4 Pos", items=pos_slot_items)
    slot5_mat: bpy.props.EnumProperty(name="Slot 5 Mat", items=mat_slot_items)
    slot5_pos: bpy.props.EnumProperty(name="Slot 5 Pos", items=pos_slot_items)
    slot6_mat: bpy.props.EnumProperty(name="Slot 6 Mat", items=mat_slot_items)
    slot6_pos: bpy.props.EnumProperty(name="Slot 6 Pos", items=pos_slot_items)
    slot7_mat: bpy.props.EnumProperty(name="Slot 7 Mat", items=mat_slot_items)
    slot7_pos: bpy.props.EnumProperty(name="Slot 7 Pos", items=pos_slot_items)
    slot8_mat: bpy.props.EnumProperty(name="Slot 8 Mat", items=mat_slot_items)
    slot8_pos: bpy.props.EnumProperty(name="Slot 8 Pos", items=pos_slot_items)
    slot9_mat: bpy.props.EnumProperty(name="Slot 9 Mat", items=mat_slot_items)
    slot9_pos: bpy.props.EnumProperty(name="Slot 9 Pos", items=pos_slot_items)
    slot10_mat: bpy.props.EnumProperty(name="Slot 10 Mat", items=mat_slot_items)
    slot10_pos: bpy.props.EnumProperty(name="Slot 10 Pos", items=pos_slot_items)
    slot11_mat: bpy.props.EnumProperty(name="Slot 11 Mat", items=mat_slot_items)
    slot11_pos: bpy.props.EnumProperty(name="Slot 11 Pos", items=pos_slot_items)
    slot12_mat: bpy.props.EnumProperty(name="Slot 12 Mat", items=mat_slot_items)
    slot12_pos: bpy.props.EnumProperty(name="Slot 12 Pos", items=pos_slot_items)
    slot13_mat: bpy.props.EnumProperty(name="Slot 13 Mat", items=mat_slot_items)
    slot13_pos: bpy.props.EnumProperty(name="Slot 13 Pos", items=pos_slot_items)
    slot14_mat: bpy.props.EnumProperty(name="Slot 14 Mat", items=mat_slot_items)
    slot14_pos: bpy.props.EnumProperty(name="Slot 14 Pos", items=pos_slot_items)
    slot15_mat: bpy.props.EnumProperty(name="Slot 15 Mat", items=mat_slot_items)
    slot15_pos: bpy.props.EnumProperty(name="Slot 15 Pos", items=pos_slot_items)
    slot16_mat: bpy.props.EnumProperty(name="Slot 16 Mat", items=mat_slot_items)
    slot16_pos: bpy.props.EnumProperty(name="Slot 16 Pos", items=pos_slot_items)

    # Atlas material selector: all materials in project
    def atlas_material_items(self, context):
        items = [('NONE','None','No atlas')]
        for mat in bpy.data.materials:
            items.append((mat.name, mat.name, ""))
        return items

    atlas_material: bpy.props.EnumProperty(name="Atlas Material", items=atlas_material_items)


class OBJECT_PT_uv_remaster(bpy.types.Panel):
    bl_label = "Object UV Remaster"
    bl_idname = "OBJECT_PT_uv_remaster"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "UV Remaster"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        p = context.object.uv_remaster_props
        layout = self.layout
        layout.prop(p, 'atlas_size')

        counts = {'FOUR':4, 'SEVEN':7, 'TEN':10, 'SIXTEEN':16}
        n = counts[p.atlas_size]
        for i in range(1, n+1):
            row = layout.row(align=True)
            row.prop(p, f"slot{i}_mat", text=f"Slot {i}")
            row.prop(p, f"slot{i}_pos", text="")

        layout.prop(p, 'atlas_material')
        layout.separator()
        layout.operator('object.uv_remap', text='Remap UVs')
        row = layout.row(align=True)
        row.operator('object.uv_clear_materials', text='Clear Materials')
        row.operator('object.uv_clear_uv', text='Clear UV Transform')


class OBJECT_OT_uv_remap(bpy.types.Operator):
    bl_idname = 'object.uv_remap'
    bl_label = 'Remap UVs'
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # ensure object mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        obj = context.object
        mesh = obj.data
        uv_layer = mesh.uv_layers.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV layer")
            return {'CANCELLED'}
        uvdata = uv_layer.data
        if not uvdata:
            self.report({'ERROR'}, "UV data empty")
            return {'CANCELLED'}

        p = obj.uv_remaster_props
        counts = {'FOUR':4, 'SEVEN':7, 'TEN':10, 'SIXTEEN':16}
        mapping = {
            'TL':((0,0.5),.5), 'TR':((.5,0.5),.5), 'BL':((0,0),.5), 'BR':((.5,0),.5),
            'BR_TL':((.5,0.25),.25), 'BR_TR':((.75,0.25),.25), 'BR_BL':((.5,0),.25), 'BR_BR':((.75,0),.25),
            'BL_TL':((0,0.25),.25), 'BL_TR':((.25,0.25),.25), 'BL_BL':((0,0),.25), 'BL_BR':((.25,0),.25),
        }
        for r, y in enumerate((0.75,0.5,0.25,0.0), start=1):
            for c, x in enumerate((0,0.25,0.5,0.75), start=1):
                mapping[f"R{r}C{c}"] = ((x,y), .25)

        # handle atlas material
        atlas_idx = None
        if p.atlas_material != 'NONE':
            mat = bpy.data.materials.get(p.atlas_material)
            # add to object if missing
            slot_names = [slot.name for slot in obj.data.materials]
            if mat.name in slot_names:
                atlas_idx = slot_names.index(mat.name)
            else:
                obj.data.materials.append(mat)
                atlas_idx = len(obj.material_slots) - 1

        used_idxs = set()
        for i in range(1, counts[p.atlas_size] + 1):
            mat_id = getattr(p, f"slot{i}_mat")
            pos_key = getattr(p, f"slot{i}_pos")
            if mat_id == 'NONE':
                continue
            idx = int(mat_id)
            used_idxs.add(idx)
            off, sc = mapping.get(pos_key, ((0,0),1))
            for poly in mesh.polygons:
                if poly.material_index == idx:
                    if atlas_idx is not None:
                        poly.material_index = atlas_idx
                    for li in poly.loop_indices:
                        uv = uvdata[li].uv
                        uvdata[li].uv = Vector((uv.x * sc + off[0], uv.y * sc + off[1]))

        mesh.update()
        if atlas_idx is not None:
            for idx in sorted(used_idxs, reverse=True):
                if idx == atlas_idx:
                    continue
                obj.active_material_index = idx
                bpy.ops.object.material_slot_remove()

        self.report({'INFO'}, "UV remapping and consolidation complete")
        return {'FINISHED'}


class OBJECT_OT_uv_clear_materials(bpy.types.Operator):
    bl_idname = 'object.uv_clear_materials'
    bl_label = 'Clear Materials'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        p = context.object.uv_remaster_props
        for i in range(1, 17):
            setattr(p, f"slot{i}_mat", 'NONE')
        self.report({'INFO'}, "Cleared materials")
        return {'FINISHED'}


class OBJECT_OT_uv_clear_uv(bpy.types.Operator):
    bl_idname = 'object.uv_clear_uv'
    bl_label = 'Clear UV Transform'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        p = context.object.uv_remaster_props
        size = p.atlas_size
        counts = {'FOUR':4, 'SEVEN':7, 'TEN':10, 'SIXTEEN':16}
        defaults = {}
        if size == 'FOUR':
            defaults = {1:'TL', 2:'TR', 3:'BL', 4:'BR'}
        elif size == 'SEVEN':
            defaults = {1:'TL', 2:'TR', 3:'BR', 4:'BR_TL', 5:'BR_TR', 6:'BR_BL', 7:'BR_BR'}
        elif size == 'TEN':
            defaults = {1:'TL', 2:'TR', 3:'BL_TL', 4:'BL_TR', 5:'BL_BL', 6:'BL_BR', 7:'BR_TL', 8:'BR_TR', 9:'BR_BL', 10:'BR_BR'}
        else:
            for i in range(1, 17):
                row = (i - 1) // 4
                col = (i - 1) % 4
                defaults[i] = f"R{row+1}C{col+1}"
        for i, pos in defaults.items():
            setattr(p, f"slot{i}_pos", pos)
        self.report({'INFO'}, "Reset UV positions to defaults")
        return {'FINISHED'}


# Registration
classes = (
    UVRemasterProperties,
    OBJECT_PT_uv_remaster,
    OBJECT_OT_uv_remap,
    OBJECT_OT_uv_clear_materials,
    OBJECT_OT_uv_clear_uv,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.uv_remaster_props = bpy.props.PointerProperty(type=UVRemasterProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.uv_remaster_props


if __name__ == '__main__':
    register()