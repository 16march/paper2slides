#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import shutil
import tempfile
import subprocess 
from subprocess import PIPE
import csv
from pdf2image import convert_from_bytes

def compile_latex(fname, latex_dir, compile_twice=True):
  with tempfile.TemporaryDirectory() as td:
    jobname = os.path.basename(fname)[:-len('.tex')]
    try:
      fp = subprocess.run(f'pdflatex -interaction=nonstopmode -output-directory="{td}" "{fname}"', shell=True, stdout=PIPE, stderr=PIPE, timeout=60, cwd=latex_dir)
      if compile_twice:
        fp = subprocess.run(f'pdflatex -interaction=nonstopmode -output-directory="{td}" "{fname}"', shell=True, stdout=PIPE, stderr=PIPE, timeout=60, cwd=latex_dir)
      with open(os.path.join(td, f'{jobname}.pos'), 'rb') as f:
        pos = list(map(lambda x: x.decode('UTF-8'), f.readlines()))
      with open(os.path.join(td, f'{jobname}.pdf'), 'rb') as f:
        pdf = f.read()
    except subprocess.TimeoutExpired:
      print(f"Timeout compiling {fname}")
      return None, None
    except FileNotFoundError:
      print(f"Failed to generate PDF or POS file for {fname}")
      if fp.stderr:
          print("STDERR:", fp.stderr.decode('utf-8'))
      return None, None
      
  return pdf, pos

def create_annotation(pos, jobname, yolo_dir, csv_dir):
  rows = csv.reader(pos, delimiter=',', quotechar='"')

  y_step = 0
  column = 0
  page = 0
  yolo_annotation = []
  csv_annotation = ['type,id,x,y,width,height,content\n']

  for row in rows:
    type = row[0]
    text = row[-1]
    row_numbers = list(map(lambda x: float(x), row[1:-1]))
    x, y, depth, height, paperheight, width, paperwidth, linewidth = row_numbers

    if 'title' in type:
      if width > linewidth:
        multiplier = ((width // linewidth) + 1)
        height = height * multiplier * 1.25
        depth = depth * multiplier * 1.25
        width = linewidth
      else:
        x = x + 0.5*(linewidth - width)

    if 'author' in type or 'section' in type or 'formula' in type or 'footnote' in type:
      y = y + height
    if 'section' in type:
      section_indent = 8.540379999999999
      x = x - section_indent
      width = width + section_indent

    if 'formula' in type:
      if width > linewidth:
        multiplier = ((width // linewidth) + 1)
        height = height * multiplier * 1.25
        depth = depth * multiplier * 1.25
        if 30.53094 < x < 111.71721:
          x = 30.53094
        else:
          x = 111.71721
        width = linewidth

    x_centre = (x + 0.5*width) / paperwidth
    y_centre = (paperheight - y + 0.5*(height + depth)) / paperheight
    width_yolo = width / paperwidth
    height_yolo = (depth + height) / paperheight

    if y_step == 0:
      y_step = y_centre
    if column == 0:
      column = 1

    if y_centre > y_step and 'author' not in type and 'footnote' not in type:
      y_step = y_centre
    elif y_centre < y_step:
      # 2nd column
      column += 1
      y_step = y_centre

    if column >= 3:
      # new page
      page += 1
      with open(os.path.join(yolo_dir, f'{jobname}_{page}.txt'), 'w') as f:
        f.writelines(yolo_annotation)

      with open(os.path.join(csv_dir, f'{jobname}_{page}.csv'), 'w') as f:
        f.writelines(csv_annotation)

      yolo_annotation.clear()
      csv_annotation = ['type,id,x,y,width,height,content\n']
      column = 1
    
    pod_type, pod_id = type.split('_')
    yolo_annotation.append(f'{map_type(pod_type)} {x_centre} {y_centre} {width_yolo} {height_yolo}\n')
    
    csv_annotation.append(f'{pod_type},{pod_id},{x_centre},{y_centre},{width_yolo},{height_yolo},{text}\n')
  
  page += 1
  with open(os.path.join(yolo_dir, f'{jobname}_{page}.txt'), 'w') as f:
    f.writelines(yolo_annotation)
  with open(os.path.join(csv_dir, f'{jobname}_{page}.csv'), 'w') as f:
    f.writelines(csv_annotation)

def create_images_from_pdf(pdf, jobname, img_dir):
  images = convert_from_bytes(pdf, fmt='jpg')
  for i, im in enumerate(images):
    im.save(os.path.join(img_dir, f'{jobname}_{i+1}.jpg'))

def map_type(type):
  types = ['title', 'author', 'section', 'paragraph', 'table', 'figure', 'formula', 'footnote']
  return types.index(type)

def main():
  args = parse_args()

  os.makedirs(args.img_dir, exist_ok=True)
  os.makedirs(args.yolo_dir, exist_ok=True)
  os.makedirs(args.csv_dir, exist_ok=True)

  for tex in glob.glob(os.path.join(args.latex_dir, '*.tex')):
    jobname = os.path.basename(tex)[:-len('.tex')]

    pdf, pos = compile_latex(os.path.abspath(tex), args.latex_dir)
    if pdf is None:
        continue
    create_images_from_pdf(pdf, jobname, args.img_dir)
    create_annotation(pos, jobname, args.yolo_dir, args.csv_dir)
  
def parse_args():
  from argparse import ArgumentParser

  parser = ArgumentParser()
  parser.add_argument('--latex_dir',
                      dest='latex_dir',
                      help='latex files directory')
  parser.add_argument('--img_dir',
                      dest='img_dir',
                      help='output directory for PDF image')
  parser.add_argument('--yolo_dir',
                      dest='yolo_dir',
                      help='output directory for yolo annotation')
  parser.add_argument('--csv_dir',
                      dest='csv_dir',
                      help='output directory for csv files')               
  return parser.parse_args()

if __name__ == "__main__":
    main()

