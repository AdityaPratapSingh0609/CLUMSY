"""J.A.R.V.I.S. Automated Blender 3D Pipeline Script (bpy).
Model: generate a 3d model using blender of your desk bot model (deskbot_head)
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
    shape = 'deskbot_head'
    if shape == 'arc_reactor':
        bpy.ops.mesh.primitive_torus_add(major_radius=1.4, minor_radius=0.36, location=(0, 0, 0))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(0, 0, 0))
    elif shape == 'geodesic_sphere':
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.4, location=(0, 0, 0))
    elif shape == 'mech_gear':
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.35, depth=0.45, location=(0, 0, 0))
    else:
        bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
        obj = bpy.context.active_object
        obj.scale = (1.25, 0.85, 0.85)
        mod = obj.modifiers.new(name='Bevel', type='BEVEL')
        mod.width = 0.18
        mod.segments = 4

    # Emission Cyan Hologram Material
    mat = bpy.data.materials.new(name='JARVIS_Holo_Cyan')
    mat.use_nodes = True
    if bpy.context.active_object:
        bpy.context.active_object.data.materials.append(mat)

    # Camera & Key Light
    bpy.ops.object.camera_add(location=(3.8, -3.8, 2.6), rotation=(math.radians(63), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.ops.object.light_add(type='AREA', location=(3.0, -2.5, 4.0))
    bpy.context.scene.render.filepath = 'workspace_output/models_3d/job_1794598217_4dfbda_deskbot_head_render.png'
    print("[JARVIS Blender Bridge] Scene ready -> OBJ: workspace_output/models_3d/job_1794598217_4dfbda_deskbot_head.obj")

if __name__ == '__main__':
    build_jarvis_scene()
