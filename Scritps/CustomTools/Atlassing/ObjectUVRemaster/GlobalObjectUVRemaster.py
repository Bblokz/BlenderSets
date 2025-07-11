bl_info = {
    "name": "Global Object UV Remaster",
    "author": "ChatGPT",
    "version": (1, 2),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > UV Remaster",
    "description": "Globally map materials to atlas slots and remap UVs across objects without resetting selections",
    "category": "UV",
}

import bpy
from mathutils import Vector

class GlobalUVRemasterProperties(bpy.types.PropertyGroup):
    """Store global remapping settings in WindowManager"""

    def update_atlas(self, context):
        # Set default positions on atlas size change
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
            ('FOUR', '4 Slots', '2x2 atlas'),
            ('SEVEN', '7 Slots', '3+4 atlas'),
            ('TEN', '10 Slots', '2+8 atlas'),
            ('SIXTEEN', '16 Slots', '4x4 atlas'),
        ],
        default='FOUR',
        update=update_atlas
    )

    def mat_slot_items(self, context):
        # Global list of all materials in the project
        items = [('NONE', 'None', 'No remapping')]
        for mat in bpy.data.materials:
            items.append((mat.name, mat.name, ''))
        return items

    def pos_slot_items(self, context):
        size = self.atlas_size
        if size == 'FOUR':
            return [('TL','Top Left',''),('TR','Top Right',''),('BL','Bottom Left',''),('BR','Bottom Right','')]
        if size == 'SEVEN':
            return [('TL','Top Left',''),('TR','Top Right',''),('BR','Bottom Right',''),
                    ('BR_TL','BR: Top Left',''),('BR_TR','BR: Top Right',''),
                    ('BR_BL','BR: Bottom Left',''),('BR_BR','BR: Bottom Right','')]
        if size == 'TEN':
            return [('TL','Top Left',''),('TR','Top Right',''),
                    ('BL_TL','BL: Top Left',''),('BL_TR','BL: Top Right',''),
                    ('BL_BL','BL: Bottom Left',''),('BL_BR','BL: Bottom Right',''),
                    ('BR_TL','BR: Top Left',''),('BR_TR','BR: Top Right',''),
                    ('BR_BL','BR: Bottom Left',''),('BR_BR','BR: Bottom Right','')]
        slots = []
        for r in range(1,5):
            for c in range(1,5):
                key = f"R{r}C{c}"
                slots.append((key,key,''))
        return slots

    # Define global mapping slots (material name -> atlas position)
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

    # Atlas material (global)
    def atlas_material_items(self, context):
        items = [('NONE','None','No atlas')]
        for mat in bpy.data.materials:
            items.append((mat.name,mat.name,''))
        return items
    atlas_material: bpy.props.EnumProperty(name="Atlas Material", items=atlas_material_items)


class OBJECT_PT_uv_remaster(bpy.types.Panel):
    bl_label = "Global UV Remaster"
    bl_idname = "OBJECT_PT_uv_remaster"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "UV Remaster"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        wm = context.window_manager.global_uv_props
        layout = self.layout
        layout.prop(wm, 'atlas_size')

        counts = {'FOUR':4,'SEVEN':7,'TEN':10,'SIXTEEN':16}
        slot_count = counts[wm.atlas_size]
        for i in range(1, slot_count+1):
            row = layout.row(align=True)
            row.prop(wm, f"slot{i}_mat", text=f"Mat {i}")
            row.prop(wm, f"slot{i}_pos", text=f"Pos {i}")

        layout.prop(wm, 'atlas_material')
        layout.separator()
        layout.operator('global_uv_remap.execute', text='Remap UVs')
        row=layout.row(align=True)
        row.operator('global_uv_remap.clear_materials', text='Clear Mats')
        row.operator('global_uv_remap.clear_uv', text='Clear UVs')


