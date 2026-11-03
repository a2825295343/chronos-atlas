"""Fetch at most 28 additional, human-verified portraits for newly added reigns."""
import json,pathlib,re,urllib.parse,urllib.request,hashlib,concurrent.futures,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from enrich_polities import simplify,label
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'GuanlanAtlas/1.4 historical research'}),timeout=18) as r:return r.read()
def main():
 path=ROOT/'public/data/portraits.json';portraits=json.loads(path.read_bytes());curated=json.loads((ROOT/'public/data/curated-facts.json').read_bytes())['polities'];queries={}
 for country,c in curated.items():
  if not any('唐' in r[2] or '宋' in r[2] or '元世祖' in r[2] or '成吉思汗' in r[2] for r in c.get('rulers',[])):continue
  for a,b,text in c['rulers']:
   if country+'|'+text in portraits['manualRulers']:continue
   simple=re.sub(r'（.*?）','',text).split()[-1];queries.setdefault(simple,[]).append((country,text))
 names=list(queries)[:28];cache=ROOT/'.local/portraits/new-dynastic-ids.json'
 if cache.exists():result=json.loads(cache.read_bytes())
 else:
  params={'action':'query','titles':'|'.join(names),'prop':'pageprops','format':'json','redirects':1};result=json.loads(get('https://zh.wikipedia.org/w/api.php?'+urllib.parse.urlencode(params)));cache.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
 q=result.get('query',{});redirects={r['from']:r['to'] for r in q.get('normalized',[])+q.get('redirects',[])};pages={p['title']:p for p in q.get('pages',{}).values()};ids={}
 for name in names:
  key=name
  for i in range(4):key=redirects.get(key,key)
  qid=pages.get(key,{}).get('pageprops',{}).get('wikibase_item')
  if qid:ids[qid]=name
 if not ids:print('No new verified portrait identities');return
 cache=ROOT/'.local/portraits/new-dynastic-entities.json'
 if cache.exists():entities=json.loads(cache.read_bytes())
 else:
  params={'action':'wbgetentities','ids':'|'.join(ids),'props':'labels|claims','languages':'zh-hans|zh|en','format':'json'};entities=json.loads(get('https://www.wikidata.org/w/api.php?'+urllib.parse.urlencode(params)))['entities'];cache.write_text(json.dumps(entities,ensure_ascii=False),encoding='utf-8')
 def download(item):
  person,name=item;e=entities.get(person,{})
  if not any((s:=simplify(c)) and s['value']=='Q5' for c in e.get('claims',{}).get('P31',[])):return None
  c=next((s for claim in e.get('claims',{}).get('P18',[]) if (s:=simplify(claim)) and isinstance(s['value'],str)),None)
  if not c:return None
  file=c['value'];normal=file.replace(' ','_');md5=hashlib.md5(normal.encode()).hexdigest();quoted=urllib.parse.quote(normal,safe='');ext='.png' if file.lower().endswith('.svg') else ''
  dest=ROOT/'public/data/portraits'/(hashlib.sha256(file.encode()).hexdigest()[:20]+'.jpg')
  try:
   if not dest.exists():dest.write_bytes(get(f'https://thumb.wikimedia.org/wikipedia/commons/thumb/{md5[0]}/{md5[:2]}/{quoted}/330px-{quoted}{ext}'))
   if dest.read_bytes()[:1]==b'<':return None
   return person,name,{'path':'/data/portraits/'+dest.name,'label':label(e),'file':file,'commons':'https://commons.wikimedia.org/wiki/File:'+quoted,'license':'作者与许可见 Commons 原始文件页','source':'https://www.wikidata.org/wiki/'+person,'caption':'有来源的历史画像或后世绘像；并非现代照片复原'}
  except Exception as error:print('Portrait unavailable',person,str(error),flush=True);return None
 count=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for result in pool.map(download,ids.items()):
   if not result:continue
   person,name,record=result;portraits['people'][person]=record
   for country,text in queries[name]:portraits['manualRulers'][country+'|'+text]=person
   count+=1
 path.write_text(json.dumps(portraits,ensure_ascii=False,separators=(',',':')),encoding='utf-8');print('Additional portraits',count,'total',len(portraits['people']),flush=True)
if __name__=='__main__':main()
