import cv2
from ultralytics import YOLO

model = YOLO(r"C:\\Users\\Owner\\Documents\\Dev\\Capstone\\compute\\cv\\runs2\\content\\runs\\detect\\train\\weights\\best.pt")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open camera")

for _ in range(10):
    cap.read()

ret, frame = cap.read()
if not ret:
    raise RuntimeError("Failed to capture frame")

results = model(frame)

result = results[0]
boxes = result.boxes

print("Detections:")
for box in boxes:
    cls = int(box.cls[0])
    conf = float(box.conf[0])
    label = model.names[cls]

    print(f"{label} ({conf:.2f})")

cap.release()