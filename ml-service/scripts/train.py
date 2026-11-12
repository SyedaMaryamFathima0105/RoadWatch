from ultralytics import YOLO
model=YOLO('yolov8n.pt')
model.train(data='data/roadwatch.yaml', imgsz=640, epochs=30, project='runs/roadwatch', name='train')
best='runs/roadwatch/train/weights/best.pt'
import shutil, pathlib
pathlib.Path('models').mkdir(exist_ok=True);shutil.copy2(best,'models/best.pt')
