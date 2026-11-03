import json,hashlib,pathlib,sys,urllib.parse,urllib.request,concurrent.futures
sys.path.insert(0,'scripts')
from prepare_flags import get,year,plain
root=pathlib.Path('.');raw={}
for path in (root/'.local/wikidata').glob('*.json'):
 for q,e in json.loads(path.read_text(encoding='utf-8')).items():
  if e.get('claims'):raw[q]=e
p=root/'public/data/flags.json';data=json.loads(p.read_text(encoding='utf-8'));rows=[]
for q in ['Q884','Q971','Q865','Q13426199','Q180573','Q222','Q219','Q45']:
 for c in raw.get(q,{}).get('claims',{}).get('P41',[]):
  file=c.get('mainsnak',{}).get('datavalue',{}).get('value')
  if not isinstance(file,str)or c.get('rank')=='deprecated':continue
  qualifiers=c.get('qualifiers',{});date=lambda k:next((year(s)for s in qualifiers.get(k,[])if year(s)is not None),None)
  rows.append({'qid':q,'file':file,'from':date('P580'),'to':date('P582'),'at':date('P585'),'commons':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(file.replace(' ','_')),'source':'https://www.wikidata.org/wiki/'+q+'#P41'})
files=sorted({r['file']for r in rows});infos={}
for i in range(0,len(files),20):
 group=files[i:i+20];params={'action':'query','titles':'|'.join('File:'+f for f in group),'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':400,'format':'json','redirects':1}
 result=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)))
 for page in result.get('query',{}).get('pages',{}).values():
  if page.get('imageinfo'):infos[page['title'].removeprefix('File:')]=page['imageinfo'][0]
for row in rows:
 info=infos.get(row['file'])
 if not info:continue
 url=info.get('thumburl')or info['url'];file=root/'public/data/flags'/(hashlib.sha256(row['file'].encode()).hexdigest()[:20]+('.svg'if url.endswith('.svg')else'.png'))
 try:
  if not file.exists():file.write_bytes(get(url))
  row['path']='/data/flags/'+file.name;row['license']=plain(info.get('extmetadata',{}).get('LicenseShortName',{}).get('value','参见来源'));row['artist']=plain(info.get('extmetadata',{}).get('Artist',{}).get('value',''));q=row.pop('qid');target=data['entities'].setdefault(q,[])
  if not any(r['file']==row['file']and r['from']==row['from']and r['to']==row['to']for r in target):target.append(row)
 except Exception as e:print('Flag unavailable',str(e),flush=True)
data['count']=len({r['path']for rows in data['entities'].values()for r in rows});p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8');print('Corrected identity flag records',len(rows),'assets',data['count'],flush=True)
