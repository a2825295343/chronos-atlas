"""Apply reviewed French map headings and preserve common search names."""
from territory_repair_stage import ROOT,read,write
from prepare_political_presentation import label_path
from polity_display_names import DISPLAY_NAMES

def main():
 names={n:v for n,v in DISPLAY_NAMES.items()if v in ['法兰西','法兰西帝国']}
 for file in ['display-names.zh.json','temporal.zh.json']:
  path='src/localization/'+file;d=read(path);d.update(names);write(path,d)
 provenance=read('src/localization/provenance.json');provenance.update({n:'reviewed-historical-display-name'for n in names});write('src/localization/provenance.json',provenance)
 files=list((ROOT/'public/data/temporal').glob('*.geojson'))+list((ROOT/'public/data').glob('world_*.geojson'));count=0
 republics=['French First Republic','French Directory','French Consulate','French Second Republic','French Third Republic','French Fourth Republic','French Fifth Republic','French Republic','France']
 for path in files:
  d=read(path);changed=False
  for f in d['features']:
   p=f.get('properties')or{};n=p.get('NAME')
   if n in names:
    p['displayName']=names[n];p['labelPath']=label_path(f['geometry'],names[n]);count+=1;changed=True
   if n in names or n in republics:p['searchAliases']=['法国','法兰西'];changed=True
  if changed:write(path,d)
 print('French monarchy and empire labels updated',count,flush=True)

if __name__=='__main__':main()
