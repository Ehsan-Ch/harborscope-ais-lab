from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).parent
URL='https://noaaocm.blob.core.windows.net/ais/csv2/csv2024/ais-2024-01-01.csv.zst'
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def download():
 p=ROOT/'data/raw/ais-2024-01-01.csv.zst';p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  partial=p.with_suffix('.partial')
  with urllib.request.urlopen(URL,timeout=120)as response,open(partial,'wb')as f:
   expected=int(response.headers.get('Content-Length',0));size=0
   while b:=response.read(1024*1024):f.write(b);size+=len(b)
  if expected and size!=expected:raise ValueError('Truncated download')
  partial.replace(p)
 sha=digest(p);manifest=ROOT/'data/source_manifest.json'
 if manifest.exists()and json.loads(manifest.read_text())['sha256']!=sha:raise ValueError('Archive changed; review revision')
 manifest.write_text(json.dumps({'url':URL,'sha256':sha,'bytes':p.stat().st_size,'retrieved':'2026-11-17','hash_note':'Locally computed integrity pin; no publisher checksum supplied.'},indent=2)+'\n',encoding='utf-8',newline='\n')
 print('Verified archive',p.stat().st_size,sha,flush=True)
if __name__=='__main__':download()
