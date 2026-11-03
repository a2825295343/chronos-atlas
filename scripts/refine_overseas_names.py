import json,pathlib,sys
ROOT=pathlib.Path('.').resolve();sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'.local/python'))
from shapely.geometry import shape,mapping
from shapely import make_valid
from prepare_political_presentation import label_path
admin=json.loads((ROOT/'.local/presentation/admin0.geojson').read_text(encoding='utf-8'))['features'];british=[f for f in admin if f['properties'].get('SOV_A3')=='GB1'and f['properties'].get('NAME_EN')!='United Kingdom']
labels=json.loads((ROOT/'src/localization/display-names.zh.json').read_text(encoding='utf-8'));records=set();count=0
for path in (ROOT/'public/data/temporal').glob('*.geojson'):
 data=json.loads(path.read_text(encoding='utf-8'));rows=[]
 for f in data['features']:
  p=f['properties'];name=p['NAME'];parent=p.get('sovereignName');country=name.split(' Colony - ',1)[-1]
  cap=1931 if parent=='United Kingdom'and country in ['Canada','South Africa']else 1942 if parent=='United Kingdom'and country=='Australia'else 1947 if parent=='United Kingdom'and country=='New Zealand'else None
  if cap is not None:
   p['validTo']=min(p['validTo'],cap)
   if p['validFrom']>p['validTo']:continue
  if parent=='United Kingdom'and country=='China':p['displayName']='英属香港及在华租借地';labels[name]=p['displayName']
  if name=='British Overseas Territories':
   g=make_valid(shape(f['geometry']));remaining=g
   for territory in british:
    a=territory['properties'];cut=g.intersection(make_valid(shape(territory['geometry'])))
    if cut.is_empty or cut.geom_type not in ['Polygon','MultiPolygon']or cut.area<.001:continue
    n='British Territory - '+a['NAME_EN'];label=a.get('NAME_ZH')or a['NAME_EN'];labels[n]=label
    properties={**p,'NAME':n,'SUBJECTO':n,'sourcePolity':name,'displayName':label,'sovereignName':'United Kingdom','sovereignQid':'Q145','territoryType':'overseas','partitionBasis':'现代英国海外领地地理分区；保留主权所属资料'}
    baseline=label_path(mapping(cut),label)
    if baseline:properties['labelPath']=baseline
    rows.append({'type':'Feature','id':str(f['id'])+'-'+a['ADM0_A3'],'properties':properties,'geometry':mapping(cut)});remaining=remaining.difference(cut);count+=1
   if not remaining.is_empty and remaining.geom_type in ['Polygon','MultiPolygon']and remaining.area>.05:rows.append({**f,'geometry':mapping(remaining),'properties':{**p,'displayName':'英国其他海外领地'}})
  else:
   century=int(path.stem)
   if p['validTo']>=century*100:rows.append(f)
 for f in rows:records.add(f['properties']['sourceRecord'])
 data['features']=rows;path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
p=ROOT/'public/data/temporal/index.json';index=json.loads(p.read_text(encoding='utf-8'));index['counts']['polityRecords']=len(records);p.write_text(json.dumps(index,ensure_ascii=False),encoding='utf-8')
(ROOT/'src/localization/display-names.zh.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2),encoding='utf-8');(ROOT/'src/color-groups.mjs').write_text('export const colorGroups='+json.dumps(labels,ensure_ascii=False)+';\n',encoding='utf-8')
print('Named overseas units',count,'records',len(records),flush=True)
