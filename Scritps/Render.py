import bpy

# Create a new scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import your tank model from an FBX file
fbx_file_path = "D:/BlenderProjects/BlenderTanks/Heavy Tanks/TigerII/SM_TigerII.fbx"
bpy.ops.import_scene.fbx(filepath=fbx_file_path)

# Get the imported object (assuming it's the only one imported)
imported_objects = bpy.context.selected_objects
if imported_objects:
    tank = imported_objects[0]
else:
    raise Exception("No objects were imported. Please check the file path and contents.")

# Set up the camera
# Check if a camera already exists
if "Camera" in bpy.data.objects:
    camera = bpy.data.objects["Camera"]
else:
    # Create a new camera
    bpy.ops.object.camera_add(location=(0, -10, 0))
    camera = bpy.context.view_layer.objects.active
    camera.name = "Camera"

# Position and set the camera to orthographic
camera.location = (0, -10, 0)
camera.rotation_euler = (1.5708, 0, 0)  # Top down view
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 5

# Add wireframe modifier to the imported model
bpy.context.view_layer.objects.active = tank
bpy.ops.object.modifier_add(type='WIREFRAME')

# Set up material
material = bpy.data.materials.new(name="WireframeMaterial")
material.use_nodes = True
nodes = material.node_tree.nodes
nodes.clear()

emission = nodes.new(type='ShaderNodeEmission')
emission.inputs[0].default_value = (0, 0, 0, 1)  # Black color

output = nodes.new(type='ShaderNodeOutputMaterial')
material.node_tree.links.new(emission.outputs[0], output.inputs[0])

tank.data.materials.append(material)

# Enable Freestyle
bpy.context.scene.render.use_freestyle = True

# Freestyle line set
freestyle_settings = bpy.context.scene.view_layers["View Layer"].freestyle_settings
line_set = freestyle_settings.linesets.new(name="LineSet")
line_set.select_silhouette = True
line_set.select_border = True
line_set.select_crease = True
line_set.select_edge_mark = True

# Line style
line_style = line_set.linestyle
line_style.thickness = 1
line_style.color = (0, 0, 0)

# Render settings
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.filepath = "D:/Renders/render.png"

# Render the image
bpy.ops.render.render(write_still=True)
