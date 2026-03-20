#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import cv2 as cv
import numpy as np

def separate_paragraph_regions(fname, jobname, yolo_dir, img_out_dir, yolo_out_dir):
  image = cv.imread(fname)
  regions, annotations = extract_paragraph_regions(image, fname, jobname, yolo_dir)

  paragraph_im = 255*np.ones_like(image)

  for region in regions:
    x, y, w, h, bb = region
    paragraph_im[y:y+h, x:x+w] = bb

  cv.imwrite(os.path.join(img_out_dir, f'{jobname}_p.jpg'), paragraph_im)

  paragraph_only = annotations.copy()

  for annotation in annotations:
    if map_type(int(annotation.split(' ')[0])) != 'paragraph':
      paragraph_only.remove(annotation)


  with open(os.path.join(yolo_out_dir, f'{jobname}_p.txt'), 'w') as f:
    f.writelines(paragraph_only)


def separate_non_paragraph_regions(fname, jobname, yolo_dir, img_out_dir, yolo_out_dir):
  image = cv.imread(fname)
  regions, annotations = extract_non_paragraph_regions(image, fname, jobname, yolo_dir)

  for region in regions:
    x, y, w, h, bb = region
    image[y:y+h, x:x+w] = bb

  cv.imwrite(os.path.join(img_out_dir, f'{jobname}_np.jpg'), image)

  no_paragraph = annotations.copy()

  for annotation in annotations:
    if map_type(int(annotation.split(' ')[0])) == 'paragraph':
      no_paragraph.remove(annotation)

  with open(os.path.join(yolo_out_dir, f'{jobname}_np.txt'), 'w') as f:
    f.writelines(no_paragraph)

def extract_paragraph_regions(image, fname, jobname, yolo_dir):
  contours = []

  with open(os.path.join(yolo_dir, f'{jobname}.txt')) as f:
    boxes = f.readlines()

  height, width, _ = image.shape
  for box in boxes:
    type, x_yolo, y_yolo, width_yolo, height_yolo = list(map(lambda x: float(x), box.split(' ')))
    if type == 3:
      x = round((x_yolo - 0.5*width_yolo) * width)
      y = round((y_yolo - 0.5*height_yolo) * height)
      w = round(width_yolo * width)
      h = round(height_yolo * height)
      bb = image[y:y + h, x: x + w]
      contours.append((x,y,w,h,bb))

  return contours, boxes

def extract_non_paragraph_regions(image, fname, jobname, yolo_dir):
  contours = []

  with open(os.path.join(yolo_dir, f'{jobname}.txt')) as f:
    boxes = f.readlines()

  height, width, _ = image.shape
  for box in boxes:
    type, x_yolo, y_yolo, width_yolo, height_yolo = list(map(lambda x: float(x), box.split(' ')))
    if type == 3:
      x = round((x_yolo - 0.5*width_yolo) * width)
      y = round((y_yolo - 0.5*height_yolo) * height)
      w = round(width_yolo * width)
      h = round(height_yolo * height)
      bb = 255*np.ones_like(image[y:y + h, x: x + w])
      contours.append((x,y,w,h,bb))

  return contours, boxes

def map_type(index):
  types = ['title', 'author', 'section', 'paragraph', 'table', 'figure', 'formula', 'footnote']
  return types[index]

def main():
  args = parse_args()

  os.makedirs(args.img_out_dir, exist_ok=True)
  os.makedirs(args.yolo_out_dir, exist_ok=True)

  types = ('*.jpg', '*.png')
  fnames = []
  for type in types:
    fnames.extend(glob.glob(os.path.join(args.img_dir, type)))
  
  for fname in fnames:
    jobname = os.path.basename(fname)[:-len('.jpg')]
    separate_paragraph_regions(fname, jobname, args.yolo_dir, args.img_out_dir, args.yolo_out_dir)
    separate_non_paragraph_regions(fname, jobname, args.yolo_dir, args.img_out_dir, args.yolo_out_dir)
  
def parse_args():
  from argparse import ArgumentParser

  parser = ArgumentParser()
  parser.add_argument('--img_dir',
                      dest='img_dir',
                      help='image directory')
  parser.add_argument('--yolo_dir',
                      dest='yolo_dir',
                      help='yolo annotation directory')
  parser.add_argument('--img_out_dir',
                      dest='img_out_dir',
                      help='output directory for image after preprocessing')
  parser.add_argument('--yolo_out_dir',
                      dest='yolo_out_dir',
                      help='output directory for yolo_annotation after preprocessing')               
  return parser.parse_args()

if __name__ == "__main__":
    main()