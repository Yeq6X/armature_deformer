bl_info = {
    "name": "Armature Deformer",
    "blender": (2, 80, 0),
    "category": "Object",
    "description": "Lattice deformer for armature and collider",
    "author": "toyofuku",
    "version": (1, 0, 0)
}

if "bpy" in locals():
    import importlib
    if "armature_collider_processor" in locals():
        importlib.reload(armature_lattice_processor)
    if "armature_deformer_ui" in locals():
        importlib.reload(armature_deformer_ui)

import bpy
from .armature_deformer_ui import register, unregister

def register():
    from .armature_deformer_ui import register as init_register
    init_register()

def unregister():
    from .armature_deformer_ui import unregister as init_unregister
    init_unregister()

if __name__ == "__main__":
    register()