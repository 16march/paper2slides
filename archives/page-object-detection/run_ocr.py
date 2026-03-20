#!/usr/bin/env python3
"""
步骤7：OCR文本提取
从排序后的边界框中提取文本
"""

import cv2
import pytesseract
from pathlib import Path
import json

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
        'conf': conf
    }

def extract_region(image, obj):
    """从图像中提取边界框区域"""
    h, w = image.shape[:2]
    
    # 转换YOLO坐标为像素坐标
    x_center_px = int(obj['x_center'] * w)
    y_center_px = int(obj['y_center'] * h)
    width_px = int(obj['width'] * w)
    height_px = int(obj['height'] * h)
    
    x1 = max(0, x_center_px - width_px // 2)
    y1 = max(0, y_center_px - height_px // 2)
    x2 = min(w, x_center_px + width_px // 2)
    y2 = min(h, y_center_px + height_px // 2)
    
    return image[y1:y2, x1:x2]

def ocr_text(region, class_name):
    """对区域进行OCR"""
    if region.size == 0:
        return ""
    
    # 使用Tesseract OCR
    text = pytesseract.image_to_string(region).strip()
    
    # 根据类别进行后处理
    if class_name == 'section':
        # 移除section前的数字
        parts = text.split(maxsplit=1)
        if len(parts) > 1 and parts[0].replace('.', '').isdigit():
            text = parts[1]
    
    elif class_name == 'paragraph':
        # 段落需要处理换行和连字符
        lines = text.split('\n')
        processed_lines = []
        for line in lines:
            line = line.strip()
            if line.endswith('-'):
                processed_lines.append(line[:-1])  # 移除连字符
            elif line:
                processed_lines.append(line + ' ')
        text = ''.join(processed_lines).strip()
    
    return text

def process_page(image_path, annotation_file, output_dir):
    """处理单页"""
    # 读取图像
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"   ❌ 无法读取图像: {image_path}")
        return []
    
    # 解析标注
    objects = []
    with open(annotation_file, 'r') as f:
        for line in f:
            if line.strip():
                obj = parse_yolo_line(line)
                if obj:
                    objects.append(obj)
    
    # 排序
    objects.sort(key=lambda obj: (obj['y_center'] - obj['height']/2, obj['x_center']))
    
    # 提取文本
    results = []
    img_output_dir = output_dir / 'images'
    img_output_dir.mkdir(exist_ok=True)
    
    page_name = image_path.stem
    
    for i, obj in enumerate(objects, 1):
        class_name = obj['class_name']
        
        # 提取区域
        region = extract_region(image, obj)
        
        # 处理不同类型
        if class_name in ['title', 'author', 'section', 'paragraph', 'footnote']:
            # 文本类：OCR提取
            text = ocr_text(region, class_name)
            results.append({
                'index': i,
                'class': class_name,
                'type': 'text',
                'content': text,
                'confidence': obj['conf']
            })
        
        elif class_name in ['table', 'figure', 'formula']:
            # 图片类：保存为图片
            img_filename = f"{page_name}_obj{i}_{class_name}.png"
            img_path = img_output_dir / img_filename
            cv2.imwrite(str(img_path), region)
            
            results.append({
                'index': i,
                'class': class_name,
                'type': 'image',
                'image_path': str(img_path),
                'confidence': obj['conf']
            })
    
    return results

if __name__ == '__main__':
    print("📝 步骤7：OCR文本提取...")
    
    images_dir = Path('test_output')
    labels_dir = Path('test_output/predictions/labels')
    output_dir = Path('test_output/ocr_results')
    output_dir.mkdir(exist_ok=True)
    
    # 获取所有图像
    image_files = sorted(images_dir.glob('latex_dataset0-*.png'))
    
    all_results = {}
    
    for image_file in image_files:
        page_num = image_file.stem.split('-')[-1]
        label_file = labels_dir / f"{image_file.stem}.txt"
        
        if not label_file.exists():
            print(f"\n⚠️  跳过 {image_file.name} (无标注文件)")
            continue
        
        print(f"\n📄 处理页面 {page_num}: {image_file.name}")
        
        results = process_page(image_file, label_file, output_dir)
        
        # 显示提取结果
        for item in results:
            if item['type'] == 'text':
                preview = item['content'][:50] + '...' if len(item['content']) > 50 else item['content']
                print(f"   {item['index']}. {item['class']:10s} | {preview}")
            else:
                print(f"   {item['index']}. {item['class']:10s} | 图片: {Path(item['image_path']).name}")
        
        all_results[f'page_{page_num}'] = results
    
    # 保存JSON结果
    output_json = output_dir / 'extracted_content.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 步骤7完成！")
    print(f"   - 提取结果: {output_json}")
    print(f"   - 图片保存: {output_dir}/images/")
