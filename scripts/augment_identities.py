import json,re,sys
from pathlib import Path
sys.path.insert(0,'scripts')
from enrich_polities import load_many,PROPS,simplify,label,CC
p=Path('public/data/polity-facts.json');d=json.loads(p.read_text(encoding='utf-8'))
ids=['Q45','Q884','Q971','Q865','Q13426199','Q180573','Q222','Q219','Q172640']
entities=load_many([q for q in ids if q not in d['entities']]);refs=set()
for q,e in entities.items():
 fields={}
 for prop,k in PROPS.items():
  rows=[v for c in e.get('claims',{}).get(prop,[])if(v:=simplify(c))]
  if rows:fields[k]=rows[:80]
  refs.update(r['value']for r in rows if isinstance(r['value'],str)and re.fullmatch('Q[0-9]+',r['value']))
 d['entities'][q]={'label':label(e),'en':e.get('labels',{}).get('en',{}).get('value',''),'description':CC.convert(e.get('descriptions',{}).get('zh',{}).get('value','')),'fields':fields}
ref=load_many(refs-d['labels'].keys(),'labels');d['labels'].update({q:label(e)for q,e in ref.items()})
for q,e in entities.items():
 for rows in d['entities'][q]['fields'].values():
  for row in rows:row['label']=d['labels'].get(str(row['value']),str(row['value']))
p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8');print('Identity corrections metadata',len(entities),flush=True)
