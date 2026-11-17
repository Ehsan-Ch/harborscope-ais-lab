"""Recompute all episodes and sensitivity statistics from the retained point CSV."""
import json,math
from pathlib import Path
from download import digest
from build import load_points
from analysis import episodes,summary
def reconcile(a,b,path='root'):
 if isinstance(a,float)or isinstance(b,float):
  assert isinstance(a,(int,float))and isinstance(b,(int,float))and math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9),path
 elif isinstance(a,dict):
  assert isinstance(b,dict)and a.keys()==b.keys(),path
  for k in a:reconcile(a[k],b[k],path+'.'+k)
 elif isinstance(a,list):
  assert isinstance(b,list)and len(a)==len(b),path
  for i,(x,y)in enumerate(zip(a,b)):reconcile(x,y,path+f'[{i}]')
 else:assert a==b,path
root=Path(__file__).parent;r=json.loads((root/'report.json').read_text())
assert digest(root/'points.csv')==r['points_sha256'];assert digest(root/'config.json')==r['extraction']['config_sha256']
assert json.loads((root/'data/source_manifest.json').read_text())==r['extraction']['source']
points=load_points();c=r['config'];expected=episodes(points,gap_minutes=c['max_gap_minutes'],min_minutes=c['min_dwell_minutes'],speed_threshold=c['stationary_speed_knots'])
for i,e in enumerate(expected):e['id']=f'E{i+1:03d}'
reconcile(expected,r['events']);reconcile(summary(expected),r['summary'])
assert len(points)==r['extraction']['quality']['accepted_reports']
for s in r['sensitivity']:reconcile(summary(episodes(points,gap_minutes=s['gap_minutes'])),{k:v for k,v in s.items()if k!='gap_minutes'})
assert len({(p['vessel'],p['time'])for p in points})==len(points)
assert all(c['bounds']['south']<=p['lat']<=c['bounds']['north']and c['bounds']['west']<=p['lon']<=c['bounds']['east']for p in points)
assert sum(t['reports']for t in r['tracks'])==len(points)
print(f"Reconciled {len(points):,} reports, {len(expected)} episodes, all sensitivity summaries and integrity pins.")
