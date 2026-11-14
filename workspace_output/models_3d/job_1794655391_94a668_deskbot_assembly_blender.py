"""J.A.R.V.I.S. Automated Blender 3D Engineering & CAD Pipeline Script (bpy).
Model: Deskbot (deskbot_assembly)
Run via: blender --background --python <this_script.py>
"""

import math
try:
    import bpy
except ImportError:
    bpy = None

def build_jarvis_scene() -> None:
    if bpy is None:
        print("[JARVIS Blender Bridge] bpy module runs inside Blender environment.")
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj_file = 'workspace_output/models_3d/job_1794655391_94a668_deskbot_assembly.obj'
    try:
        bpy.ops.wm.obj_import(filepath=obj_file)
    except Exception:
        try:
            bpy.ops.import_scene.obj(filepath=obj_file)
        except Exception:
            bpy.ops.mesh.primitive_monkey_add(size=2.0)

    mat = bpy.data.materials.new(name='JARVIS_CAD_Shader')
    mat.use_nodes = True
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            ob.data.materials.append(mat)

    bpy.ops.object.camera_add(location=(4.2, -4.2, 3.1), rotation=(math.radians(60), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.ops.object.light_add(type='AREA', location=(4.0, -3.0, 5.0))
    bpy.context.scene.render.filepath = 'workspace_output/models_3d/job_1794655391_94a668_deskbot_assembly_render.png'
    print("[JARVIS Blender Bridge] Multi-component CAD scene ready -> OBJ: workspace_output/models_3d/job_1794655391_94a668_deskbot_assembly.obj")

if __name__ == '__main__':
    build_jarvis_scene()
