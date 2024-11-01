# Armature Deformer

Blenderアドオン「Armature Deformer」は、アーマチュアとコライダーにラティスモディファイアを適用できるアドオンです。

`armature_collider_processor.py`の関数をAPIとして利用しカスタムスクリプトに統合することも可能です。

BlenderのGUIモードだと多少時間がかかりますがPythonでヘッドレスでの実行だと早く完了します。

https://github.com/user-attachments/assets/9f8294c7-493b-4736-a069-c460a30a6a67

## 機能

- **アーマチュアへのラティス適用**: アーマチュア全体または特定のボーン以下の階層にラティスモディファイアを適用可能
- **コライダーオブジェクトへのラティス適用（任意）**: emptyオブジェクトとして設定されたコライダーにラティスを適用
- **複数ラティスの適用**: 複数のラティスオブジェクトを一括で順次適用する機能
- **APIとしての利用**: `armature_collider_processor.py`の関数をAPIとして他のBlenderスクリプトから呼び出し可能

## インストール方法

このリポジトリをクローンまたは[releasesページ](https://github.com/Yeq6X/armature_deformer/releases/tag/v1.0.0)からZIPファイルとしてダウンロード&インストール

## 使い方
![image](https://github.com/user-attachments/assets/a17a7cba-9bc2-4df2-927b-2e23388d9a5c)

1. **アーマチュアとコライダーの選択**: 追加された「Armature Deformer」パネルで、対象のアーマチュアと（任意で）コライダーのコレクションを選択します。

2. **コライダーの設定（任意）**: コライダーは、親がアーマチュアのボーンである球体のemptyオブジェクトを仮定しています。たとえば、VRoidアバターの「Collider」コレクションに含まれる球体のemptyオブジェクトが対象となります。

4. **ラティスの適用設定**: `Processing Settings`セクションで`branch_bone`と`lattice_names`（カンマ区切り）を設定し、さらに必要に応じて複数の設定を追加します。
   - **branch_bone**: ラティスの適用基準となるボーン名で、指定されたボーンとその配下のすべての子ボーンにラティスが適用されます。例として、`J_Bip_C_Neck`を指定すると、頭や髪のボーンに対して一括処理が可能です。
   - **lattice_names**: カンマ区切りで複数のラティスオブジェクト名を指定。先頭から順にラティスが適用されます。

5. **実行**: `Execute Processing`ボタンをクリックすると、ラティスがアーマチュアとコライダーに適用され、指定された処理が実行されます。

## APIとしての使用方法

`armature_collider_processor.py`内の関数をAPIとして利用することで、他のBlenderスクリプトから簡単に呼び出せます。主な関数は以下のとおりです：

- **`apply_lattice(armature, collider_collection, shape_key_weight, processing_settings)`**: アーマチュアと指定されたコライダーにラティスモディファイアを適用します。`shape_key_weight`でシェイプキーの影響度を指定できます。

- **`generate_collider_meshes(collider_collection)`**: 球体のemptyオブジェクトのコレクションを基に同位置、同スケールで新しいコライダーを生成。

- **`process_bones_and_colliders_recursively`**: アーマチュアの各ボーンに対してラティスを適用し、再帰的に処理するメインの処理関数。

## 処理の仕組み

- **ラティス適用**: `apply_lattice`関数では、指定したラティスオブジェクトをアーマチュアやコライダーに順次適用。`lattice_names`に複数指定された場合、順番にラティスが適用されます。
- **ボーン構造の再帰的処理**: `process_bones_and_colliders_recursively`では、指定された`branch_bone`を起点に、各ボーンにラティスを適用。各ボーンやコライダーがメッシュとして生成された後、ラティス変形を行い、その座標、スケールをもとのアーマチュア、コライダーに適用します。
