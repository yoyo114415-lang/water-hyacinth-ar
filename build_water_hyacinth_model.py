"""
Blender 5.4+ Procedural 3D Modeling Script: 布袋蓮 (Water Hyacinth / Pontederia crassipes)
特色生物結構：
1. 膨大葉柄 (Spongy Bulbous Petioles) - 內部具發達通氣組織(氣室)，提供漂浮水面的浮力。
2. 匙形卵圓翠綠葉片 (Broad Glossy Leaves) - 葉表具厚角質蠟質層，防水耐曬。
3. 經典鳳眼藍花朵 (Blue-Purple Flower with Peacock Eye) - 六瓣花被，頂瓣具鮮黃眼斑與藍色暈輪。
4. 紫黑色懸浮羽狀鬚根 (Feathery Floating Roots) - 懸垂於水中吸收養分並如同龍骨維持重心平衡。
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

def reset_scene():
    """清空現有場景所有物件"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)

def create_material(name, base_color, roughness=0.3, metallic=0.0, specular=0.5):
    """建立標準 PBR 材質"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = nodes.get('Principled BSDF')
    if principled:
        # Blender 4.0+ / 5.0+ 屬性支援
        principled.inputs['Base Color'].default_value = base_color
        principled.inputs['Roughness'].default_value = roughness
        principled.inputs['Metallic'].default_value = metallic
        if 'Specular IOR Level' in principled.inputs:
            principled.inputs['Specular IOR Level'].default_value = specular
        elif 'Specular' in principled.inputs:
            principled.inputs['Specular'].default_value = specular
    return mat

def create_leaf_mesh(mat_leaf, mat_bulb, index, total=7):
    """建立單片含膨大葉柄的完整布袋蓮葉"""
    angle = (index / total) * 2 * math.pi
    tilt = 0.45 + (index % 2) * 0.15 # 向外傾斜弧度
    scale_factor = 0.85 + (index % 3) * 0.1
    
    # 1. 建立膨大葉柄 (Spindle/Bulb)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=0.22 * scale_factor,
        location=(0, 0, 0)
    )
    bulb = bpy.context.active_object
    bulb.name = f"Petiole_Bulb_{index}"
    
    # 變形為葫蘆/倒卵形葉柄
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(bulb.data)
    for v in bm.verts:
        # 上下拉長，且下部稍飽滿、上部收窄
        z = v.co.z
        v.co.z *= 2.0
        if z > 0:
            factor = max(0.2, 1.0 - z * 2.2)
            v.co.x *= factor
            v.co.y *= factor
        else:
            factor = max(0.3, 1.0 + z * 1.5)
            v.co.x *= factor
            v.co.y *= factor
    bmesh.update_edit_mesh(bulb.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 2. 建立頂部葉片 (Leaf Blade)
    bpy.ops.mesh.primitive_circle_add(
        vertices=24, radius=0.32 * scale_factor, fill_type='NGON',
        location=(0, 0, 0.42 * scale_factor)
    )
    leaf = bpy.context.active_object
    leaf.name = f"Leaf_Blade_{index}"
    
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(leaf.data)
    # 細分並使葉片微彎、稍微呈現圓匙形心狀
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    for v in bm.verts:
        # 心形葉片拉伸
        dist = math.sqrt(v.co.x**2 + v.co.y**2)
        v.co.y *= 1.35
        v.co.z = -0.08 * (dist**2) # 葉面向下微弧
        if v.co.y < 0:
            v.co.x *= (1.0 + abs(v.co.y) * 0.5)
    bmesh.update_edit_mesh(leaf.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 加上微厚度 (Solidify)
    sol = leaf.modifiers.new(name="Solidify", type='SOLIDIFY')
    sol.thickness = 0.015
    bpy.ops.object.modifier_apply(modifier="Solidify")
    
    # 葉片向外傾斜
    leaf.rotation_euler = Euler((0.35, 0, 0), 'XYZ')
    
    # 指派材質
    bulb.data.materials.append(mat_bulb)
    leaf.data.materials.append(mat_leaf)
    
    # 合併葉柄與葉片
    bpy.ops.object.select_all(action='DESELECT')
    bulb.select_set(True)
    leaf.select_set(True)
    bpy.context.view_layer.objects.active = bulb
    bpy.ops.object.join()
    
    combined_leaf = bpy.context.active_object
    combined_leaf.name = f"Water_Hyacinth_Leaf_{index}"
    
    # 套用平滑著色
    bpy.ops.object.shade_smooth()
    
    # 放置到蓮座狀圍繞圓心
    rad = 0.18
    combined_leaf.location = Vector((rad * math.cos(angle), rad * math.sin(angle), 0.15))
    combined_leaf.rotation_euler = Euler((tilt * math.sin(angle), -tilt * math.cos(angle), angle), 'XYZ')
    
    return combined_leaf

def create_flower(mat_petal, mat_eye, mat_stamen):
    """建立經典鳳眼藍花朵 (頂部花被具藍黃鳳眼)"""
    flower_parts = []
    
    # 6 片花瓣 (3 外輪、3 內輪)
    for i in range(6):
        angle = (i / 6.0) * 2 * math.pi
        is_top_petal = (i == 3) # 頂端朝上花瓣，具有金黃鳳眼
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.1,
            location=(0, 0, 0)
        )
        petal = bpy.context.active_object
        
        # 擠壓成薄片水滴花瓣
        petal.scale = Vector((0.6, 1.4, 0.08))
        bpy.ops.object.transform_apply(scale=True)
        
        if is_top_petal:
            petal.scale = Vector((1.3, 1.5, 0.08))
            bpy.ops.object.transform_apply(scale=True)
            petal.data.materials.append(mat_eye)
            petal.name = "Petal_Peacock_Eye"
        else:
            petal.data.materials.append(mat_petal)
            petal.name = f"Petal_{i}"
            
        bpy.ops.object.shade_smooth()
        
        # 旋轉排成漏斗狀花冠
        petal.location = Vector((0.08 * math.cos(angle), 0.08 * math.sin(angle), 0.05))
        petal.rotation_euler = Euler((0.45 * math.sin(angle), -0.45 * math.cos(angle), angle + math.pi/2), 'XYZ')
        flower_parts.append(petal)
        
    # 花蕊 (Stamens)
    for s in range(6):
        st_angle = (s / 6.0) * 2 * math.pi
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.006, depth=0.12, location=(0.02 * math.cos(st_angle), 0.02 * math.sin(st_angle), 0.05)
        )
        stamen = bpy.context.active_object
        stamen.data.materials.append(mat_stamen)
        stamen.rotation_euler = Euler((0.15 * math.sin(st_angle), -0.15 * math.cos(st_angle), st_angle), 'XYZ')
        bpy.ops.object.shade_smooth()
        flower_parts.append(stamen)
        
    # 合併整朵花
    bpy.ops.object.select_all(action='DESELECT')
    for p in flower_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = flower_parts[0]
    bpy.ops.object.join()
    flower = bpy.context.active_object
    flower.name = "Water_Hyacinth_Flower"
    return flower

def create_stem(mat_bulb):
    """建立中央直立挺出花莖"""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.035, depth=0.65, location=(0, 0, 0.32)
    )
    stem = bpy.context.active_object
    stem.name = "Flower_Stem"
    stem.data.materials.append(mat_bulb)
    bpy.ops.object.shade_smooth()
    return stem

def create_feathery_roots(mat_root, count=18):
    """建立水下懸浮羽狀鬚根系統 (提供水中平衡)"""
    roots = []
    for r in range(count):
        r_angle = (r / count) * 2 * math.pi + (r % 3) * 0.2
        spread = 0.06 + (r % 4) * 0.025
        depth = 0.55 + (r % 5) * 0.08
        
        # 曲線彎折根
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=10, radius=0.009, depth=depth,
            location=(spread * math.cos(r_angle), spread * math.sin(r_angle), -depth / 2.0)
        )
        root = bpy.context.active_object
        root.name = f"Feathery_Root_{r}"
        
        # 輕微隨機向外擴展
        tilt_x = 0.12 * math.sin(r_angle)
        tilt_y = -0.12 * math.cos(r_angle)
        root.rotation_euler = Euler((tilt_x, tilt_y, 0), 'XYZ')
        root.data.materials.append(mat_root)
        bpy.ops.object.shade_smooth()
        roots.append(root)
        
    # 合併根系
    bpy.ops.object.select_all(action='DESELECT')
    for rt in roots:
        rt.select_set(True)
    bpy.context.view_layer.objects.active = roots[0]
    bpy.ops.object.join()
    all_roots = bpy.context.active_object
    all_roots.name = "Water_Hyacinth_Root_System"
    return all_roots

def create_water_surface_indicator(mat_water):
    """建立象徵水面的半透明圓盤基座 (標示水上與水下分界)"""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=36, radius=0.9, depth=0.015, location=(0, 0, 0.0)
    )
    water = bpy.context.active_object
    water.name = "Water_Surface_Reference"
    water.data.materials.append(mat_water)
    bpy.ops.object.shade_smooth()
    return water

def build_complete_water_hyacinth(output_glb_path):
    print(">>> 開始建構布袋蓮 (Water Hyacinth) 3D 模型...")
    reset_scene()
    
    # 1. 材質調配
    # 葉片材質：鮮綠微反光 (模擬厚角質蠟質層)
    mat_leaf = create_material("Mat_Leaf", (0.12, 0.48, 0.15, 1.0), roughness=0.25, specular=0.6)
    
    # 膨大葉柄材質：黃綠海綿組織質地 (具通氣氣室)
    mat_bulb = create_material("Mat_Bulb", (0.35, 0.65, 0.22, 1.0), roughness=0.45, specular=0.3)
    
    # 花瓣材質：淡紫藍色花被
    mat_petal = create_material("Mat_Petal", (0.75, 0.68, 0.92, 1.0), roughness=0.35, specular=0.4)
    
    # 頂端鳳眼花瓣：中央孔雀藍與金黃斑點
    mat_eye = create_material("Mat_Eye", (0.95, 0.82, 0.15, 1.0), roughness=0.28, specular=0.7)
    
    # 雄蕊花絲
    mat_stamen = create_material("Mat_Stamen", (0.45, 0.25, 0.65, 1.0), roughness=0.4)
    
    # 水下懸浮羽狀鬚根：深紫黑褐色
    mat_root = create_material("Mat_Root", (0.10, 0.07, 0.12, 1.0), roughness=0.7)
    
    # 水面波紋參考底盤 (半透明水藍色)
    mat_water = create_material("Mat_Water", (0.2, 0.6, 0.85, 0.4), roughness=0.1, specular=0.9)
    
    all_objects = []
    
    # 2. 生成 7 片環狀放射的膨大葉片
    for i in range(7):
        leaf_obj = create_leaf_mesh(mat_leaf, mat_bulb, index=i, total=7)
        all_objects.append(leaf_obj)
        
    # 3. 建立中央挺出花莖與花序
    stem = create_stem(mat_bulb)
    all_objects.append(stem)
    
    flower = create_flower(mat_petal, mat_eye, mat_stamen)
    flower.location = Vector((0, 0, 0.62))
    all_objects.append(flower)
    
    # 4. 建立水下紫黑色懸浮鬚根
    roots = create_feathery_roots(mat_root, count=18)
    all_objects.append(roots)
    
    # 5. 水面參考底盤
    water_disc = create_water_surface_indicator(mat_water)
    all_objects.append(water_disc)
    
    # 6. 合併全部物體為單一結構
    bpy.ops.object.select_all(action='DESELECT')
    for obj in all_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = all_objects[0]
    bpy.ops.object.join()
    
    final_model = bpy.context.active_object
    final_model.name = "Water_Hyacinth_Plant"
    
    # 調整至適當 AR 檢視尺寸 (約 30cm 寬度)
    final_model.scale = Vector((0.7, 0.7, 0.7))
    bpy.ops.object.transform_apply(scale=True, location=True, rotation=True)
    
    print(f">>> 匯出 GLB 檔案至: {output_glb_path}")
    bpy.ops.export_scene.gltf(
        filepath=output_glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(">>> 3D 模型建置與 GLB 匯出成功！")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_glb = os.path.join(current_dir, "water_hyacinth.glb")
    build_complete_water_hyacinth(target_glb)
