"""Convert RDD2022 VOC annotations into deterministic YOLO train/val/test splits."""
import argparse, random, shutil
from pathlib import Path
import xml.etree.ElementTree as ET
CLASSES = ['longitudinal_crack','transverse_crack','alligator_crack','pothole']
# RDD2022 VOC source labels. Explicit names are also accepted for curated exports.
SOURCE_LABELS = {'d00':'longitudinal_crack','d10':'transverse_crack','d20':'alligator_crack','d40':'pothole', **{n:n for n in CLASSES}}
def convert(xml: Path, out: Path):
    root=ET.parse(xml).getroot(); size=root.find('size'); w=float(size.findtext('width')); h=float(size.findtext('height')); rows=[]
    for obj in root.findall('object'):
        label=SOURCE_LABELS.get(obj.findtext('name','').strip().lower())
        if label not in CLASSES: continue
        b=obj.find('bndbox'); x1,y1,x2,y2=[float(b.findtext(k)) for k in ('xmin','ymin','xmax','ymax')]
        rows.append(f"{CLASSES.index(label)} {(x1+x2)/(2*w):.6f} {(y1+y2)/(2*h):.6f} {(x2-x1)/w:.6f} {(y2-y1)/h:.6f}")
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text('\n'.join(rows)+'\n' if rows else '',encoding='utf-8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--images',required=True);p.add_argument('--annotations',required=True);p.add_argument('--output',default='data/roadwatch');p.add_argument('--seed',type=int,default=42);a=p.parse_args()
    images=Path(a.images); anns=Path(a.annotations); pairs=[]
    image_index={p.stem.lower():p for p in images.rglob('*') if p.suffix.lower() in {'.jpg','.jpeg','.png'}}
    for xml in anns.rglob('*.xml'):
        image=image_index.get(xml.stem.lower())
        if image:pairs.append((image,xml))
    random.Random(a.seed).shuffle(pairs);n=len(pairs); splits={'train':pairs[:int(.7*n)],'val':pairs[int(.7*n):int(.85*n)],'test':pairs[int(.85*n):]};root=Path(a.output)
    for split,items in splits.items():
        for image,xml in items:
            target=root/'images'/split/image.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(image,target);convert(xml,root/'labels'/split/f'{image.stem}.txt')
    yaml='path: '+str(root.resolve()).replace('\\','/')+'\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n'+''.join(f'  {i}: {name}\n' for i,name in enumerate(CLASSES))
    Path('data').mkdir(exist_ok=True);Path('data/roadwatch.yaml').write_text(yaml,encoding='utf-8');print({k:len(v) for k,v in splits.items()})
if __name__=='__main__':main()
