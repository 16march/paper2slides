from ultralytics import YOLO

if __name__ == '__main__':
    print("🚀 正在启动 CPU 极速模式...")
    model = YOLO('yolov8n.pt') 

    model.train(
        data='my_yolo_dataset/data.yaml',
        epochs=20,              # 20轮足够证明实验效果了！
        imgsz=416,              # 保持 416
        batch=16,               # CPU 内存管够，开 16 没问题
        device='cpu',           # 【关键】切换到 CPU
        workers=4,              # 【关键】利用 M3 的多核 CPU 加速
        val=False,              # 训练时不验证，极致提速
        name='cpu_run_final'
    )
    
    print("✅ 训练完成！正在验证...")
    metrics = model.val(split='val', imgsz=416, device='cpu')
    print(f"最终 mAP50: {metrics.box.map50}")