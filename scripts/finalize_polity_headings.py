"""Two remaining ruler-list headings are not names or identities of states."""
import copy
from territory_repair_stage import read,write
FIXES={'Principality of Waldeck and Pyrmont':('瓦尔德克和皮尔蒙特亲王国','local:waldeck-pyrmont','Q165763'),'Principality of Schwarzburg-Sonderhausen':('施瓦茨堡-松德斯豪森亲王国','local:schwarzburg-sondershausen','Q708821')}
def main():
 facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json');idx=read('public/data/temporal/index.json');counts={}
 for century in idx['centuries']:
  path=f'public/data/temporal/{century}.geojson';db=read(path);count=0
  for f in db['features']:
   p=f['properties']
   if p['NAME']not in FIXES:continue
   zh,q,old=FIXES[p['NAME']];p.update(displayName=zh,sourceQid=p.get('sourceQid',p.get('qid')),qid=q,entityId=q);count+=1
  if count:write(path,db);counts[century]=count
 for n,(zh,q,old)in FIXES.items():
  cur['identities'][n]=q;e=copy.deepcopy(facts['entities'].get(q,facts['entities'].get(old,dict(fields={}))))
  e.update(label=zh,en=n,description='具体亲王国档案；原始统治者列表仅作人物检索线索，不作为国家身份。');e['fields'].pop('instanceOf',None);facts['entities'][q]=e
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  d=read(path);d.update({n:v[0]for n,v in FIXES.items()});write(path,d)
 write('public/data/polity-facts.json',facts);write('public/data/curated-facts.json',cur);write('public/data/polity-heading-followup-review.json',dict(reviewedAt='2026-11-02',states=FIXES,shardRows=counts))
 print('Corrected catalogue headings',len(FIXES))
if __name__=='__main__':main()
