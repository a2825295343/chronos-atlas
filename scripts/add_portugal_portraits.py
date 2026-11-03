import json,urllib.parse,sys,pathlib,hashlib
sys.path.insert(0,'scripts')
from enrich_polities import load_many,label
from prepare_flags import get,plain
root=pathlib.Path('.');path=root/'public/data/portraits.json';data=json.loads(path.read_text(encoding='utf-8'))
q={'action':'query','titles':'Óscar Carmona|Francisco Craveiro Lopes|Américo Tomás','prop':'pageprops','format':'json','redirects':1}
result=json.loads(get('https://pt.wikipedia.org/w/api.php?'+urllib.parse.urlencode(q)));mapping={p['title']:p.get('pageprops',{}).get('wikibase_item')for p in result['query']['pages'].values()};ids=[v for v in mapping.values()if v];raw=load_many(ids);names={'Óscar Carmona':'奥斯卡·卡尔莫纳','Francisco Craveiro Lopes':'弗朗西斯科·克拉韦罗·洛佩斯','Américo Tomás':'阿梅里科·托马斯'}
for title,qid in mapping.items():
 if not qid:continue
 name=names.get(title)
 if name:data['manualRulers']['Q824489|'+name]=qid
 e=raw.get(qid,{});files=[c.get('mainsnak',{}).get('datavalue',{}).get('value')for c in e.get('claims',{}).get('P18',[])if c.get('rank')!='deprecated']
 if not files:continue
 file=files[0];params={'action':'query','titles':'File:'+file,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':220,'format':'json'}
 try:
  answer=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)));info=next(p['imageinfo'][0]for p in answer['query']['pages'].values()if p.get('imageinfo'))
  target=root/'public/data/portraits'/(hashlib.sha256(file.encode()).hexdigest()[:20]+'.jpg');target.write_bytes(get(info.get('thumburl')or info['url']));meta=info.get('extmetadata',{});data['people'][qid]={'label':label(e),'file':file,'path':'/data/portraits/'+target.name,'license':plain(meta.get('LicenseShortName',{}).get('value','参见来源')),'commons':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(file),'source':'https://www.wikidata.org/wiki/'+qid+'#P18','caption':'人物肖像资料；详见原图来源'}
 except Exception as error:print('portrait not cached',qid,str(error),flush=True)
data['manualRulers']['Q13474305|弗朗西斯科·佛朗哥']='Q29179';path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8');print('Portugal portraits',mapping,flush=True)
