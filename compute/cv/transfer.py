# 1) Install dependencies
# pip install ultralytics

from ultralytics import YOLO
import yaml

# 2) Create YOLO dataset config (data.yaml)
data = {
    'train': 'cv/dataset/images/train',
    'val': 'cv/dataset/images/val',
    'names': ['bed']
}

with open('data.yaml', 'w') as f:
    yaml.dump(data, f)

# 3) Load pretrained model
model = YOLO("yolov8n.yaml")  # lightweight but effective

# 4) Train on your dataset
model.train(
    data="data.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
    pretrained=True,
)

# 5) Evaluate
results = model.val()
print(results)
