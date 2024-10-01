import bpy

# Function to process objects with UV maps
def process_uv_maps(obj):
    # Check if the object has UV maps (typically meshes and curves with certain modifiers)
    if hasattr(obj.data, 'uv_layers'):
        uv_layers = obj.data.uv_layers
        
        # If there are UV maps, proceed
        if uv_layers:
            # Rename the active UV map to "LightMapUV"
            uv_layers.active.name = "LightMapUV"
            
            # Store the name of the active UV map
            active_uv_name = uv_layers.active.name
            
            # Create a list of UV maps to delete (those not in use)
            uvs_to_delete = [uv for uv in uv_layers if uv.name != active_uv_name]
            
            # Delete all non-active UV maps
            for uv in uvs_to_delete:
                uv_layers.remove(uv)
                
            print(f"Processed {obj.name}: Renamed active UV map to 'LightMapUV' and deleted {len(uvs_to_delete)} UV map(s).")
        else:
            print(f"{obj.name} has no UV maps.")
    else:
        print(f"{obj.name} does not have UV layers.")

# Loop through all objects in the scene
for obj in bpy.context.scene.objects:
    # Call the function to process UV maps for each object
    process_uv_maps(obj)
            
print("UV map renaming and cleanup completed.")

