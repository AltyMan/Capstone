import cv2
from ultralytics import YOLO
import numpy as np

# Load model
model = YOLO("C:\\Users\\Owner\\Documents\\Dev\\Capstone\\compute\\cv\\runs2\\content\\runs\\detect\\train\\weights\\best.pt")
model.predict(source=np.zeros((640, 640, 3), dtype=np.uint8), verbose=False)

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open camera")

# Warm up camera
for _ in range(10):
    cap.read()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run detection
    results = model(frame, stream=True)

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{label} {conf:.2f}",
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

    # Show frame continuously
    cv2.imshow("Object Detection", frame)

    # Press 'e' to exit
    if cv2.waitKey(1) & 0xFF == ord("e"):
        break

cap.release()
cv2.destroyAllWindows()