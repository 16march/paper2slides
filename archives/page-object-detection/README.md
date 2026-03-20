# Page Object detection

## Documentation structure

The documentation of this project is divided into 5 parts:

* [Installing dependencies](#installing-dependencies)

* [Generation of dataset](#generation-of-dataset)

* [Separation of image into layers](#separation-of-image-into-layers)

* [Object detection using YOLOv3](#object-detection-using-yolov3)

* [Generating LaTeX](#generating-latex-from-images)

  

## Installing dependencies

  

1. Install the required python packages

    ```
    
    pip install -r requirements.txt
    
    ```
  

2. Install PDFLatex and some LaTeX packages for your operating system.
    
    It is usually included in TeX distribution.

    Download and install the appropriate version for your operating system [here](https://www.latex-project.org/get/)

    Make sure you can run ```pdflatex``` command from your terminal and can import these packages directly into a .tex file:
    ```
    \usepackage{trimclip}
    \usepackage{pgfplots}
    \usepackage{amsmath}
    \usepackage{zref-savepos}
    ```

3. Install poppler utils for your operating system [here](https://poppler.freedesktop.org/)

    Make sure you can run ```pdftoppm``` command from your terminal after poppler installation
  

4. Install [Google Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
    
    Make sure you can run ```tesseract``` command from your terminal after Google Tesseract OCR installation

  

## Generation of dataset

  
Generate latex dataset files using `generate_dataset.py`
The dataset contains generated LaTeX files.

**generate_dataset.py**

```

usage:

generate_dataset.py [-n] [--out_dir] [--start]

  

arguments:

-n number of latex files to be generated

--out_dir output directory for the latex files

--start Starting number (for resuming generation session) [Optional argument]

```

  

Generate 2500 latex dataset files (This will produce roughly around 10,000 - 15,000 images)

```

python generate_dataset.py -n 2500 --out_dir out_dir

```

  

Compile generated latex files and produce annotation using `compile_and_annotate_dataset.py`
This program compiles latex files in a directory and produces images of each page in each PDF with its annotation.

**compile_and_annotate_dataset.py**

```

usage:

compile_and_annotate_dataset.py [--latex_dir] [--img_dir] [--yolo_dir] [--csv_dir]

  

arguments:

--latex_dir latex files directory

--img_dir image directory

--yolo_dir output directory for yolo annotation

--csv_dir output directory for csv files

```

  

Compile and annotate the generated latex files

```

python compile_and_annotate_dataset.py --latex_dir latex_dir --img_dir img_dir --yolo_dir yolo_dir --csv_dir csv_dir

```

  

## Separation of image into layers

Use **preprocess_image.py** to separate an image into two layer (paragraph layer and non-paragraph layer)

```

usage:

preprocess_image.py [--img_dir] [--yolo_dir] [--img_out_dir] [--yolo_out_dir]

  

arguments:

--img_dir image directory (image needs to be a .jpg or .png images)

--yolo_dir yolo annotation directory

--img_out_dir output directory for image after preprocessing

--yolo_out_dir output directory for yolo annotation after preprecossing

```

  

Preprocess the dataset from previous step

```

python preprocess_image.py --img_dir img_dir --yolo_dir yolo_dir --img_out_dir img_out_dir --yolo_out_dir yolo_out_dir

```

  

## Object detection using YOLOv3

This part explains briefly how to install YOLOv3, train the dataset, test the detection, and evaluate the result.

For more detailed instruction on each part please refer to the original repository [https://github.com/AlexeyAB/darknet](https://github.com/AlexeyAB/darknet)

  

#### Installing YOLOv3

Clone YOLOv3 repository from [https://github.com/AlexeyAB/darknet](https://github.com/AlexeyAB/darknet)

Run `make` in the directory of YOLOv3 to compile the program

Refer to the page of [dependencies requirements](https://github.com/AlexeyAB/darknet#requirements) and [compilation options](https://github.com/AlexeyAB/darknet#how-to-compile-on-linux) for more detailed instruction

  

#### Training

1. Create `yolo-obj.cfg` file with the same content as in `yolov3.cfg` (copy *yolov3.cfg* and rename it to *yolo-obj.cfg*)

2. Modify these lines in `yolo-obj.cfg` to

* `batch=64`

* `subdivision=8`

* `max_batches=16000`

* `steps=12800, 14400`

* `classes=8`

* `filters=39`

3. Create `obj.names` file with object names - each in new line

**obj.names**

```

title

author

section

paragraph

table

figure

formula

footnote

```

4. Create `obj.data`, `train.txt`, and `valid.txt` files

**obj.data**

```

classes=8

train=train.txt

valid=valid.txt

names=obj.names

backup=backup/

```

***train.txt***

```

path/path/train_img1.jpg *path_to_training_img1*

path/path/train_img2.jpg *path_to_training_img2*

...

```

***valid.txt***

```

path/path/valid_img1.jpg *path_to_training_img1*

path/path/valid_img2.jpg *path_to_training_img2*

...

```

5. Download pre-trained weights from [https://pjreddie.com/media/files/darknet53.conv.74](https://pjreddie.com/media/files/darknet53.conv.74)

6. Start training by using the command

```

./darknet detector train obj.data yolo-obj.cfg darknet53.conv.74

```

#### Test detection

Test detection on a single image and show the output (It will prompt you to input the image path)

```

./darknet detector test obj.data yolo-obj.cfg backup/yolo-obj_###.weights

```

  

Test detection on multiple images and output prediction result for each image in yolo annotation format

```

./darknet detector test obj.data yolo-obj.cfg yolo-obj_###.weights -thresh 0.5 -dont_show -save_labels < list_of_images.txt

```

`list_of_images.txt` contains paths to the tested images (one path in each new line) similar to `train.txt` or `valid.txt`

  

#### mAP (mean average precision) evaluation

Calculate mAP

```

./darknet detector map obj.data yolo-obj.cfg yolo-obj_###.weights

```

  

## Generating LaTeX from images

Generate LaTeX file from prediction using `generate_latex.py`.
This program generates LaTeX files (in isolation for each object) from an image and an annotation.

**generate_latex.py**

```

usage:

generate_latex.py [--img] [--annotation] [--out_dir]

  

arguments:

--img Image of a page in a document

--annotation YOLO annotation file

--out_dir output directory

```

Generate LaTeX files from an image of a page in a document

```

python generate_latex.py --img img_path --annotation annotation_path --output_dir output_dir

```