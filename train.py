from pathlib import Path
import torch
from ultralytics import YOLO

def main():
    # 自動偵測是否有 NVIDIA CUDA 顯示卡，若無則使用 CPU
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"使用的運算裝置: {device}")

    # 取得 dataset.yaml 的絕對路徑
    base_dir = Path(__file__).resolve().parent
    dataset_yaml = base_dir / "YOLODataset" / "dataset.yaml"

    if not dataset_yaml.exists():
        raise FileNotFoundError(f"找不到資料集設定檔: {dataset_yaml}")

    # 載入 YOLOv8 分割預訓練模型
    model = YOLO("yolov8n-seg.pt")

    # 開始訓練
    model.train(
        data=str(dataset_yaml),
        epochs=200,          # 訓練輪數（有早停機制，表現不再提升會提前結束）
        imgsz=640,           # 影像尺寸
        batch=4,             # 批次大小（小型資料集建議設為 4）
        device=device,       # 自動選用 cpu 或 cuda:0
        workers=0,           # Windows 環境下設定為 0 避免多執行緒 I/O 卡死
        plots=True,          # 自動繪製訓練評估圖表
    )

if __name__ == "__main__":
    main()