class GLOBAL_OT_uv_remap(bpy.types.Operator):
    bl_idname = 'global_uv_remap.execute'
    bl_label = 'Global Remap UVs'
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        wm = context.window_manager.global_uv_props
        counts = {'FOUR':4,'SEVEN':7,'TEN':10,'SIXTEEN':16}

        # mapping positions
        mapping = {}
        # large slots
        mapping.update({
            'TL':((0,0.5),.5),'TR':((.5,0.5),.5),
            'BL':((0,0),.5),'BR':((.5,0),.5)
        })
        # small slots
        mapping.update({
            'BR_TL':((.5,0.25),.25),'BR_TR':((.75,0.25),.25),
            'BR_BL':((.5,0),.25),'BR_BR':((.75,0),.25),
            'BL_TL':((0,0.25),.25),'BL_TR':((.25,0.25),.25),
            'BL_BL':((0,0),.25),'BL_BR':((.25,0),.25)
        })
        # 16-grid
        for r, y in enumerate((0.75,0.5,0.25,0.0),1):
            for c, x in enumerate((0,0.25,0.5,0.75),1):
                mapping[f"R{r}C{c}"] = ((x,y),.25)

        # process each selected mesh
        for obj in context.selected_objects:
            if obj.type!='MESH': continue
            bpy.context.view_layer.objects.active=obj
            mesh=obj.data

            # atlas material slot
            atlas_idx=None
            if wm.atlas_material!='NONE':
                mat=bpy.data.materials.get(wm.atlas_material)
                if mat:
                    slot_names=[s.material.name for s in obj.material_slots]
                    if mat.name not in slot_names:
                        obj.data.materials.append(mat)
                        slot_names.append(mat.name)
                    atlas_idx=slot_names.index(mat.name)

            uv_layer=mesh.uv_layers.active
            if not uv_layer: continue
            uvdata=uv_layer.data

            used=set()
            scount=counts[wm.atlas_size]
            for i in range(1,scount+1):
                mat_name=getattr(wm,f"slot{i}_mat")
                pos_key=getattr(wm,f"slot{i}_pos")
                if mat_name=='NONE': continue
                # only remap if object has this material
                if mat_name not in [s.material.name for s in obj.material_slots]: continue
                src_idx=[idx for idx,s in enumerate(obj.material_slots) if s.material.name==mat_name][0]
                used.add(src_idx)
                off,sc=mapping.get(pos_key,((0,0),1))
                for poly in mesh.polygons:
                    if poly.material_index==src_idx:
                        if atlas_idx is not None:
                            poly.material_index=atlas_idx
                        for li in poly.loop_indices:
                            v=uvdata[li].uv
                            uvdata[li].uv=Vector((v.x*sc+off[0],v.y*sc+off[1]))
            mesh.update()

            if atlas_idx is not None:
                for idx in sorted(used,reverse=True):
                    if idx==atlas_idx: continue
                    obj.active_material_index=idx
                    bpy.ops.object.material_slot_remove()

        self.report({'INFO'},"Global UV remap complete")
        return{'FINISHED'}

class GLOBAL_OT_uv_clear_materials(bpy.types.Operator):
    bl_idname='global_uv_remap.clear_materials'
    bl_label='Clear Materials'
    bl_options={'INTERNAL'}
    def execute(self,context):
        wm=context.window_manager.global_uv_props
        for i in range(1,17): setattr(wm,f"slot{i}_mat",'NONE')
        self.report({'INFO'},"Cleared materials")
        return{'FINISHED'}

class GLOBAL_OT_uv_clear_uv(bpy.types.Operator):
    bl_idname='global_uv_remap.clear_uv'
    bl_label='Clear UV Transform'
    bl_options={'INTERNAL'}
    def execute(self,context):
        wm=context.window_manager.global_uv_props
        size=wm.atlas_size; counts={'FOUR':4,'SEVEN':7,'TEN':10,'SIXTEEN':16}
        defaults={}
        if size=='FOUR': defaults={1:'TL',2:'TR',3:'BL',4:'BR'}
        elif size=='SEVEN': defaults={1:'TL',2:'TR',3:'BR',4:'BR_TL',5:'BR_TR',6:'BR_BL',7:'BR_BR'}
        elif size=='TEN': defaults={1:'TL',2:'TR',3:'BL_TL',4:'BL_TR',5:'BL_BL',6:'BL_BR',7:'BR_TL',8:'BR_TR',9:'BR_BL',10:'BR_BR'}
        else:
            for i in range(1,17): row=(i-1)//4; col=(i-1)%4; defaults[i]=f"R{row+1}C{col+1}"
        for i,pos in defaults.items(): setattr(wm,f"slot{i}_pos",pos)
        self.report({'INFO'},"Reset UV positions to defaults")
        return{'FINISHED'}

# Registration
classes=(GlobalUVRemasterProperties,OBJECT_PT_uv_remaster,GLOBAL_OT_uv_remap,GLOBAL_OT_uv_clear_materials,GLOBAL_OT_uv_clear_uv)
def register():
    for c in classes: bpy.utils.register_class(c)
    bpy.types.WindowManager.global_uv_props=bpy.props.PointerProperty(type=GlobalUVRemasterProperties)
def unregister():
    for c in reversed(classes): bpy.utils.unregister_class(c)
    del bpy.types.WindowManager.global_uv_props

if __name__=='__main__': register()
