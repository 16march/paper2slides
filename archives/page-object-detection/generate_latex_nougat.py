#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Nougat OCR的LaTeX生成脚本
基于原版generate_latex.py，但用Nougat替代Tesseract
"""

from os import makedirs
from os.path import join, basename
import cv2
from nougat_ocr_wrapper import nougat_ocr_region

OBJ_NAMES = ['title', 'author', 'section', 'paragraph', 'table', 'figure', 'formula', 'footnote']
GENERATED_OBJ = ['title', 'author', 'section', 'paragraph', 'footnote']

def get_regions(image, annotation_file):
  """提取图像区域（与原版相同）"""
  with open(annotation_file, 'r') as f:
    annotations = f.readlines()

  regions = []
  img = cv2.imread(image)
  height, width, _ = img.shape
  for annotation in annotations:
    parts = annotation.split(' ')
    if len(parts) < 5:
      continue
    # 支持带置信度的格式
    type_id = float(parts[0])
    x_yolo = float(parts[1])
    y_yolo = float(parts[2])
    width_yolo = float(parts[3])
    height_yolo = float(parts[4])
    
    type = OBJ_NAMES[int(type_id)]
    
    x = round((x_yolo - 0.5*width_yolo) * width)
    y = round((y_yolo - 0.5*height_yolo) * height)
    w = round(width_yolo * width)
    h = round(height_yolo * height)
    bb = img[y:y + h, x: x + w]

    regions.append((type, bb, y_yolo))  # 添加y坐标用于排序
  
  # 按y坐标排序
  regions.sort(key=lambda r: r[2])
  return [(t, bb) for t, bb, _ in regions]

def generate_tex_from_regions(regions, out_dir, jobname):
  """使用Nougat OCR生成LaTeX片段"""
  for i, (type, region) in enumerate(regions):
    if type not in GENERATED_OBJ:
      continue

    fname = join(out_dir, f'{jobname}_generated_{i}_{type}.tex')
    tex = None
    
    # 使用Nougat OCR提取文本
    print(f"  🔍 Nougat OCR处理 {type}...")
    text = nougat_ocr_region(region, return_markdown=False)
    
    if type == 'title':
      tex = generate_title_tex(text)

    if type == 'author':
      # 作者信息保持换行
      author = text.replace('\n', '\\\\')
      tex = generate_author_tex(author)

    if type == 'section':
      # Section标题不移除数字，保留完整
      tex = generate_section_tex(text)

    if type == 'paragraph':
      # 段落处理
      sentences = text.split('\n')
      # 移除连字符
      remove_hypen = lambda x: x[:-1] if x and len(x) > 0 and x[-1] == '-' else x
      sentences = [remove_hypen(x) for x in sentences]
      paragraph = ''.join(sentences)
      tex = generate_paragraph_tex(paragraph)

    if type == 'footnote':
      tex = generate_footnote_tex(text)

    if tex is not None:
      with open(fname, 'w') as f:
        f.write(tex)
      print(f"  ✅ 生成: {fname}")

def build_latex(content):
  return f'''\\documentclass[11pt,a4paper, twocolumn]{{article}}
  
\\begin{{document}}
{content}
\\end{{document}}
  '''

def generate_title_tex(str):
  title = f'''
\\title{{\\textbf{{{str}}}}}
\\author{{}}
\\date{{}}
\\maketitle
  '''
  return build_latex(title)

def generate_author_tex(str):
  author = f'''
\\title{{\\textbf{{title}}}}
\\author{{
  {str}
}}
\\date{{}}
\\maketitle
  '''
  return build_latex(author)
  
def generate_section_tex(str):
  section = f'''
\\section{{{str}}}
  '''
  return build_latex(section)

def generate_paragraph_tex(str):
  paragraph = f'''
{str}
  '''
  return build_latex(paragraph)

def generate_footnote_tex(str):
  footnote = f'''
\\footnotetext[1]{{{str}}}
  '''
  return build_latex(footnote)

def main():
    args = parse_args()

    makedirs(args.out_dir, exist_ok=True)

    print(f"\n📄 处理: {args.img}")
    print("🔄 使用Nougat OCR (这可能需要一些时间)...\n")
    
    regions = get_regions(args.img, args.annotation)
    generate_tex_from_regions(regions, args.out_dir, basename(args.img))
    
    print(f"\n✅ 完成！输出目录: {args.out_dir}")

def parse_args():
  from argparse import ArgumentParser

  parser = ArgumentParser()
  parser.add_argument('--img',
                      dest='img',
                      help='Image of a page in a document')
  parser.add_argument('--annotation',
                      dest='annotation',
                      help='YOLO annotation file')
  parser.add_argument('--out_dir',
                      dest='out_dir',
                      help='Output directory')
  return parser.parse_args()

if __name__ == "__main__":
    main()
