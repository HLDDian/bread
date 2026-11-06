**YOLOv8 實例分割實作教學**

# 步驟 1　安裝 Python

## 1-1　下載安裝程式

開啟 <https://www.python.org/downloads/> ，下載 Windows installer（64-bit）。建議安裝 Python 3.12，這兩個版本與 PyTorch、OpenCV 等套件的相容性最穩定。

## 1-2　執行安裝

1. 雙擊下載的安裝檔。
2. 在第一個畫面最下方勾選 Add python.exe to PATH。
3. 點選 Install Now，等待安裝完成後按 Close。

沒有勾選 Add python.exe to PATH 的話，命令列會找不到 python 指令。遇到這種情況，重新執行安裝程式並勾選該選項即可。

## 1-3　確認安裝結果

按 Win + R，輸入 cmd或powershell 後按 Enter，開啟命令提示字元，執行下列指令：

python --version

pip --version

兩個指令都顯示版本號就表示安裝成功。macOS 與 Linux 請改用 python3 與 pip3。

# 步驟 2　建立虛擬環境

虛擬環境是專案專用的獨立 Python 環境，套件只裝在專案資料夾內，不會影響系統其他程式使用的 Python。

先新增一個新的專案資料夾

## 2-1　建立虛擬環境

```bash
python -m venv venv
```

執行後專案資料夾內會出現 venv 資料夾，裡面有一份獨立的 Python 與 pip。

## 2-2　啟動虛擬環境

依使用的命令列選擇對應指令：

| **命令列**          | **啟動指令**             |
| ------------------- | ------------------------ |
| 命令提示字元（cmd） | venv\\Scripts\\activate  |
| PowerShell          | venv\\Scripts\\activate  |
| macOS / Linux       | source venv/bin/activate |

啟動成功後，命令列最前面會出現 (venv)。

PowerShell 若出現「已停用指令碼執行」的錯誤，先執行 Set-ExecutionPolicy -Scope CurrentUser RemoteSigned，輸入 Y 確認，再重新啟動虛擬環境。

## 2-4　升級 pip

python -m pip install --upgrade pip

(第一次)進入虛擬環境時需執行上述指令，更新pip版本

## 2-5 小結

之後每次開啟新的命令列視窗，都要先進入專案資料夾並啟動虛擬環境，才能執行後面的指令。工作結束時，輸入 deactivate 即可離開虛擬環境。

# 步驟 3　安裝套件

## 3-1　安裝 ultralytics、labelme、labelme2yolo

確認命令列開頭有 (venv) 後，執行：

pip install ultralytics labelme labelme2yolo

ultralytics (YOLO主程式)會一併安裝 PyTorch、OpenCV 等相依套件，下載量大，需要數分鐘。

使用labelme進行影像資料標註，產生json檔

再用labelme2yolo對json進行轉檔，產生YOLO可用的txt檔

## 3-2　驗證安裝

yolo checks

labelme --version

labelme2yolo --help

yolo checks 會列出 Ultralytics、Python、PyTorch 的版本，以及是否偵測到 GPU。後兩個指令能印出版本與說明，表示 labelme 與 labelme2yolo 可以使用。

## 3-3　使用 NVIDIA 顯卡訓練（選用）

Windows 上用 pip 安裝的 PyTorch 預設是 CPU 版。

以下指令檢查torch上面的CUDA是否有效

(電腦有 NVIDIA 顯卡時，先檢查 PyTorch 能否使用NVIDIA GPU)

python -c "import torch; print(torch.cuda.is_available())"

沒有獨立顯卡只能用 CPU 訓練，速度較慢，小型示範資料集仍可完成。

若要使用 NVIDIA 顯卡訓練就得先將(剛才裝好)的torch、torchvision、torchaudio解除安裝(指令如下)

pip uninstall torch torchvision torchaudio -y

再重新安裝新的torch (安裝指令由以下網站產生)

