import csv,io,json,math,collections,hashlib
from pathlib import Path
import zstandard
from download import digest
from analysis import stamp,iso,clean,episodes,summary,state
ROOT=Path(__file__).parent
def extract():
 config=json.loads((ROOT/'config.json').read_text());manifest=json.loads((ROOT/'data/source_manifest.json').read_text());raw=ROOT/'data/raw/ais-2024-01-01.csv.zst'
 if digest(raw)!=manifest['sha256']:raise ValueError('Archive digest mismatch')
 b=config['bounds'];points=[];quality=collections.Counter();fields=None
 with open(raw,'rb')as compressed,zstandard.ZstdDecompressor().stream_reader(compressed)as reader,io.TextIOWrapper(reader,encoding='utf-8-sig',newline='')as f:
  rows=csv.DictReader(f);fields=rows.fieldnames;print('Source schema:',fields,flush=True)
  for source in rows:
   quality['source_rows']+=1
   row={k.lower():v for k,v in source.items()}
   try:
    lat=float(row.get('lat',row.get('latitude','')));lon=float(row.get('lon',row.get('longitude','')))
    if not math.isfinite(lat)or not math.isfinite(lon)or not(-90<=lat<=90 and -180<=lon<=180):raise ValueError()
   except(ValueError,TypeError):quality['invalid_coordinates']+=1;continue
   if not(b['south']<=lat<=b['north']and b['west']<=lon<=b['east']):continue
   quality['area_rows']+=1
   try:typ=int(float(row.get('vesseltype',row.get('vessel_type',''))))
   except(ValueError,TypeError):quality['area_unknown_type']+=1;continue
   if not 70<=typ<=89:continue
   quality['commercial_area_rows']+=1
   try:
    vessel=row['mmsi'];speed=float(row['sog']);status=int(float(row['status']));time=iso(stamp(row.get('basedatetime',row.get('base_date_time',''))))
    if len(vessel)!=9 or not vessel.isdigit()or not math.isfinite(speed)or not 0<=speed<=config['max_speed_knots']or not 0<=status<=15 or not time.startswith(config['date']):raise ValueError()
   except(ValueError,TypeError,KeyError):quality['commercial_invalid_rows']+=1;continue
   points.append({'vessel':vessel,'time':time,'lat':lat,'lon':lon,'speed':speed,'status':status,'kind':'cargo'if typ<80 else'tanker'})
   if quality['source_rows']%1000000==0:print('Scanned',quality['source_rows'],flush=True)
 identifiers={v:f'V{i+1:03d}'for i,v in enumerate(sorted({p['vessel']for p in points}))}
 for p in points:p['vessel']=identifiers[p['vessel']]
 points,checks=clean(points);quality.update(checks);quality['accepted_reports']=len(points)
 out=ROOT/'points.csv'
 with open(out,'w',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=['vessel','time','lat','lon','speed','status','kind'],lineterminator='\n');w.writeheader();w.writerows(points)
 metadata={'source':manifest,'schema':fields,'quality':dict(quality),'config_sha256':digest(ROOT/'config.json')}
 (ROOT/'data/extraction.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n');return points

def load_points():
 with open(ROOT/'points.csv',encoding='utf-8')as f:return [{**r,'lat':float(r['lat']),'lon':float(r['lon']),'speed':float(r['speed']),'status':int(r['status'])}for r in csv.DictReader(f)]
def report(points):
 config=json.loads((ROOT/'config.json').read_text());events=episodes(points,gap_minutes=config['max_gap_minutes'],min_minutes=config['min_dwell_minutes'],speed_threshold=config['stationary_speed_knots'])
 for i,e in enumerate(events):e['id']=f'E{i+1:03d}'
 tracks=[]
 for v in sorted({p['vessel']for p in points}):
  rows=[p for p in points if p['vessel']==v];sample=[];last=None
  for p in rows:
   if last is None or stamp(p['time'])-stamp(last['time'])>=300 or p is rows[-1]:sample.append(p);last=p
  tracks.append({'vessel':v,'kind':rows[0]['kind'],'reports':len(rows),'first':rows[0]['time'],'last':rows[-1]['time'],'points':sample})
 sensitivity=[{'gap_minutes':g,**summary(episodes(points,gap_minutes=g))}for g in [5,15,30]]
 out={'schema_version':1,'config':config,'extraction':json.loads((ROOT/'data/extraction.json').read_text()),'points_sha256':digest(ROOT/'points.csv'),'summary':summary(events),'events':events,'tracks':tracks,'sensitivity':sensitivity}
 (ROOT/'report.json').write_text(json.dumps(out,separators=(',',':'),allow_nan=False)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps({'quality':out['extraction']['quality'],'summary':out['summary'],'vessels':len(tracks),'sensitivity':sensitivity},indent=2),flush=True)
if __name__=='__main__':
 import sys
 points=load_points()if '--from-points'in sys.argv else extract();report(points)
