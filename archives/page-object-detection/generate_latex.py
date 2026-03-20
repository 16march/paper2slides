#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import makedirs
from os.path import join, basename
from pytesseract import image_to_string
import cv2


OBJ_NAMES = ['title', 'author', 'section', 'paragraph', 'table', 'figure', 'formula', 'footnote']
GENERATED_OBJ = ['title', 'author', 'section', 'paragraph', 'footnote']

def get_regions(image, annotation_file):
  with open(annotation_file, 'r') as f:
    annotations = f.readlines()

  regions = []
  img = cv2.imread(image)
  height, width, _ = img.shape
  for annotation in annotations:
    parts = annotation.split(' ')
    if len(parts) < 5:
      continue
    # 支持带置信度的格式 (6个值) 或不带的格式 (5个值)
    type_id = float(parts[0])
    x_yolo = float(parts[1])
    y_yolo = float(parts[2])
    width_yolo = float(parts[3])
    height_yolo = float(parts[4])
    # parts[5] 是置信度，我们不需要它
    
    type = OBJ_NAMES[int(type_id)]
    
    x = round((x_yolo - 0.5*width_yolo) * width)
    y = round((y_yolo - 0.5*height_yolo) * height)
    w = round(width_yolo * width)
    h = round(height_yolo * height)
    bb = img[y:y + h, x: x + w]

    regions.append((type, bb, y_yolo))  # 添加y坐标用于排序
  
  # 按y坐标排序
  regions.sort(key=lambda r: r[2])
  return [(t, bb) for t, bb, _ in regions]  # 返回排序后的结果

def generate_tex_from_regions(regions, out_dir, jobname):
  for i, (type, region) in enumerate(regions):
    if type not in GENERATED_OBJ:
      continue

    fname = join(out_dir, f'{jobname}_generated_{i}_{type}.tex')
    tex = None
    
    if type == 'title':
      tex = generate_title_tex(image_to_string(region))

    if type == 'author':
      author = image_to_string(region).replace('\n', '\\\\')
      tex = generate_author_tex(author)

    if type == 'section':
      section = image_to_string(region)
      if section and len(section) > 0 and str.isdigit(section[0]):
        section = ' '.join(section.split()[1:])

      tex = generate_section_tex(section)

    if type == 'paragraph':
      sentences = image_to_string(region).split('\n')
      remove_hypen = lambda x: x[:-1] if x and len(x) > 0 and x[-1] == '-' else x
      sentences = [remove_hypen(x) for x in sentences]
      paragraph = ''.join(sentences)

      tex = generate_paragraph_tex(paragraph)

    if type == 'footnote':
      footnote = image_to_string(region)
      if footnote and len(footnote) > 0 and str.isdigit(footnote[0]):
        footnote = ' '.join(footnote.split()[1:])
      
      tex = generate_footnote_tex(footnote)


    if tex is not None:
      with open(fname, 'w') as f:
        f.write(tex)

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

    regions = get_regions(args.img, args.annotation)
    generate_tex_from_regions(regions, args.out_dir, basename(args.img))

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