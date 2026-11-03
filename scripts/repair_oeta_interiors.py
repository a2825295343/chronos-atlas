"""Bring the already generated OETA districts in line with the reviewed mask."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely import union_all
from shapely.geometry import shape,mapping,box
from prepare_political_presentation import label_path

def main():
 admin=json.loads((ROOT/'.local/presentation/admin0.geojson').read_bytes())['features'];syria=union_all([shape(f['geometry'])for f in admin if f['properties']['NAME_EN']=='Syria'])
 interior=syria.intersection(box(35,30,37,34.5));path=ROOT/'public/data/temporal/19.geojson';data=json.loads(path.read_bytes())
 for year in [1918,1919]:
  west=next(f for f in data['features']if f['properties']['NAME']=='OETA Western Military Administration'and f['properties']['validFrom']==year)
  east=next(f for f in data['features']if f['properties']['NAME']=='OETA East Arab Administration'and f['properties']['validFrom']==year)
  cut=shape(west['geometry']).intersection(interior)
  if cut.is_empty:continue
  for f,g in [(west,shape(west['geometry']).difference(cut)),(east,union_all([shape(east['geometry']),cut]))]:
   f['geometry']=mapping(g);f['properties']['labelPath']=label_path(f['geometry'],f['properties']['displayName']);f['properties']['representationNote']=f['properties'].get('representationNote','')+' 南部叙利亚内陆（包括大马士革）归入东区，不随沿岸概化区划入西区。'
 path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print('OETA Damascus/interior district checked',flush=True)
if __name__=='__main__':main()
