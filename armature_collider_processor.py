
import bpy

def apply_lattice(armature, collider_collection, shape_key_weight, processing_settings):

    collider_map = generate_collider_meshes(collider_collection) if collider_collection else None
    process_bones_and_colliders_recursively(armature, processing_settings, shape_key_weight, collider_map)

def generate_bone_mesh(bone):
    mesh = bpy.data.meshes.new(bone.name)
    obj = bpy.data.objects.new(bone.name, mesh)
    mesh.from_pydata([bone.head_local, bone.tail_local], [], [(0, 1)])
    return obj

def generate_collider_meshes(collider_collection):
    collider_map = {}
    for obj in collider_collection.objects:
        if obj.type == 'EMPTY' and obj.empty_display_type == 'SPHERE':
            # 新しいUV Sphereメッシュを生成
            sphere_mesh = bpy.data.meshes.new(f"{obj.name}_ColliderSphere")
            sphere_obj = bpy.data.objects.new(f"{obj.name}_ColliderSphere", sphere_mesh)
            bpy.context.collection.objects.link(sphere_obj)

            # Colliderの位置とサイズをメッシュに反映
            bpy.context.view_layer.objects.active = sphere_obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.primitive_uv_sphere_add(radius=obj.empty_display_size, location=(0, 0, 0))
            bpy.ops.object.mode_set(mode='OBJECT')

            # Sphereの位置を元のColliderの位置と同じに設定
            sphere_obj.location = obj.matrix_world.to_translation()
            sphere_obj.scale = obj.scale

            # 親ボーンが存在する場合、collider_mapに追加
            if obj.parent and obj.parent.type == 'ARMATURE':
                if obj.parent_bone not in collider_map:
                    collider_map[obj.parent_bone] = []
                collider_map[obj.parent_bone].append(obj.name)

    return collider_map

