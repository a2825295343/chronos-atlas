"""Cache official pontiff dates and resolve historical monarchs to human IDs.
Reign dates are NOT taken from birth/death columns or unrelated positions.
"""
import json,re,time,hashlib,urllib.parse,sys
from pathlib import Path
from enrich_polities import ROOT
from enrich_modern_archives import request
CACHE=ROOT/'.local/historical-review-2026-10-31';CACHE.mkdir(exist_ok=True)

def save(name,data):
 (CACHE/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')

def resolve(titles):
 result={}
 for i in range(0,len(titles),40):
  group=titles[i:i+40];file='titles-'+hashlib.sha256('|'.join(group).encode()).hexdigest()[:16]+'.json';p=CACHE/file
  if p.exists():d=json.loads(p.read_bytes())
  else:
   params=urllib.parse.urlencode({'action':'query','format':'json','redirects':1,'prop':'pageprops','ppprop':'wikibase_item','titles':'|'.join(group)})
   d=json.loads(request('https://en.wikipedia.org/w/api.php?'+params));save(file,d);time.sleep(.5)
  query=d['query'];redirects={r['from']:r['to']for r in query.get('normalized',[])+query.get('redirects',[])};pages={r['title']:r.get('pageprops',{}).get('wikibase_item')for r in query['pages'].values()}
  for title in group:
   name=title
   for _ in range(5):name=redirects.get(name,name)
   if q:=pages.get(name):result[title]=q
  print('Resolve names',min(i+40,len(titles)),'/',len(titles),flush=True)
 return result

def entities(ids,scope):
 result={};wanted=set(ids)
 for folder,glob in [(ROOT/'.local/wikidata','*.json'),(ROOT/'.local/modern-archive/2026-10-30','*.json'),(CACHE,scope+'-*.json')]:
  for path in folder.glob(glob):
   data=json.loads(path.read_bytes())
   for q in wanted.intersection(data):
    if isinstance(data[q],dict)and data[q].get('claims'):result[q]=data[q]
 missing=sorted(wanted-result.keys())
 for i in range(0,len(missing),40):
  group=missing[i:i+40];file=scope+'-'+hashlib.sha256('|'.join(group).encode()).hexdigest()[:16]+'.json'
  params=urllib.parse.urlencode({'action':'wbgetentities','format':'json','ids':'|'.join(group),'props':'labels|claims|descriptions','languages':'zh-hans|zh|en'})
  d=json.loads(request('https://www.wikidata.org/w/api.php?'+params))['entities'];save(file,d);result.update(d);print(scope,min(i+40,len(missing)),'/',len(missing),flush=True);time.sleep(.6)
 save(scope+'.json',result);return result

def main():
 candidates=json.loads((CACHE/'list-candidates.json').read_bytes());popes=json.loads((CACHE/'pontiff-terms.json').read_bytes())
 titles=sorted({title for names in candidates.values()for title in names}|{'Pope '+p['name']for p in popes}|{'Pope','List of rulers of Austria','List of Polish monarchs','List of Hungarian monarchs','List of Bohemian monarchs','List of German monarchs'})
 ids=resolve(titles);save('resolved-titles.json',ids);people=entities(set(ids.values()),'people')
 countries=entities(['Q12548','Q577867','Q171150','Q42585','Q170174','Q66504140','Q65968','Q194355'],'countries')
 offices={v['mainsnak']['datavalue']['value']['id']for e in countries.values()for p in ['P1906','P1313']for v in e.get('claims',{}).get(p,[])if v.get('mainsnak',{}).get('datavalue',{}).get('value',{}).get('id')}
 offices.update(v['mainsnak']['datavalue']['value']['id']for e in people.values()for v in e.get('claims',{}).get('P39',[])if v.get('mainsnak',{}).get('datavalue',{}).get('value',{}).get('id'))
 entities(offices,'offices');print('Historical candidate entities',len(people),'office entities',len(offices),flush=True)
if __name__=='__main__':main()
