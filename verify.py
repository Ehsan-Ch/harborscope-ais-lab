"""Recompute all episodes and sensitivity statistics from the retained point CSV."""
import json
from pathlib import Path
from download import digest
from build import load_points
from analysis import episodes,summary
root=Path(__file__).parent;r=json.loads((root/'report.json').read_text())
assert digest(root/'points.csv')==r['points_sha256'];assert digest(root/'config.json')==r['extraction']['config_sha256']
assert json.loads((root/'data/source_manifest.json').read_text())==r['extraction']['source']
points=load_points();c=r['config'];expected=episodes(points,gap_minutes=c['max_gap_minutes'],min_minutes=c['min_dwell_minutes'],speed_threshold=c['stationary_speed_knots'])
for i,e in enumerate(expected):e['id']=f'E{i+1:03d}'
assert expected==r['events'];assert summary(expected)==r['summary']
assert len(points)==r['extraction']['quality']['accepted_reports']
for s in r['sensitivity']:assert summary(episodes(points,gap_minutes=s['gap_minutes']))=={k:v for k,v in s.items()if k!='gap_minutes'}
assert len({(p['vessel'],p['time'])for p in points})==len(points)
assert all(c['bounds']['south']<=p['lat']<=c['bounds']['north']and c['bounds']['west']<=p['lon']<=c['bounds']['east']for p in points)
assert sum(t['reports']for t in r['tracks'])==len(points)
print(f"Reconciled {len(points):,} reports, {len(expected)} episodes, all sensitivity summaries and integrity pins.")
