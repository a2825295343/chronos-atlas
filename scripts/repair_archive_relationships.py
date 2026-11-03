"""Keep postwar records valid after removing office-as-person mistakes."""
import copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def main():
 facts=read('public/data/polity-facts.json');tag='archive-relationship-followup-2026-10-31';target=facts['entities']['Q203493']['fields']
 target['ruler']=[r for r in target.get('ruler',[])if r.get('supplement')!=tag]
 for r in facts['entities']['Q218']['fields']['ruler']:
  a,b=r.get('from'),r.get('to')
  if a is None or b is None or a>1947 or b<1881:continue
  row=copy.deepcopy(r);row.update({'from':max(a,1881),'to':min(b,1947),'roleLabel':'罗马尼亚国王','supplement':tag,'citation':['https://en.wikipedia.org/wiki/King_of_Romania','https://www.wikidata.org/wiki/'+str(r['value'])+'#P39']});target.setdefault('ruler',[]).append(row)
 write('public/data/polity-facts.json',facts)
 count=0
 for path in (ROOT/'public/data/temporal').glob('*.geojson'):
  data=json.loads(path.read_bytes());changed=False
  for f in data['features']:
   p=f['properties']
   if p['NAME']!='Netherlands Antilles':continue
   p.update(sovereignName='Netherlands',sovereignQid='Q55',territoryType='overseas',relationshipSource='https://en.wikipedia.org/wiki/Netherlands_Antilles',representationNote='源GIS将部分荷兰美洲领地并为一个轮廓，名称与行政构成尚待进一步逐期拆分；1954年前的殖民地与其后的王国自治组成地区不能视为相同宪制。上层中央元首另列，不冒充地方总督。');count+=1;changed=True
  if changed:path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print('Romanian named royal terms restored; Dutch overseas superior recorded',count,flush=True)
if __name__=='__main__':main()
