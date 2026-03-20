#!/usr/bin/env python3
"""
Nougat OCR 封装模块
为YOLO检测到的区域提供高质量的OCR服务
"""

import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # M3兼容性

import cv2
import numpy as np
from PIL import Image
import torch
from pathlib import Path
import tempfile

# 全局模型实例（懒加载）
_nougat_model = None
_nougat_processor = None

def initialize_nougat():
    """初始化Nougat模型（仅初始化一次）"""
    global _nougat_model, _nougat_processor
    
    if _nougat_model is not None:
        return _nougat_model, _nougat_processor
    
    print("🔄 正在加载Nougat模型（首次加载需要下载，约350MB）...")
    
    try:
        from transformers import VisionEncoderDecoderModel, NougatProcessor
        
        # 使用small模型以节省资源
        model_name = "facebook/nougat-small"
        
        _nougat_processor = NougatProcessor.from_pretrained(model_name)
        _nougat_model = VisionEncoderDecoderModel.from_pretrained(model_name)
        
        # CPU模式（M3可能不支持MPS）
        device = "cpu"
        _nougat_model.to(device)
        _nougat_model.eval()
        
        print(f"✅ Nougat模型加载成功 (设备: {device})")
        
    except Exception as e:
        print(f"❌ Nougat模型加载失败: {e}")
        raise
    
    return _nougat_model, _nougat_processor

def nougat_ocr_region(image_region, return_markdown=False):
    """
    对图像区域进行Nougat OCR
    
    Args:
        image_region: numpy array (BGR格式，来自cv2)
        return_markdown: 是否返回markdown格式（默认返回纯文本）
    
    Returns:
        str: 提取的文本
    """
    if image_region.size == 0:
        return ""
    
    try:
        model, processor = initialize_nougat()
        
        # 转换为PIL Image (RGB)
        if len(image_region.shape) == 2:
            # 灰度图
            pil_image = Image.fromarray(image_region).convert("RGB")
        else:
            # BGR -> RGB
            rgb_image = cv2.cvtColor(image_region, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
        
        # Nougat预处理
        pixel_values = processor(pil_image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(model.device)
        
        # 生成
        with torch.no_grad():
            outputs = model.generate(
                pixel_values,
                max_length=model.config.max_length,
                pad_token_id=processor.tokenizer.pad_token_id,
                eos_token_id=processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,  # 加速
            )
        
        # 解码
        sequence = processor.batch_decode(outputs, skip_special_tokens=True)[0]
        
        # 后处理：移除markdown标记（如果需要纯文本）
        if not return_markdown:
            text = clean_markdown(sequence)
        else:
            text = sequence
        
        return text.strip()
        
    except Exception as e:
        print(f"⚠️  Nougat OCR失败，回退到空字符串: {e}")
        return ""

def clean_markdown(markdown_text):
    """
    清理markdown标记，提取纯文本
    保留换行和基本格式
    """
    import re
    
    text = markdown_text
    
    # 移除数学公式标记（但保留内容）
    text = re.sub(r'\$\$([^\$]+)\$\$', r'\1', text)  # 行间公式
    text = re.sub(r'\$([^\$]+)\$', r'\1', text)      # 行内公式
    
    # 移除markdown标题标记
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # 移除加粗和斜体
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # 移除链接保留文本
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    return text

def nougat_ocr_image_file(image_path):
    """
    对整个图像文件进行OCR（用于测试）
    
    Args:
        image_path: 图像文件路径
    
    Returns:
        str: 提取的markdown文本
    """
    image = cv2.imread(str(image_path))
    return nougat_ocr_region(image, return_markdown=True)


if __name__ == "__main__":
    # 测试代码
    print("测试Nougat OCR封装...")
    
    # 测试初始化
    model, processor = initialize_nougat()
    print("模型初始化成功")
    
    # 测试一个小图像
    test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
    result = nougat_ocr_region(test_image)
    print(f"测试结果: '{result}'")
