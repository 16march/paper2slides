from ultralytics import YOLO

model = YOLO('runs/detect/m3_air_training/weights/last.pt') 

# 强制使用 CPU
model.train(resume=True, device='cpu')