"""Observed dwell episodes; never infer unobserved time across coverage gaps."""
import math
from datetime import datetime,timezone

def stamp(value):
 d=datetime.fromisoformat(value.replace('Z','+00:00'))
 if d.tzinfo is None:d=d.replace(tzinfo=timezone.utc)
 return d.timestamp()
def iso(value):return datetime.fromtimestamp(value,timezone.utc).isoformat().replace('+00:00','Z')
def distance(a,b):
 lat1,lat2=map(math.radians,[a['lat'],b['lat']]);dlat=lat2-lat1;dlon=math.radians(b['lon']-a['lon']);h=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
 return 6371000*2*math.asin(math.sqrt(min(1,max(0,h))))
def state(p,threshold=.5):
 if p['speed']>threshold:return 'moving'
 return {1:'reported_anchor',5:'reported_moored'}.get(p['status'],'other_stationary')
def clean(points):
 """Reject all observations at conflicting vessel/timestamps; identical duplicates keep one."""
 groups={};duplicate=conflict=0
 for p in points:groups.setdefault((p['vessel'],p['time']),[]).append(p)
 output=[]
 for rows in groups.values():
  signatures={(p['lat'],p['lon'],p['speed'],p['status'],p['kind'])for p in rows}
  if len(signatures)>1:conflict+=len(rows)
  else:duplicate+=len(rows)-1;output.append(rows[0])
 return sorted(output,key=lambda p:(p['vessel'],p['time'])),{'identical_duplicates_removed':duplicate,'conflicting_rows_rejected':conflict}

def episodes(points,gap_minutes=15,min_minutes=20,speed_threshold=.5,radius_m=500):
 if gap_minutes<=0 or min_minutes<0 or speed_threshold<0 or radius_m<=0:raise ValueError('Invalid segmentation parameter')
 result=[];run=[];start_reason='observation_boundary'
 def finish(reason):
  if len(run)>=2:
   minutes=(stamp(run[-1]['time'])-stamp(run[0]['time']))/60
   if minutes>=min_minutes:result.append({'vessel':run[0]['vessel'],'kind':run[0]['kind'],'state':state(run[0],speed_threshold),'start':run[0]['time'],'end':run[-1]['time'],'minutes':minutes,'reports':len(run),'lat':sum(p['lat']for p in run)/len(run),'lon':sum(p['lon']for p in run)/len(run),'start_reason':start_reason,'end_reason':reason})
 previous=None
 for p in sorted(points,key=lambda p:(p['vessel'],p['time'])):
  reason=None
  if previous is not None:
   if p['vessel']!=previous['vessel']:reason='observation_boundary'
   elif stamp(p['time'])-stamp(previous['time'])>gap_minutes*60:reason='coverage_gap'
   elif state(p,speed_threshold)!=state(previous,speed_threshold):reason='state_change'
   elif run and distance(run[0],p)>radius_m:reason='radius_limit'
  if reason:finish(reason);run=[];start_reason=reason
  if state(p,speed_threshold)!='moving':run.append(p)
  previous=p
 finish('observation_boundary')
 return sorted(result,key=lambda e:(e['vessel'],e['start']))

def summary(events):
 values=sorted(e['minutes']for e in events);n=len(values)
 return {'episodes':n,'vessels':len({e['vessel']for e in events}),'observed_hours':sum(values)/60,'median_minutes':(values[(n-1)//2]+values[n//2])/2 if n else None,'by_state':{s:sum(e['state']==s for e in events)for s in ['reported_moored','reported_anchor','other_stationary']}}
