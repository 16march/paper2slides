#!/usr/bin/env python3
"""
使用Transformers直接调用Nougat处理整页PDF
"""

import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

from PIL import Image
import torch
from pathlib import Path
import pdf2image

def process_pdf_fullpage(pdf_path, output_dir):
    """使用Nougat处理完整PDF（使用transformers）"""
    
    print(f"📄 处理PDF: {pdf_path}")
    print("🔄 第1步：PDF转图像...")
    
    # 转换PDF第1页为图像
    images = pdf2image.convert_from_path(
        pdf_path,
        first_page=1,
        last_page=1,
        dpi=300
    )
    
    if not images:
        print("❌ PDF转图像失败")
        return False
    
    page_image = images[0]
    print(f"✅ 图像大小: {page_image.size}")
    
    # 加载Nougat模型
    print("\n🔄 第2步：加载Nougat模型...")
    from transformers import VisionEncoderDecoderModel, NougatProcessor
    
    model_name = "facebook/nougat-small"
    processor = NougatProcessor.from_pretrained(model_name)
    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    
    device = "cpu"
    model.to(device)
    model.eval()
    print(f"✅ 模型加载成功 (设备: {device})")
    
    # 处理图像
    print("\n🔄 第3步：Nougat OCR处理（这可能需要1-2分钟）...")
    
    pixel_values = processor(page_image, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)
    
    # 生成
    with torch.no_grad():
        outputs = model.generate(
            pixel_values,
            max_length=model.config.max_length,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
            use_cache=True,
            num_beams=1,
        )
    
    # 解码
    sequence = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    
    # 保存结果
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    output_file = output_path / f"{Path(pdf_path).stem}_page1_fullpage.mmd"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sequence)
    
    print(f"\n✅ 处理完成！")
    print(f"📁 输出文件: {output_file}")
    print(f"📏 生成文本长度: {len(sequence)} 字符")
    
    # 预览
    print(f"\n{'='*60}")
    print("📄 前800字符预览:")
    print(f"{'='*60}")
    print(sequence[:800])
    if len(sequence) > 800:
        print("\n... (后续省略)")
    print(f"{'='*60}")
    
    return True

if __name__ == "__main__":
    pdf_path = "latex_dataset0.pdf"
    output_dir = "test_output/nougat_fullpage"
    
    print("🎯 Nougat整页PDF处理测试")
    print("="*60)
    
    success = process_pdf_fullpage(pdf_path, output_dir)
    
    if success:
        print("\n🎉 成功！现在可以对比三个版本：")
        print("  1. Tesseract版本 (test_output/final_output.pdf)")
        print("  2. Nougat混合版本 (test_output/final_output_nougat.pdf)")
        print("  3. Nougat整页版本 (test_output/nougat_fullpage/)")