def process_bones_and_colliders_recursively(armature, settings, shape_key_weight, collider_map=None):
    def apply_lattice(mesh_obj, lattice_obj):
        # Latticeモディファイアを追加
        mod = mesh_obj.modifiers.new(name="LatticeModifier", type='LATTICE')
        mod.object = lattice_obj

        # シェイプキーとして適用
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.modifier_apply_as_shapekey(modifier="LatticeModifier")

        # 生成されたシェイプキーの名前をLatticeの名前に設定
        mesh_obj.data.shape_keys.key_blocks[-1].name = lattice_obj.name

        # weightを設定
        mesh_obj.data.shape_keys.key_blocks[-1].value = shape_key_weight

    def apply_shape_key(obj):
        shape_keys = obj.data.shape_keys

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shape_key_add(from_mix=True)
        new_shape_key = shape_keys.key_blocks[-1]

        for key_block in list(shape_keys.key_blocks):
            if (key_block != new_shape_key):
                obj.shape_key_remove(key_block)

        new_shape_key.name = "Mixed Shape"

    def move_origin_to_center(collider_mesh_obj):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        collider_mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = collider_mesh_obj

        # 原点を重心に移動
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

        collider_mesh_obj.select_set(False)

    def restore_bone_positions(bone_mesh_obj):
        v1 = bone_mesh_obj.data.vertices[0].co
        v2 = bone_mesh_obj.data.vertices[1].co

        # 編集モードに切り替えてボーンの位置を更新
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')

        edit_bone = armature.data.edit_bones.get(bone_mesh_obj.name)
        if not edit_bone.use_connect:
            edit_bone.head = v1
            edit_bone.tail = v2
        else:
            edit_bone.tail = v2
        
        bpy.ops.object.mode_set(mode='OBJECT')

    def restore_collider_positions(collider_mesh_obj, empty_obj): # edit_boneはparent_boneのEditBone
        # Sphereのグローバル位置を取得
        sphere_global_location = collider_mesh_obj.matrix_world.translation

        # アーマチュアを編集モードに切り替えてボーン情報を取得
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bone = armature.data.edit_bones.get(empty_obj.parent_bone)

        # tailの座標を取得して、逆行列を作成
        bone_tail_matrix = edit_bone.matrix.copy()
        bone_tail_matrix.translation = edit_bone.tail
        bone_tail_matrix_inv = bone_tail_matrix.inverted()

        bpy.ops.object.mode_set(mode='OBJECT')

        # グローバル座標をボーンのtail基準の相対座標に変換
        relative_location = bone_tail_matrix_inv @ sphere_global_location

        # Emptyオブジェクトの相対座標を更新
        empty_obj.location = relative_location

        # Sphere の寸法（Dimensions）を取得して平均を計算
        sphere_dim_x = collider_mesh_obj.dimensions.x
        sphere_dim_y = collider_mesh_obj.dimensions.y
        sphere_dim_z = collider_mesh_obj.dimensions.z
        average_dimension = (sphere_dim_x + sphere_dim_y + sphere_dim_z) / 3

        # Emptyオブジェクトの寸法を更新
        empty_obj.empty_display_size = average_dimension/2

    def recursive_process(bone_name, current_branch_bone_name, setting_index):
        # ボーンのメッシュを生成
        bone = armature.data.bones.get(bone_name)
        child_bone_names = [child_bone.name for child_bone in bone.children]
        bone_mesh_obj = generate_bone_mesh(bone)
        bpy.context.collection.objects.link(bone_mesh_obj)
        # latticeを適用
        for lattice_obj in lattices_objects_list[setting_index]:
            apply_lattice(bone_mesh_obj, lattice_obj)
        # シェイプキーを適用
        apply_shape_key(bone_mesh_obj)
        # ボーンの位置を復元
        restore_bone_positions(bone_mesh_obj)
        # bone_mesh_objを削除
        bpy.data.objects.remove(bone_mesh_obj)

        # `collider_map`のキーに現在のボーンを親として持つ対応するコライダーを取得しスフィアメッシュを生成
        if collider_map is not None and bone_name in collider_map:
            for collider_name in collider_map[bone_name]:
                collider_mesh_obj = bpy.data.objects.get(f"{collider_name}_ColliderSphere")
                # latticeを適用
                for lattice_obj in lattices_objects_list[setting_index]:
                    apply_lattice(collider_mesh_obj, lattice_obj)
                # シェイプキーを適用
                apply_shape_key(collider_mesh_obj)
                # 原点を重心に移動
                move_origin_to_center(collider_mesh_obj)
                # コライダーの位置を復元
                empty_obj = bpy.data.objects.get(collider_name)
                restore_collider_positions(collider_mesh_obj, empty_obj)
                # collider_mesh_objを削除
                bpy.data.objects.remove(collider_mesh_obj)

        # 子ボーンに対して再帰的に処理
        for child_bone_name in child_bone_names:
            # 次の設定に属するかどうかを判断
            for idx, setting in enumerate(settings):
                if child_bone_name.startswith(setting.branch_bone_name) and child_bone_name != current_branch_bone_name:
                    recursive_process(child_bone_name, setting.branch_bone_name, idx)
                    return
            # 現在の設定内で処理を続ける
            recursive_process(child_bone_name, current_branch_bone_name, setting_index)

    # アーマチュアの最初のボーンを基準にグループ化
    root_bone_name = armature.data.bones[0].name

    # `root_bone_name` に一致する設定のインデックスを取得
    idx = next((i for i, s in enumerate(settings) if s.branch_bone_name == root_bone_name), None)
    if idx is None:
        # 設定が見つからない場合はRootボーンを基準に設定を追加
        print("Setting not found. Adding new setting.")
        idx = len(settings)
        new_setting = settings.add()
        new_setting.branch_bone_name = root_bone_name
        new_setting.lattice_names = ""

    lattices_objects_list = []
    for setting in settings:
        lattice_names = [name.strip() for name in setting.lattice_names.split(',') if name.strip()]
        if len(lattice_names) > 0:
            lattice_objects = [bpy.data.objects.get(name) for name in lattice_names]
            lattices_objects_list.append(lattice_objects)
        else:
            lattices_objects_list.append([])

    print(lattices_objects_list)
    # 再帰的なグループ化を開始
    recursive_process(root_bone_name, root_bone_name, idx)
