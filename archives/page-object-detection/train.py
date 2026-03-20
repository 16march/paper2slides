from ultralytics import YOLO
import torch

# 检查一下 MPS 是否可用 (装个逼，确认一下 GPU 也就是 Metal 是否在线)
if torch.backends.mps.is_available():
    print("🚀 检测到 Apple M3 GPU (MPS 加速已开启)！")
    device = 'mps'
else:
    print("⚠️ 未检测到 MPS，正在使用 CPU (会很慢)...")
    device = 'cpu'

if __name__ == '__main__':
    # 1. 加载模型 (推荐用 Nano 版本，M3 跑这个飞快)
    model = YOLO('yolov8n.pt') 

    # 2. 开始训练
    model.train(
        data='my_yolo_dataset/data.yaml',
        epochs=50,           # 改回 50 轮，1000张图跑50轮足够收敛了
        imgsz=416,           # 【关键！】从 640 改成 416
        batch=32,            # 图片小了，batch 可以开大一点，利用率更高
        device='mps',
        name='exp_1k_416sz'  # 改个名
)