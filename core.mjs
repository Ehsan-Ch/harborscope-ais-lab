export const labels={reported_moored:'Reported moored',reported_anchor:'Reported at anchor',other_stationary:'Other low-speed'};
export function selectEvents(report,kind='all',status='all'){return report.events.filter(e=>(kind==='all'||e.kind===kind)&&(status==='all'||e.state===status));}
export function stats(events){const sorted=events.map(e=>e.minutes).sort((a,b)=>a-b),n=sorted.length;return {episodes:n,vessels:new Set(events.map(e=>e.vessel)).size,hours:sorted.reduce((a,b)=>a+b,0)/60,median:n?(sorted[(n-1)>>1]+sorted[n>>1])/2:null};}
export function csv(events){const fields=['id','vessel','kind','state','start','end','minutes','reports','start_reason','end_reason'];return fields.join(',')+'\n'+events.map(e=>fields.map(k=>JSON.stringify(e[k])).join(',')).join('\n')+'\n';}
export function visibleTrack(track,clock){return track.points.filter(p=>Date.parse(p.time)<=Date.parse(clock));}
