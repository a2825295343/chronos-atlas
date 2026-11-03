"""Partition source ownership around dated control overlays, without double areas.
Back up the pre-overlay shard once so the operation is repeatable.
"""
import json,pathlib,sys,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely.geometry import shape,mapping
from shapely import union_all,make_valid
from prepare_political_presentation import label_path
def main():
 controls=json.loads((ROOT/'public/data/control-areas.geojson').read_bytes())['features'];backup=ROOT/'.local/control-originals';backup.mkdir(exist_ok=True)
 for century in {int(f['properties']['validFrom'])//100 for f in controls}:
  dest=ROOT/f'public/data/temporal/{century}.geojson';original=backup/dest.name
  if not original.exists():shutil.copyfile(dest,original)
  data=json.loads(original.read_bytes());rows=[];overlays=[]
  for f in controls:
   p=f['properties']
   if p['validFrom']//100!=century:continue
   # Temporary states already present keep their original dated record. Add only
   # if genuinely missing; never overwrite a better upstream annual boundary.
   if p.get('kind')=='temporary' and any(x['properties']['NAME']==p['SUBJECTO'] and x['properties']['validFrom']<=p['validFrom']<=x['properties']['validTo'] for x in data['features']):continue
   overlays.append((f,make_valid(shape(f['geometry']))))
  for f in data['features']:
   p=f['properties'];from_,to=p['validFrom'],p['validTo'];g=shape(f['geometry'])
   relevant=[(r,o) for r,o in overlays if r['properties']['validFrom']<=to and from_<=r['properties']['validTo'] and g.intersects(o)]
   if not relevant:rows.append(f);continue
   stops=sorted({from_,to+1}|{max(from_,r['properties']['validFrom']) for r,o in relevant}|{min(to+1,r['properties']['validTo']+1) for r,o in relevant})
   for a,b in zip(stops,stops[1:]):
    active=[o for r,o in relevant if r['properties']['validFrom']<=a<=r['properties']['validTo']];cut=make_valid(g.difference(union_all(active))) if active else g
    if cut.is_empty:continue
    if cut.geom_type=='GeometryCollection':cut=union_all([x for x in cut.geoms if x.geom_type in ['Polygon','MultiPolygon']])
    if cut.is_empty or cut.geom_type not in ['Polygon','MultiPolygon']:continue
    props={**p,'validFrom':a,'validTo':b-1}
    if active:props.pop('labelPath',None)
    rows.append({**f,'geometry':mapping(cut),'properties':props})
  for f,g in overlays:
   p={**f['properties'],'sourceRecord':'control-'+f['properties']['id'],'controlArea':True,'labelPath':label_path(g,f['properties']['displayName'])}
   rows.append({**f,'properties':p})
  dest.write_text(json.dumps({'type':'FeatureCollection','features':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8');print('Control-partitioned shard',century,len(rows),flush=True)
 index=ROOT/'public/data/temporal/index.json';d=json.loads(index.read_bytes());d['changeYears']=sorted(set(d['changeYears'])|{p for f in controls for p in [f['properties']['validFrom'],f['properties']['validTo']+1]})
 records={f['properties']['sourceRecord'] for century in d['centuries'] for f in json.loads((ROOT/f'public/data/temporal/{century}.geojson').read_bytes())['features']}
 d['counts']['sourcePolityRecords']=12059;d['counts']['polityRecords']=len(records);d['counts']['supplementaryControlAreas']=sum(isinstance(r,str) and r.startswith('control-') for r in records);index.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
 names=ROOT/'src/localization/display-names.zh.json';labels=json.loads(names.read_bytes());labels.update({f['properties']['NAME']:f['properties']['displayName'] for f in controls});labels['Allied Control Council']='盟国管制委员会';names.write_text(json.dumps(labels,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
