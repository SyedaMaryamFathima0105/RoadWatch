"""Compute workflow metrics from reports and human-labeled duplicate groups."""
import argparse,csv,statistics,itertools
from datetime import datetime
p=argparse.ArgumentParser();p.add_argument('reports_csv',help='Columns: id, latitude, longitude, image_url, status, created_at, reviewed_at, duplicate_group');p.add_argument('--duplicate-labels',help='CSV columns: report_id, true_group');a=p.parse_args()
with open(a.reports_csv,newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
usable=sum(bool(r.get('image_url') and r.get('latitude') and r.get('longitude')) for r in rows); accepted=sum(r.get('status')=='ACCEPTED' for r in rows); durations=[]
for r in rows:
 try: durations.append((datetime.fromisoformat(r['reviewed_at'].replace('Z','+00:00'))-datetime.fromisoformat(r['created_at'].replace('Z','+00:00'))).total_seconds()/3600)
 except (ValueError,KeyError,TypeError): pass
print({'acceptance_rate':accepted/len(rows) if rows else None,'median_review_hours':statistics.median(durations) if durations else None,'usable_image_location_pct':100*usable/len(rows) if rows else None})
if a.duplicate_labels:
 with open(a.duplicate_labels,newline='',encoding='utf-8') as f: labels={r['report_id']:r['true_group'] for r in csv.DictReader(f)}
 predicted={r['id']:r.get('duplicate_group') or r['id'] for r in rows if r['id'] in labels}; ids=list(predicted);tp=fp=fn=0
 for x,y in itertools.combinations(ids,2):
  truth=labels[x]==labels[y];guess=predicted[x]==predicted[y]
  if truth and guess:tp+=1
  elif guess:fp+=1
  elif truth:fn+=1
 print({'duplicate_grouping_precision':tp/(tp+fp) if tp+fp else None,'duplicate_grouping_recall':tp/(tp+fn) if tp+fn else None,'labeled_pairs':len(ids)*(len(ids)-1)//2})
