import os
import shutil
import random
import yaml

# ================= 配置区域 (请根据你的实际路径修改) =================

# 1. 你的图片文件夹路径 (看截图应该是这里)
SOURCE_IMG_DIR = 'img_dir/'

# 2. 你的标注文件夹路径 (看截图应该是这里)
SOURCE_LABEL_DIR = 'yolo_dir/'

# 3. 你想把整理好的数据集放在哪里 (生成的文件夹名)
OUTPUT_DIR = 'my_yolo_dataset'

# 4. 验证集比例 (0.2 表示 20% 做验证集，80% 做训练集)
VAL_SPLIT_RATIO = 0.2

# 5. 类别名称 (必须严格对应学长论文的 obj.names 顺序)
CLASS_NAMES = [
    'title', 'author', 'section', 'paragraph', 
    'table', 'figure', 'formula', 'footnote'
]

# ===================================================================

def main():
    # 1. 检查源文件夹是否存在
    if not os.path.exists(SOURCE_IMG_DIR) or not os.path.exists(SOURCE_LABEL_DIR):
        print(f"❌ 错误: 找不到源文件夹！请检查路径:\n{SOURCE_IMG_DIR}\n{SOURCE_LABEL_DIR}")
        return

    # 2. 创建目标文件夹结构
    subdirs = ['train/images', 'train/labels', 'val/images', 'val/labels']
    for subdir in subdirs:
        os.makedirs(os.path.join(OUTPUT_DIR, subdir), exist_ok=True)

    print("🔍 正在扫描并配对文件...")
    
    # 获取所有图片文件 (.jpg, .png)
    image_files = [f for f in os.listdir(SOURCE_IMG_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    valid_pairs = []
    
    # 3. 检查每张图是否有对应的 txt
    for img_file in image_files:
        file_name_no_ext = os.path.splitext(img_file)[0]
        label_file = file_name_no_ext + '.txt'
        label_path = os.path.join(SOURCE_LABEL_DIR, label_file)
        
        if os.path.exists(label_path):
            valid_pairs.append((img_file, label_file))
        else:
            print(f"⚠️ 跳过 (无标注): {img_file}")

    total_count = len(valid_pairs)
    print(f"✅ 成功找到 {total_count} 组有效数据 (图片+标注)")

    if total_count == 0:
        print("❌ 没有找到有效数据，请检查文件夹路径或文件名是否匹配。")
        return

    # 4. 随机打乱并切分
    random.shuffle(valid_pairs)
    val_count = int(total_count * VAL_SPLIT_RATIO)
    
    val_set = valid_pairs[:val_count]
    train_set = valid_pairs[val_count:]
    
    print(f"📊 划分结果: 训练集 {len(train_set)} 张, 验证集 {len(val_set)} 张")

    # 5. 复制文件 (Copy files)
    def copy_files(dataset, split_name):
        print(f"🚀 正在复制 {split_name} 数据...")
        for img_file, label_file in dataset:
            # 源路径
            src_img = os.path.join(SOURCE_IMG_DIR, img_file)
            src_label = os.path.join(SOURCE_LABEL_DIR, label_file)
            
            # 目标路径
            dst_img = os.path.join(OUTPUT_DIR, split_name, 'images', img_file)
            dst_label = os.path.join(OUTPUT_DIR, split_name, 'labels', label_file)
            
            shutil.copy(src_img, dst_img)
            shutil.copy(src_label, dst_label)

    copy_files(train_set, 'train')
    copy_files(val_set, 'val')

    # 6. 自动生成 data.yaml
    print("📝 正在生成 data.yaml 配置文件...")
    yaml_content = {
        'path': os.path.abspath(OUTPUT_DIR),  # 使用绝对路径最稳妥
        'train': 'train/images',
        'val': 'val/images',
        'nc': len(CLASS_NAMES),
        'names': {i: name for i, name in enumerate(CLASS_NAMES)}
    }
    
    yaml_path = os.path.join(OUTPUT_DIR, 'data.yaml')
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, sort_keys=False)

    print("\n" + "="*50)
    print(f"🎉 大功告成！数据集已整理到: {OUTPUT_DIR}")
    print(f"📄 配置文件位置: {yaml_path}")
    print("="*50)
    print("\n接下来你可以直接运行训练脚本了！")

if __name__ == '__main__':
    main()