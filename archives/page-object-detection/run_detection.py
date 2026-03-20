#!/usr/bin/env python3
"""
步骤5：使用训练好的YOLOv8n模型进行目标检测
"""

import sys
import os

# 检查环境
try:
    from ultralytics import YOLO
    print("✅ ultralytics已安装")
except ImportError:
    print("❌ 缺少ultralytics，正在安装...")
    os.system("pip install -q ultralytics")
    from ultralytics import YOLO

if __name__ == '__main__':
    print("🔍 步骤5：开始YOLO目标检测...")
    
    # 加载训练好的模型
    model = YOLO('runs/detect/cpu_run_final/weights/best.pt')
    print(f"✅ 模型加载成功: {model.model}")
    
    # 对测试图像进行推理
    results = model.predict(
        source='test_output/*.png',
        save=True,
        save_txt=True,  # 保存YOLO格式的标注
        save_conf=True,
        conf=0.5,
        device='cpu',
        project='test_output',
        name='predictions',
        exist_ok=True
    )
    
    print(f"\n✅ 检测完成！共处理 {len(results)} 张图像")
    print("📁 结果保存在: test_output/predictions/")
    print("   - 可视化结果(带框): test_output/predictions/*.png")
    print("   - YOLO标注文件: test_output/predictions/labels/*.txt")

