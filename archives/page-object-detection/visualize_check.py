import cv2
import os

# 你的文件路径（根据你的截图修改）
img_path = 'img_dir/latex_dataset0_2.jpg'  # 假设图片是jpg，也可能是png
label_path = 'yolo_dir/latex_dataset0_2.txt'

# 类别名字（为了看清楚写的是啥）
classes = ['title', 'author', 'section', 'paragraph', 'table', 'figure', 'formula', 'footnote']

# 读取图片
image = cv2.imread(img_path)
h, w, _ = image.shape

# 读取标注文件
with open(label_path, 'r') as f:
    lines = f.readlines()

for line in lines:
    parts = line.strip().split()
    class_id = int(parts[0])
    x_center, y_center, width, height = map(float, parts[1:])

    # 把 0-1 的小数还原回像素坐标
    x_c, y_c = x_center * w, y_center * h
    box_w, box_h = width * w, height * h
    
    # 计算左上角和右下角坐标
    x1 = int(x_c - box_w / 2)
    y1 = int(y_c - box_h / 2)
    x2 = int(x_c + box_w / 2)
    y2 = int(y_c + box_h / 2)

    # 画框 (绿色)
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # 写字
    cv2.putText(image, classes[class_id], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# 显示图片
cv2.imshow('Check Data', image)
cv2.waitKey(0)
cv2.destroyAllWindows()