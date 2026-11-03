"""Translate remaining public descriptive text; cache drafts separately from facts.
No English original, date, numeric value, actor ID, or citation is overwritten.
"""
import json,pathlib,re,urllib.parse,urllib.request,concurrent.futures,time,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];CACHE=ROOT/'.local/translations/archive';CACHE.mkdir(parents=True,exist_ok=True)
def strings():
 facts=json.loads((ROOT/'public/data/polity-facts.json').read_bytes());items=set(facts['labels'].values())
 for entity in facts['entities'].values():
  items.update([entity.get('description',''),entity.get('label','')]);items.update(r.get('label','') for rows in entity['fields'].values() for r in rows)
 db=json.loads((ROOT/'public/data/conflicts.json').read_bytes())
 for war in db['wars']:
  items.add(war['name']);items.update(p['name'] for p in war['participants']);items.add(war.get('location',''))
  for a in war.get('annual',{}).values():
   items.add(a['territory']);items.update(x for key in ['sideA','sideB','secondaryA','secondaryB'] for x in a[key])
 for e in json.loads((ROOT/'public/data/statistics.json').read_bytes()).values():items.update(e.get(key,'') for key in ['name','region','income','capital'])
 return sorted(x for x in items if re.search('[A-Za-z]{3}',x) and not re.search('[\u3400-\u9fff]',x) and not re.fullmatch(r'Q\d+|[-\d.]+',x) and not x.lower().endswith(('.svg','.png','.jpg','.jpeg','.gif','.webp')))
def translate(batch):
 path=CACHE/(hashlib.sha256('\n'.join(batch).encode()).hexdigest()[:20]+'.json')
 if path.exists():return json.loads(path.read_bytes())
 query=urllib.parse.urlencode({'client':'gtx','sl':'en','tl':'zh-CN','dt':'t','q':'\n'.join(batch)})
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request('https://translate.googleapis.com/translate_a/single?'+query,headers={'User-Agent':'GuanlanAtlas/1.3'}),timeout=30) as response:r=json.load(response)
   lines=''.join(x[0] or '' for x in r[0]).strip().splitlines()
   if len(lines)!=len(batch):
    if len(batch)>1:
     result={}
     for text in batch:result.update(translate([text]))
     return result
    lines=[' '.join(lines)]
   result=dict(zip(batch,lines));path.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8');time.sleep(.25);return result
  except Exception as error:
   if attempt==2:print('Translation batch deferred:',str(error),flush=True);return {}
   time.sleep(2)
def main():
 items=strings();batches=[];batch=[];length=0
 for item in items:
  if batch and (len(batch)>=14 or length+len(item)>1400):batches.append(batch);batch=[];length=0
  batch.append(item);length+=len(item)
 if batch:batches.append(batch)
 output={};print('Public strings',len(items),'batches',len(batches),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for i,result in enumerate(pool.map(translate,batches),1):
   output.update(result)
   if i%20==0:print('Translated batches',i,'/',len(batches),flush=True)
 overrides={'Government':'政权争夺','Territory':'领土争端','High income':'高收入','Upper middle income':'中高收入','Lower middle income':'中低收入','Low income':'低收入','World War I':'第一次世界大战','World War II':'第二次世界大战','Korean':'朝鲜战争','Third Sino-Japanese':'全面抗日战争','Second Sino-Japanese':'九一八事变及东北抗战','First Kashmir':'第一次印巴战争','Assam':'中印边境战争','Sinai War':'苏伊士运河战争','Lopez':'巴拉圭战争','La Plata':'拉普拉塔战争','Seven Weeks':'普奥战争','Badme Border':'厄立特里亚—埃塞俄比亚战争','Nomonhan':'诺门罕战役','Changkufeng':'张鼓峰事件','Off-shore Islands':'第一次台海危机','Taiwan Straits':'第二次台海危机','SideA':'甲方','SideB':'乙方'}
 output.update(overrides)
 (ROOT/'src/localization/text.zh.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'public/data/translation-review.json').write_text(json.dumps({'scope':'国家档案描述、字段标签、战争名、参战势力与统计说明','method':'公开文本机器翻译初稿，常见历史战争名人工校正；原文保留于原始数据','strings':len(output),'requested':len(items),'missing':[x for x in items if x not in output]},ensure_ascii=False,indent=2),encoding='utf-8')
 print('Translated strings',len(output),flush=True)
if __name__=='__main__':main()
