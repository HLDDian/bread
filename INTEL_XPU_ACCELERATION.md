# Intel 內顯（iGPU / XPU）加速 YOLO 備忘指南

這份文件記錄如何在配備 **Intel Core Ultra（如 Core Ultra 7 255H / Meteor Lake 架構）** 或配備 **Intel Arc / Iris Xe 內顯（iGPU）** 的電腦上，利用內建顯卡加速 YOLO 辨識與推論。

---

## 核心結論

| 任務類型 | 推薦方案 | 難易度 | 效果 |
| :--- | :--- | :--- | :--- |
| **推論 / 預測 (Inference)** | **OpenVINO + iGPU (`device='GPU'`)** | ⭐ 超簡單（極力推薦） | 速度比純 CPU 快數倍至十倍，吃滿 Intel Arc 內顯 |
| **模型訓練 (Training)** | **Intel Extension for PyTorch (IPEX)** | ⭐⭐⭐ 較繁瑣 | 需配置 oneAPI / IPEX，Windows+Py3.12 支援較複雜，建議大模型用雲端 GPU |

---

## 方案一：推論與辨識加速（使用 OpenVINO）

Ultralytics 原生深度整合了 Intel OpenVINO™，不需要改寫大幅程式碼，只需兩步即可直接啟用 Intel 內顯。

### 步驟 1：安裝 OpenVINO

在專案的虛擬環境中安裝：
```powershell
pip install openvino
```

### 步驟 2：匯出模型為 OpenVINO 格式

將你訓練好（或預訓練）的模型權重（`.pt`）轉成 OpenVINO 格式：
```powershell
# 指令列方式
yolo export model=yolov8n.pt format=openvino

# 或是你訓練好的權重
yolo export model=runs/segment/train/weights/best.pt format=openvino
```
> 匯出成功後，目錄下會生成一個 `best_openvino_model/` 或 `yolov8n_openvino_model/` 資料夾。

### 步驟 3：使用 Intel 內顯執行推論

OpenVINO 會將 Intel Arc 內顯識別為 `GPU`（若有 NPU 也可嘗試 `NPU`）。

#### 方式 A：命令列（CLI）
```powershell
# 辨識圖片或攝影機（0 為預設攝影機）
yolo predict model=yolov8n_openvino_model device=GPU source=0
```

#### 方式 B：Python 程式碼
```python
from ultralytics import YOLO

# 載入轉換後的 OpenVINO 模型目錄
model = YOLO("yolov8n_openvino_model")

# 指定 device="GPU"（OpenVINO 中的 Intel 內顯）
results = model.predict(source="0", device="GPU", show=True)
```

---

## 方案二：模型訓練加速（使用 Intel XPU / IPEX）

若想在本地利用 Intel 內顯進行模型訓練：

1. **技術架構**：
   - 需安裝 **Intel Extension for PyTorch (IPEX)**。
   - 程式碼或指令中指定 `device='xpu'`。

2. **Windows 平台注意事項**：
   - Intel 官方的 IPEX 對 Linux 的支援度最好。
   - 在 Windows 上搭配 Python 3.12 需確認是否有對應的預編譯 wheel 檔或 Intel oneAPI Base Toolkit。
   - **建議**：如果只是小型資料集練習，可直接用 CPU 跑；如需大規模訓練，建議上傳至 Google Colab（免費提供 T4 GPU）進行訓練，訓練完成後把 `best.pt` 下載回本地，再用**方案一（OpenVINO）**在本地順暢推論。