到 [pytorch.org](https://pytorch.org/) 的 Get Started 頁面，選擇對應的 CUDA 版本(下載時要對應NVIDIA顯示卡版本)，複製頁面產生的 pip 指令，重新安裝 torch 與 torchvision。

# 步驟 4　使用 Labelme 標註資料

## 4-1　準備圖片

在專案資料夾內建立dataset資料夾，放入要標註的圖片（jpg 或 png）。檔名建議只用英文與數字，避免空白與特殊符號。

## 4-2　開啟 Labelme 並指定(載入)資料夾

1. 在已啟動虛擬環境的命令列執行：

labelme

1. 點選左上角 Open Dir，選擇 dataset 資料夾。
2. 開啟 File 選單，勾選 Save Automatically。
3. 之後切換圖片時會自動存檔 (會自動存成json檔) 。

## 4-3　繪製多邊形標註

1. 開始標記影像資料。
2. 點選左側工具列的 Create Polygons（快捷鍵 Ctrl + N）。
3. 沿著物件邊緣依序點擊，點回第一個點即完成閉合。
4. 在彈出的視窗輸入類別名稱，按 OK。
5. 按鍵盤 D 切換到下一張，按 A 回到上一張。

同一張圖片有多個物件時，每個物件各畫一個多邊形。物件被遮擋時，只標出看得到的部分。類別名稱在所有圖片中必須完全相同，包含大小寫，建議使用英文小寫，例如 cat。

## 4-4　確認標註結果

全部標完後，開啟 dataset 資料夾，每張圖片旁邊都應該有一個同名的 .json 檔，例如 img001.jpg 對應 img001.json。缺少 json 的圖片代表漏標。

# 步驟 5　將 JSON 轉成 YOLO 的 txt

## 5-1　執行轉換

回到命令列（虛擬環境已啟動，位置在專案資料夾），執行：

labelme2yolo --json_dir dataset --val_size 0.2 --test_size 0.1 --output_format polygon --output_dir YOLODataset

需要重新轉換時，先刪除以下5-2圖上的7個資料夾。

## 5-2　檢查輸出結構

轉換完成後，bread 內會多出 YOLODataset 資料夾：

YOLODataset/

├── images/train/

├── images/val/

├── images/test/

├── labels/train/

├── labels/val/

├──labels/test/

└──dataset.yaml

## 5-3　檢查 txt 內容

開啟 labels/train 內任一個 txt。每一行代表一個物件，第一個數字是類別編號（從 0 開始），後面是成對的 x、y 座標，數值已正規化到 0 到 1 之間：

0 0.412 0.305 0.438 0.311 0.451 0.342 0.447 0.380 ...

## 5-4　檢查 dataset.yaml

用文字編輯器開啟 dataset.yaml，確認訓練集、驗證集的資料夾位置與類別名稱都正確。路徑有誤時，可改成下列格式，path 填 YOLODataset 的絕對路徑，Windows 也使用正斜線：

path: D:/bread/YOLODataset

train: images/train

val: images/val

test: images/test

names:

0: Bread

1: Croissant

2: Hambuger

3: Toast

4: Sandwich

5: RoundBread

names 的類別順序沿用轉換後產生的 dataset.yaml，不要自行調換，否則編號會和 labels 內的 txt 對不上。

# 步驟 6　使用 yolov8-seg 訓練模型

## 6-1　用(CMD或Powershell底下)下指令訓練

yolo segment train data=YOLODataset/dataset.yaml model=yolov8n-seg.pt epochs=200 imgsz=640 batch=8 device=0

第一次執行時，Ultralytics 會自動下載預訓練權重 yolov8n-seg.pt(遷移式學習)，需要連上網路。

## 會，在你這條 YOLOv8 Segmentation 訓練指令中，圖片 Resize 時，標註檔中的座標也會同步對應調整，不需要你手動修改 .txt 標註檔

## 6-2　用 Python(程式) 腳本訓練

在專案資料夾建立 train.py，內容如下：

from ultralytics import YOLO

def main():

model = YOLO("yolov8n-seg.pt")

model.train(

data="dataset/YOLODataset/dataset.yaml",

epochs=100,

imgsz=640,

batch=4,

device=0,

)

if \__name__ == "\__main_\_":

main()

先進入虛擬環境，在cmd執行 python train.py 開始訓練。Windows 上的資料讀取會啟動子行程，所以訓練程式必須放在 if \__name__ == "\__main_\_": 之下。

## 6-3　常用參數

| **參數** | **作用**             | **建議值**                                |
| -------- | -------------------- | ----------------------------------------- |
| data     | 資料集設定檔路徑     | dataset/YOLODataset/dataset.yaml          |
| model    | 起始權重             | yolov8n-seg.pt                            |
| epochs   | 訓練輪數             | 小型資料集可從 100 開始，再依驗證曲線調整 |
| imgsz    | 輸入影像邊長（像素） | 640                                       |
| batch    | 每批處理的影像數     | 8 或 16，記憶體不足時調小                 |
| device   | 運算裝置             | 0 使用第一張 GPU，cpu 使用 CPU            |

分割模型依大小分為 yolov8n-seg、yolov8s-seg、yolov8m-seg、yolov8l-seg、yolov8x-seg。模型越大，準確度越高，訓練也越慢。小型資料集和教學示範從 n 或 s 開始即可。

## 6-4　觀察訓練過程

終端機會在每個 epoch 結束後顯示驗證結果，欄位分成 Box 與 Mask 兩組，各自有 P、R、mAP50、mAP50-95。分割任務以 Mask 這一組為準，數值越接近 1 越好。

## 6-5　訓練輸出

訓練結果存放在 runs/segment/train/：

| **檔案**                 | **內容**                                 |
| ------------------------ | ---------------------------------------- |
| weights/best.pt          | 驗證集表現最好的權重，預測時使用這個檔案 |
| weights/last.pt          | 最後一個 epoch 的權重                    |
| results.png、results.csv | 損失與指標的變化曲線與數據               |
| confusion_matrix.png     | 各類別的混淆矩陣                         |
| val_batch0_pred.jpg 等   | 驗證圖片的預測結果，用來目視檢查         |

同一專案再次訓練時，輸出資料夾會依序變成 train2、train3。預測時要改用最新資料夾內的 best.pt，也可以在訓練時加上 name=my_seg 自訂資料夾名稱。

# 步驟 7　使用訓練好的權重預測圖片

## 7-1　準備測試圖片

將要預測的圖片放進專案資料夾，本教材以 test.jpg 為例。建議使用訓練時沒有出現過的圖片，才能看出模型對新圖片的表現。

## 7-2　用指令預測

yolo segment predict model=runs/segment/train/weights/best.pt source=test.jpg conf=0.25 save=True

結果圖存放在 runs/segment/predict/，圖上會疊加遮罩、外框、類別名稱與信心分數。conf=0.25 是信心分數門檻，低於這個值的偵測結果會被捨棄。

## 7-3　用 Python 腳本預測

在專案資料夾建立 predict.py：

from ultralytics import YOLO

model = YOLO("runs/segment/train/weights/best.pt")

results = model.predict(source="test.jpg", conf=0.25, save=True)

for r in results:

if r.masks is None:

print("沒有偵測到物件")

continue

for box in r.boxes:

name = r.names\[int(box.cls\[0\])\]

score = float(box.conf\[0\])

print(f"{name}: {score:.2f}")

執行 python predict.py，終端機會印出每個偵測到的類別與信心分數，結果圖同樣存到 runs/segment/predict/。source 也可以填資料夾路徑或影片檔，一次處理多張圖片或整支影片。每個物件的輪廓座標可以從 r.masks.xy 取得，單位是像素。

# 常見問題

| **狀況**                                          | **處理方式**                                                                                      |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| PowerShell 啟動虛擬環境時顯示「已停用指令碼執行」 | 執行 Set-ExecutionPolicy -Scope CurrentUser RemoteSigned，再重新啟動虛擬環境。                    |
| 找不到 yolo 或 labelme 指令                       | 虛擬環境可能沒有啟動。確認命令列開頭有 (venv)，必要時重新執行 pip install。                       |
| labels 內的 txt 每行只有 5 個數字                 | 轉換時漏了 --output_format polygon。刪除 YOLODataset 後重新轉換。                                 |
| 訓練時找不到影像或標籤                            | 檢查 dataset.yaml 的 path、train、val 是否指向實際存在的資料夾。                                  |
| 訓練時記憶體不足                                  | 調小 batch 或 imgsz，或改用較小的模型 yolov8n-seg。                                               |
| Windows 訓練時出現資料讀取（DataLoader）錯誤      | 加上 workers=0，並確認 Python 腳本使用了 if \__name__ == "\__main_\_":。                          |
| 找不到 best.pt                                    | 到 runs/segment 查看最新的 train 資料夾，重複訓練後名稱會變成 train2、train3。                    |
| 預測結果沒有任何遮罩                              | 把 conf 降到 0.1 再試。仍然沒有結果時，檢查訓練資料量、標註品質，以及測試圖片是否與訓練圖片相近。 |