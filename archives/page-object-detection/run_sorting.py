#!/usr/bin/env python3
"""
步骤6：边界框排序
按照阅读顺序（从上到下，从左到右）排序检测到的对象
"""

import os
from pathlib import Path

# YOLO类别定义
CLASS_NAMES = ['title', 'author', 'section', 'paragraph', 'table', 'figure', 'formula', 'footnote']

def parse_yolo_line(line):
    """解析YOLO标注行"""
    parts = line.strip().split()
    if len(parts) < 5:
        return None
    
    class_id = int(parts[0])
    x_center = float(parts[1])
    y_center = float(parts[2])
    width = float(parts[3])
    height = float(parts[4])
    conf = float(parts[5]) if len(parts) > 5 else 1.0
    
    return {
        'class_id': class_id,
        'class_name': CLASS_NAMES[class_id],
        'x_center': x_center,
        'y_center': y_center,
        'width': width,
        'height': height,
        'conf': conf,
        'y_top': y_center - height / 2,  # 用于排序
        'x_left': x_center - width / 2
    }

def sort_objects(objects):
    """
    排序策略：
    1. 先按Y坐标（从上到下）
    2. 同一行内按X坐标（从左到右）
    """
    # 简单策略：按y_center排序
    return sorted(objects, key=lambda obj: (obj['y_top'], obj['x_left']))

def process_page(annotation_file):
    """处理单页的标注文件"""
    objects = []
    
    with open(annotation_file, 'r') as f:
        for line in f:
            if line.strip():
                obj = parse_yolo_line(line)
                if obj:
                    objects.append(obj)
    
    # 排序
    sorted_objects = sort_objects(objects)
    
    return sorted_objects

if __name__ == '__main__':
    print("🔄 步骤6：边界框排序...")
    
    labels_dir = Path('test_output/predictions/labels')
    output_dir = Path('test_output/sorted_results')
    output_dir.mkdir(exist_ok=True)
    
    # 处理所有标注文件
    label_files = sorted(labels_dir.glob('*.txt'))
    
    for label_file in label_files:
        print(f"\n📄 处理: {label_file.name}")
        
        sorted_objects = process_page(label_file)
        
        # 保存排序后的结果
        output_file = output_dir / label_file.name.replace('.txt', '_sorted.txt')
        
        with open(output_file, 'w') as f:
            f.write(f"# 排序后的对象 (共{len(sorted_objects)}个)\n")
            f.write("# 格式: 类别 | X中心 | Y中心 | 宽 | 高 | 置信度\n\n")
            
            for i, obj in enumerate(sorted_objects, 1):
                f.write(f"{i}. {obj['class_name']:10s} | "
                       f"x={obj['x_center']:.3f} y={obj['y_center']:.3f} | "
                       f"w={obj['width']:.3f} h={obj['height']:.3f} | "
                       f"conf={obj['conf']:.3f}\n")
        
        # 打印预览
        print(f"   排序结果（共{len(sorted_objects)}个对象）：")
        for i, obj in enumerate(sorted_objects, 1):
            print(f"   {i}. {obj['class_name']:10s} (y={obj['y_top']:.3f})")
        
        print(f"   ✅ 保存到: {output_file}")
    
    print(f"\n✅ 步骤6完成！排序结果保存在: {output_dir}/")
