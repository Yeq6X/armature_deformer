import bpy

from .armature_collider_processor import apply_lattice

class ProcessingSetting(bpy.types.PropertyGroup):
    branch_bone_name: bpy.props.StringProperty(name="Branch Bone Name", default="")
    lattice_names: bpy.props.StringProperty(name="Lattice Names", default="")

class OBJECT_PT_armature_collider_processor_panel(bpy.types.Panel):
    """Panel for processing Armature and Colliders"""
    bl_label = "Armature and Collider Processor"
    bl_idname = "OBJECT_PT_armature_collider_processor_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Armature Collider'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Armatureの選択フォーム
        layout.prop(scene, "target_armature", text="Select Armature")

        # Colliderのコレクション選択フォーム
        layout.prop(scene, "collider_collection", text="Collider Collection")

        # シェイプキーの重み設定
        layout.prop(scene, "shape_key_weight", text="Shape Key Weight")

        # Body, Head, Faceの設定
        box = layout.box()
        box.label(text="Processing Settings")
        for setting in scene.processing_settings:
            box.prop(setting, "branch_bone_name", text="Branch Bone Name")
            box.prop(setting, "lattice_names", text="Lattice Name")

        # 設定の追加と削除
        row = box.row(align=True)
        row.operator("object.add_processing_setting", icon='ADD', text="Add Setting")
        row.operator("object.remove_processing_setting", icon='REMOVE', text="Remove Setting")

        # 実行ボタン
        layout.operator("object.execute_armature_collider_processing", text="Execute Processing")

class OBJECT_OT_add_processing_setting(bpy.types.Operator):
    """Add a new processing setting"""
    bl_idname = "object.add_processing_setting"
    bl_label = "Add Processing Setting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        new_setting = context.scene.processing_settings.add()
        new_setting.name = "New Part"
        return {'FINISHED'}

class OBJECT_OT_remove_processing_setting(bpy.types.Operator):
    """Remove the selected processing setting"""
    bl_idname = "object.remove_processing_setting"
    bl_label = "Remove Processing Setting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.processing_settings
        if settings:
            settings.remove(len(settings) - 1)
        return {'FINISHED'}

class OBJECT_OT_execute_armature_collider_processing(bpy.types.Operator):
    """Execute the processing of Armature and Colliders"""
    bl_idname = "object.execute_armature_collider_processing"
    bl_label = "Execute Armature and Collider Processing"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        armature = scene.target_armature
        collider_collection = scene.collider_collection
        shape_key_weight = scene.shape_key_weight
        processing_settings = scene.processing_settings

        apply_lattice(armature, collider_collection, shape_key_weight, processing_settings)

        self.report({'INFO'}, "Processing completed.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ProcessingSetting)
    bpy.utils.register_class(OBJECT_PT_armature_collider_processor_panel)
    bpy.utils.register_class(OBJECT_OT_execute_armature_collider_processing)
    bpy.utils.register_class(OBJECT_OT_add_processing_setting)
    bpy.utils.register_class(OBJECT_OT_remove_processing_setting)

    bpy.types.Scene.target_armature = bpy.props.PointerProperty(type=bpy.types.Object, name="Target Armature")
    bpy.types.Scene.collider_collection = bpy.props.PointerProperty(type=bpy.types.Collection, name="Collider Collection")
    bpy.types.Scene.shape_key_weight = bpy.props.FloatProperty(name="Shape Key Weight", default=0.0, min=0.0, max=1.0)
    bpy.types.Scene.processing_settings = bpy.props.CollectionProperty(type=ProcessingSetting)

def unregister():
    bpy.utils.unregister_class(ProcessingSetting)
    bpy.utils.unregister_class(OBJECT_PT_armature_collider_processor_panel)
    bpy.utils.unregister_class(OBJECT_OT_execute_armature_collider_processing)
    bpy.utils.unregister_class(OBJECT_OT_add_processing_setting)
    bpy.utils.unregister_class(OBJECT_OT_remove_processing_setting)

    del bpy.types.Scene.target_armature
    del bpy.types.Scene.collider_collection
    del bpy.types.Scene.shape_key_weight
    del bpy.types.Scene.processing_settings
