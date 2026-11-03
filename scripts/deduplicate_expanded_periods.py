"""Remove intermediate revisions emitted before the stage's final-write fix."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 removed=0
 for path in (ROOT/'public/data/temporal').glob('*.geojson'):
  d=json.loads(path.read_bytes());rows={};other=[]
  for f in d['features']:
   p=f['properties']
   if p.get('chronologyPatch')!='expanded-history-gaps-2026-10-31':other.append(f);continue
   k=(str(p['sourceRecord']),p['NAME'],p['validFrom'],p['validTo'])
   if k in rows:removed+=1
   rows[k]=f
  final=other+list(rows.values())
  if len(final)!=len(d['features']):d['features']=final;path.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print('Removed superseded intermediate period geometries',removed,flush=True)
if __name__=='__main__':main()
