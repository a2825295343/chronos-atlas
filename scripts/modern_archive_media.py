"""Merge sourced modern flag and officeholder images without erasing history."""
import argparse,concurrent.futures,hashlib,html,io,json,re,time,urllib.parse
from enrich_modern_archives import ROOT,CACHE,REVIEW,request,read,write,value,qvalues
from enrich_polities import simplify,label
from PIL import Image
def raw_entities(scope):
 result={}
 for p in CACHE.glob(scope+'-*.json'):result.update(json.loads(p.read_bytes()))
 return result
def plain(s):return html.unescape(re.sub('<[^>]+>','',s or ''))
def applicable(r,y):return(r.get('from')is None or r['from']<=y)and(r.get('to')is None or y<=r['to'])and(r.get('at')is None or y==r['at'])
def metadata(files,width=400):
 infos={};files=sorted(set(files));folder=ROOT/'.local/modern-media';folder.mkdir(exist_ok=True)
 for i in range(0,len(files),35):
  group=files[i:i+35];path=folder/('commons-'+hashlib.sha256(((''if width==400 else str(width)+'|')+'|'.join(group)).encode()).hexdigest()[:16]+'.json')
  if path.exists():d=json.loads(path.read_bytes())
  else:
   params=urllib.parse.urlencode({'action':'query','titles':'|'.join('File:'+f for f in group),'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':width,'format':'json','redirects':1})
   d=json.loads(request('https://commons.wikimedia.org/w/api.php?'+params));path.write_text(json.dumps(d,ensure_ascii=False),encoding='utf8');time.sleep(1)
  normalized={r['from']:r['to']for r in d.get('query',{}).get('normalized',[])};redirects={r['from']:r['to']for r in d.get('query',{}).get('redirects',[])};pages={p['title']:p for p in d.get('query',{}).get('pages',{}).values()}
  for file in group:
   name=normalized.get('File:'+file,'File:'+file)
   for _ in range(5):name=redirects.get(name,name)
   info=pages.get(name,{}).get('imageinfo',[])
   if info:infos[file]=info[0]
  print('Commons metadata',min(i+35,len(files)),'/',len(files),flush=True)
 return infos
def images(files,folder,existing,workers=3,downloader=None,original_fallback=True,thumbnail_width=400):
 needed=set(files)-existing.keys();infos=metadata(needed,thumbnail_width);result={};failures=[];dest=ROOT/'public/data'/folder;dest.mkdir(exist_ok=True)
 def one(file):
  if file in existing:return file,existing[file],None
  info=infos.get(file)
  if not info:return file,None,'没有取得Commons图像及许可信息'
  meta=info.get('extmetadata',{});description=plain(meta.get('ImageDescription',{}).get('value',''))
  if re.search(r'fictitious|fictional|imaginary flag',description,re.I):return file,None,'图像被标记为虚构'
  license=plain(meta.get('LicenseShortName',{}).get('value',''))
  if not license:return file,None,'许可信息缺失'
  urls=list(dict.fromkeys(u for u in [info.get('thumburl'),info.get('url')if original_fallback else None]if u));error=''
  for url in urls:
   if not re.match(r'https://(?:upload|thumb)\.wikimedia\.org/',url):continue
   ext='.svg'if urllib.parse.urlsplit(url).path.lower().endswith('.svg')else'.jpg'if re.search(r'\.jpe?g$',urllib.parse.urlsplit(url).path,re.I)else'.png'
   path=dest/(hashlib.sha256(file.encode()).hexdigest()[:20]+ext)
   try:
    data=path.read_bytes()if path.exists()else(downloader or request)(url)
    if ext=='.svg':
     import xml.etree.ElementTree as ET
     if not ET.fromstring(data).tag.endswith('svg'):raise ValueError('不是SVG图像')
    else:Image.open(io.BytesIO(data)).verify()
    if not path.exists():path.write_bytes(data)
    return file,{'path':'/data/'+folder+'/'+path.name,'file':file,'license':license,'artist':plain(meta.get('Artist',{}).get('value','')),'commons':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(file.replace(' ','_')),'description':description[:500]},None
   except Exception as e:error=str(e)
  return file,None,error or'图像下载失败'
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers)as pool:
  for i,(file,img,error)in enumerate(pool.map(one,sorted(set(files))),1):
   if img:result[file]=img
   else:failures.append({'file':file,'reason':error})
   if i%30==0:print(folder,'images',i,'/',len(set(files)),flush=True)
 return result,failures
