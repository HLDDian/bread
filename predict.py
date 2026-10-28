import argparse
from pathlib import Path
import torch
from ultralytics import YOLO

def find_latest_best_weights(base_dir: Path) -> Path:
    """自動尋找 runs/segment 中最新一次訓練產生的 best.pt"""
    segment_dir = base_dir / "runs" / "segment"
    if not segment_dir.exists():
        return None

    # 找出所有 train 開頭的資料夾並依照修改時間排序
    train_dirs = [d for d in segment_dir.iterdir() if d.is_dir() and d.name.startswith("train")]
    if not train_dirs:
        return None

    train_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)

    # 從最新的資料夾開始找 best.pt
    for d in train_dirs:
        best_pt = d / "weights" / "best.pt"
        if best_pt.exists():
            return best_pt
    return None

def main():
    parser = argparse.ArgumentParser(description="YOLOv8 實例分割預測腳本")
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="預測來源：圖片路徑、資料夾、影片檔或攝影機編號（預設優先找 test.jpg，若無則預測 YOLODataset/images/test）"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="模型權重路徑（預設自動尋找最新訓練的 runs/segment/train*/weights/best.pt）"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="信心分數門檻（預設 0.25）"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        default=True,
        help="是否儲存預測結果影像（預設儲存）"
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent

    # 1. 決定模型權重路徑
    if args.model:
        model_path = Path(args.model)
    else:
        model_path = find_latest_best_weights(base_dir)
        if model_path is None:
            # 備用路徑
            model_path = base_dir / "runs" / "segment" / "train" / "weights" / "best.pt"

    if not model_path.exists():
        print(f"錯誤：找不到模型權重檔 {model_path}")
        print("請確認訓練是否已完成，或手動指定 --model 參數，例如：")
        print("  python predict.py --model runs/segment/train/weights/best.pt")
        return

    print(f"已載入權重: {model_path}")

    # 2. 決定預測來源
    if args.source:
        source_path = args.source
    else:
        test_jpg = base_dir / "test.jpg"
        if test_jpg.exists():
            source_path = str(test_jpg)
        else:
            default_test_dir = base_dir / "YOLODataset" / "images" / "test"
            if default_test_dir.exists() and any(default_test_dir.iterdir()):
                source_path = str(default_test_dir)
            else:
                source_path = str(base_dir / "YOLODataset" / "images" / "val")

    print(f"預測來源: {source_path}")

    # 3. 自動適配運算裝置
    device = 0 if torch.cuda.is_available() else "cpu"

    # 4. 載入模型並進行推論
    model = YOLO(str(model_path))
    results = model.predict(
        source=source_path,
        conf=args.conf,
        device=device,
        save=args.save,
    )

    # 5. 解析並列印偵測結果
    print("\n--- 辨識結果摘要 ---")
    for idx, r in enumerate(results, start=1):
        filename = Path(r.path).name if hasattr(r, "path") else f"Image {idx}"
        print(f"\n[{filename}]")

        if r.masks is None or len(r.boxes) == 0:
            print("  - 沒有偵測到任何目標物件")
            continue

        for box in r.boxes:
            cls_id = int(box.cls[0])
            name = r.names.get(cls_id, str(cls_id))
            score = float(box.conf[0])
            print(f"  - {name}: {score:.2f} (信心度: {score*100:.1f}%)")

    print("\n完成！標註結果圖片已儲存在: runs/segment/predict/")

if __name__ == "__main__":
    main()

