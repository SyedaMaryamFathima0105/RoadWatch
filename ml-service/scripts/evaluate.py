import argparse
from ultralytics import YOLO
p=argparse.ArgumentParser();p.add_argument('--weights',default='models/best.pt');p.add_argument('--data',default='data/roadwatch.yaml');a=p.parse_args()
m=YOLO(a.weights);r=m.val(data=a.data,split='test',imgsz=640,plots=True)
print(f'mAP@0.5: {r.box.map50:.4f}\nmAP@0.5:0.95: {r.box.map:.4f}')
for i,name in m.names.items(): print(f'{name}: precision={r.box.p[i]:.4f}, recall={r.box.r[i]:.4f}')
print('Confusion matrix:',r.confusion_matrix.matrix.tolist())