def flags():
 raw=raw_entities('countries');db=read('public/data/flags.json');pool={r['file']:r for rs in db['entities'].values()for r in rs if(ROOT/'public'/r['path'].lstrip('/')).exists()};records=[]
 for q,e in raw.items():
  for c in e.get('claims',{}).get('P41',[]):
   r=simplify(c)
   if not r or not isinstance(r['value'],str):continue
   file=r['value']
   if re.search(r'fictit|fiction|imaginary|proposed|fantasy',file,re.I):continue
   if r['to']is not None and r['to']<1900:continue
   if r['from']is not None and r['from']>2026:continue
   records.append({'qid':q,'file':file,'from':r['from'],'to':r['to'],'at':r['at'],'rank':r['rank'],'source':'https://www.wikidata.org/wiki/'+q+'#P41','reviewedAt':REVIEW})
 available,failures=images([r['file']for r in records],'flags',pool)
 for q in raw:
  new=[{**available[r['file']],**r}for r in records if r['qid']==q and r['file']in available]
  if not new:continue
  new.sort(key=lambda r:(r['rank']!='preferred',r.get('to')is not None,-(r.get('from')or -10000)))
  keys={(r['file'],r['from'],r['to'],r['at'])for r in new}
  old=[r for r in db['entities'].get(q,[])if(r['file'],r.get('from'),r.get('to'),r.get('at'))not in keys and r.get('to')is not None and r['to']<1900]
  db['entities'][q]=new+old
 db['count']=len({r['path']for rs in db['entities'].values()for r in rs});db['modernReview']=REVIEW;write('public/data/flags.json',db);write('public/data/modern-flag-media-review.json',{'reviewedAt':REVIEW,'countryEntities':len(raw),'rows':len(records),'failures':failures})
 print('Modern flag records',len(records),'unavailable media',len(failures),flush=True)
def portraits():
 raw=raw_entities('officeholders');facts=read('public/data/polity-facts.json')['entities'];inventory=read('.local/modern-polities.json');curated=read('public/data/curated-facts.json');db=read('public/data/portraits.json');wanted=set()
 for r in inventory:
  if r['category']=='non-state':continue
  e=facts.get(r['qid'],{})
  for field in ['ruler','headOfGovernment']:
   for person in e.get('fields',{}).get(field,[]):
    if any(applicable(person,y)and(person.get('from')is not None or person.get('to')is not None or person.get('at')is not None)for y in [2024,2026]):wanted.add(person['value'])
  for a,b,name in curated['polities'].get(r['qid'],{}).get('rulers',[]):
   if any(a<=y<=b for y in [2024,2026])and(q:=db['manualRulers'].get(r['qid']+'|'+name)):wanted.add(q)
 files={}
 for q in wanted:
  e=raw.get(q,{})
  if 'Q5'not in qvalues(e,'P31'):continue
  claims=[c for c in e.get('claims',{}).get('P18',[])if c.get('rank')!='deprecated'];claims.sort(key=lambda c:c.get('rank')!='preferred')
  for c in claims:
   if isinstance(file:=value(c),str):files[q]=file;break
 pool={r['file']:r for r in db['people'].values()if(ROOT/'public'/r['path'].lstrip('/')).exists()};available,failures=images(files.values(),'portraits',pool)
 for q,file in files.items():
  if file in available:db['people'][q]={**available[file],'label':label(raw[q]),'source':'https://www.wikidata.org/wiki/'+q+'#P18','caption':'已核对人物身份的照片或画像；拍摄年代不等同所选任职年度'}
 db['modernReview']=REVIEW;write('public/data/portraits.json',db);write('public/data/modern-portrait-media-review.json',{'reviewedAt':REVIEW,'officeholders':len(wanted),'matchedHumanImages':len(files),'failures':failures});print('Modern officeholder portraits',len(files),'unavailable media',len(failures),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['flags','portraits','all'],default='all',nargs='?');a=p.parse_args()
 if a.stage in ['flags','all']:flags()
 if a.stage in ['portraits','all']:portraits()
