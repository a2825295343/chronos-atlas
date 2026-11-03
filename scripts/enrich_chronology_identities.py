"""Fetch official structured metadata for the reviewed identities, preserving dates."""
import json,re
from enrich_polities import ROOT,load_many,PROPS,simplify,label,CC
def main():
 path=ROOT/'public/data/polity-facts.json';data=json.loads(path.read_bytes())
 rules=json.loads((ROOT/'public/data/chronology-corrections.json').read_bytes())['identityCorrections']
 ids={r['qid']for r in rules if re.fullmatch(r'Q\d+',r['qid'])}|{'Q2475921','Q37','Q403'}
 raw={}
 for file in (ROOT/'.local/wikidata').glob('*.json'):
  for q,e in json.loads(file.read_bytes()).items():
   if q in ids and e.get('claims'):raw[q]=e
 raw.update(load_many(ids-raw.keys()))
 refs=set()
 for q,e in raw.items():
  if q in data['entities']:continue
  fields={}
  for prop,key in PROPS.items():
   rows=[v for claim in e.get('claims',{}).get(prop,[])if(v:=simplify(claim))]
   if rows:fields[key]=rows[:80]
   refs.update(r['value']for r in rows if isinstance(r['value'],str)and re.fullmatch(r'Q\d+',r['value']))
  data['entities'][q]={'label':label(e),'en':e.get('labels',{}).get('en',{}).get('value',''),'description':CC.convert(next((e.get('descriptions',{}).get(k,{}).get('value')for k in ['zh-hans','zh','en']if e.get('descriptions',{}).get(k)),'')),'fields':fields}
 labels=load_many(refs-data['labels'].keys(),'labels');data['labels'].update({q:label(e)for q,e in {**raw,**labels}.items()})
 for q in ids:
  if q not in data['entities']:continue
  for rows in data['entities'][q]['fields'].values():
   for r in rows:r['label']=data['labels'].get(str(r['value']),str(r['value']))
 path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 for q in sorted(ids):
  e=data['entities'].get(q,{})
  print(json.dumps([q,e.get('en','MISSING'),[r['value']for r in e.get('fields',{}).get('founded',[])],[r['value']for r in e.get('fields',{}).get('dissolved',[])]],ensure_ascii=True),flush=True)
if __name__=='__main__':main()
