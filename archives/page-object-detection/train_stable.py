from ultralytics import YOLO
import torch

# 强制清理一下显存缓存（玄学，但有用）
if torch.backends.mps.is_available():
    torch.cuda.empty_cache()

if __name__ == '__main__':
    # 1. 加载模型
    model = YOLO('yolov8n.pt') 

    # 2. 开始训练 (稳定版配置)
    model.train(
        data='my_yolo_dataset/data.yaml',
        epochs=50,              # 1000张图跑50轮足够收敛了，不用100
        imgsz=416,              # 【核心修复】降回学长论文的尺寸，大幅提速且防崩
        batch=8,                # 【核心修复】调小Batch，防止 Tensor Shape Mismatch
        device='mps',           # 继续用 M3 加速
        workers=0,              # Mac上设为0最稳，防止多进程死锁
        val=False,              # 【提速神器】训练时不浪费时间做验证
        name='stable_run_416'   # 结果保存在 runs/detect/stable_run_416
    )
    
    print("✅ 训练完成！现在开始验证...")
    
    # 3. 训练完后再单独验证一次 (这样就算崩了，模型也已经保存了)
    metrics = model.val(split='val', imgsz=416, device='mps')
    print(f"最终 mAP50: {metrics.box.map50}")