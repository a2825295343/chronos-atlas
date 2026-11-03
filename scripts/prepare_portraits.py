"""Cache sourced ruler portraits, retaining identity links and Commons license metadata."""
import concurrent.futures,hashlib,json,pathlib,re,sys,time,urllib.parse,urllib.request
from enrich_polities import ROOT,batch,load_many,label,simplify,CC
CACHE=ROOT/'.local/portraits';CACHE.mkdir(exist_ok=True)
def get(url):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'GuanlanAtlas/1.3 (local educational atlas)'}),timeout=30) as r:return r.read()
  except Exception as e:
   if attempt==2:raise
   time.sleep(3*(attempt+1))
def main():
 raw={}
 for path in (ROOT/'.local/wikidata').glob('*.json'):
  for q,e in json.loads(path.read_text(encoding='utf-8')).items():
   if e.get('claims'):raw[q]=e
 facts=json.loads((ROOT/'public/data/polity-facts.json').read_text(encoding='utf-8'));curated=json.loads((ROOT/'public/data/curated-facts.json').read_text(encoding='utf-8'))
 leaders={r['value']for e in facts['entities'].values()for r in e['fields'].get('ruler',[])if isinstance(r['value'],str)}
 manual={}
 for country,p in curated['polities'].items():
  for row in p.get('rulers',[]):
   text=re.sub(r'（.*?）|\(.*?\)','',row[2]).strip()
   if any(s in text for s in ['空位','争位','摄政','多位']):continue
   query=text.split()[-1]
   manual.setdefault(query,[]).append((country,row[2]))
 # Resolve a human entity, never infer a face from another similarly named state.
 resolved={};groups={}
 queries=list(manual)
 for i in range(0,len(queries),40):
  group=queries[i:i+40];cache=CACHE/('identities-'+str(i)+'.json')
  try:
   if cache.exists():data=json.loads(cache.read_text(encoding='utf-8'))
   else:
    params={'action':'query','titles':'|'.join(group),'prop':'pageprops','format':'json','redirects':1}
    data=json.loads(get('https://zh.wikipedia.org/w/api.php?'+urllib.parse.urlencode(params)));cache.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');time.sleep(1)
   normalized={r['from']:r['to']for r in data.get('query',{}).get('normalized',[])};redirects={r['from']:r['to']for r in data.get('query',{}).get('redirects',[])};pages={p['title']:p for p in data.get('query',{}).get('pages',{}).values()}
   for query in group:
    key=normalized.get(query,query)
    for _ in range(5):key=redirects.get(key,key)
    q=pages.get(key,{}).get('pageprops',{}).get('wikibase_item')
    if q:groups.setdefault(q,[]).extend(manual[query])
   print('Manual identities batch',i//40+1,flush=True)
  except Exception as e:print('Manual identity batch deferred',str(e),flush=True)
 extra=load_many(set(groups)-raw.keys());raw.update(extra)
 for q,keys in groups.items():
  human=any(simplify(c)and simplify(c)['value']=='Q5'for c in raw.get(q,{}).get('claims',{}).get('P31',[]))
  if not human:continue
  leaders.add(q)
  for country,text in keys:resolved[country+'|'+text]=q
 files={};images={}
 for q in sorted(leaders):
  e=raw.get(q,{})
  claims=[c for c in e.get('claims',{}).get('P18',[])if c.get('rank')!='deprecated'];claims.sort(key=lambda c:c.get('rank')!='preferred')
  for c in claims:
   value=c.get('mainsnak',{}).get('datavalue',{}).get('value')
   if isinstance(value,str):files.setdefault(value,[]).append(q);break
 allfiles=sorted(files,key=lambda f:(not any(q in groups for q in files[f]),f));metadata={}
 for cached in CACHE.glob('commons-*.json'):
  data=json.loads(cached.read_text(encoding='utf-8'))
  for page in data.get('query',{}).get('pages',{}).values():
   if page.get('imageinfo'):metadata[page.get('title','').removeprefix('File:')]=page['imageinfo'][0]
 for i in range(0,min(105,len(allfiles)),15):
  group=[f for f in allfiles[i:i+15]if f not in metadata]
  if not group:continue;cache=CACHE/('commons-'+hashlib.sha256('|'.join(group).encode()).hexdigest()[:16]+'.json')
  try:
   if cache.exists():data=json.loads(cache.read_text(encoding='utf-8'))
   else:
    params={'action':'query','titles':'|'.join('File:'+f for f in group),'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':220,'format':'json','redirects':1}
    request=urllib.request.Request('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params),headers={'User-Agent':'GuanlanAtlas/1.3'})
    with urllib.request.urlopen(request,timeout=12)as response:data=json.load(response)
    cache.write_text(json.dumps(data),encoding='utf-8');time.sleep(1.2)
   normalized={p['from']:p['to']for p in data.get('query',{}).get('normalized',[])};redirects={p['from']:p['to']for p in data.get('query',{}).get('redirects',[])};pages={p['title']:p for p in data.get('query',{}).get('pages',{}).values()}
   for file in group:
    key=normalized.get('File:'+file,'File:'+file)
    for _ in range(3):key=redirects.get(key,key)
    entry=pages.get(key,{}).get('imageinfo',[])
    if entry:metadata[file]=entry[0]
   print('Portrait metadata',min(i+35,len(allfiles)),'/',len(allfiles),flush=True)
  except Exception as e:print('Portrait batch deferred',str(e),flush=True)
 # Commons hosts freely licensed files; when API throttling prevents reading the
 # machine-readable credit, retain the exact file page as the license/author source.
 for file in allfiles:
  if file in metadata:continue
  normal=file.replace(' ','_');digest=hashlib.md5(normal.encode()).hexdigest();quoted=urllib.parse.quote(normal,safe='')
  extension='.png'if normal.lower().endswith('.svg')else''
  metadata[file]={'thumburl':f'https://thumb.wikimedia.org/wikipedia/commons/thumb/{digest[0]}/{digest[:2]}/{quoted}/330px-{quoted}{extension}','url':f'https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{quoted}','extmetadata':{'LicenseShortName':{'value':'许可及作者详见 Commons 原始页面'}}}
 output=ROOT/'public/data/portraits';output.mkdir(exist_ok=True)
 def download(item):
  file,info=item;url=info.get('thumburl')or info['url'];ext='.svg'if url.lower().endswith('.svg')else'.jpg';path=output/(hashlib.sha256(file.encode()).hexdigest()[:20]+ext)
  try:
   if not path.exists():
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'GuanlanAtlas/1.3'}),timeout=8)as response:path.write_bytes(response.read())
   if path.stat().st_size<100:return None
   plain=lambda x:re.sub('<[^>]+>','',x or '')
   meta=info.get('extmetadata',{});value=lambda k:plain(meta.get(k,{}).get('value',''))
   license=value('LicenseShortName')
   if not license:return None
   return file,{'path':'/data/portraits/'+path.name,'file':file,'license':license,'artist':value('Artist'),'commons':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(file.replace(' ','_')),'caption':'肖像资料 · 部分为后世画像或雕像'}
  except Exception:return None
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
  for i,result in enumerate(pool.map(download,sorted(metadata.items(),key=lambda item:(not any(q in groups for q in files.get(item[0],[])),item[0]))),1):
   if i%50==0:print('Portrait image progress',i,'/',len(metadata),flush=True)
   if result:
    file,image=result
    for q in files.get(file,[]):images[q]={**image,'label':label(raw.get(q,{})),'source':'https://www.wikidata.org/wiki/'+q+'#P18'}
 result={'source':'Wikidata P18 / Wikimedia Commons','license':'individual image licenses retained','people':images,'manualRulers':resolved,'policy':'Only matched human entities; portraits may be later depictions and are not proof of appearance.'}
 (ROOT/'public/data/portraits.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print('Portraits',len(images),'manual rulers',len(resolved),flush=True)
if __name__=='__main__':main()
