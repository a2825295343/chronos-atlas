"""Named ancient/medieval ruler rosters with separate reign columns.
Birth/death columns are never parsed as reigns. Exact P39 terms take precedence;
the explicit named Reign column is a marked fallback, including BCE handling.
"""
import argparse,json,re,sys,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
from prepare_global_archive_review import ROOT,human,fetch
from supplement_historical_rulers import Tables
from enrich_polities import simplify,label
CACHE=ROOT/'.local/ancient-roster-review';CACHE.mkdir(exist_ok=True)
CONFIG=[
 ('List_of_Roman_emperors',['Q2277'],-27,394,r'roman emperor'),
 ('List_of_Byzantine_emperors',['Q12544','Q112039853'],395,1453,r'byzantine emperor|eastern roman emperor|roman emperor'),
 ('List_of_Achaemenid_monarchs',['Q389688'],-550,-330,r'king of kings|persia|achaemenid'),
 ('List_of_Sasanian_monarchs',['Q83891'],224,651,r'king of kings|persia|sasan'),
 ('Ptolemaic_dynasty',['Q2320005'],-305,-30,r'pharaoh|egypt|ptolema'),
 ('List_of_Seleucid_rulers',['Q705904'],-305,-63,r'seleucid|king of syria'),
 ('Maurya_Empire',['Q62943'],-322,-185,r'maurya|emperor of india'),
 ('Gupta_Empire',['Q11774'],320,550,r'gupta'),
 ('List_of_Chola_emperors',['Q6806806'],848,1279,r'chola'),
 ('List_of_rulers_of_the_Delhi_Sultanate',[],1206,1526,r'sultan of delhi'),
 ('List_of_Mughal_emperors',['Q33296'],1526,1857,r'mughal'),
 ('List_of_Vijayanagara_emperors',['Q167639'],1336,1646,r'vijayanagara'),
 ('List_of_Safavid_monarchs',['Q161205'],1501,1736,r'safavid|shah of iran|shah of persia'),
 ('List_of_emperors_of_Ethiopia',['Q207521','Q115'],1270,1974,r'emperor of ethiopia'),
 ('Mansa_(title)',['Q184536'],1235,1600,r'mansa|mali'),
 ('Sapa_Inca',['Q28573'],1200,1572,r'sapa inca|inca emperor'),
 ('List_of_rulers_of_Tenochtitlan',['Q2608489'],1375,1521,r'tlatoani|tenochtitlan|aztec'),
 ('List_of_rulers_of_the_Kingdom_of_Kongo',['local:kingdom-of-kongo'],1390,1884,r'kongo'),
 ('List_of_Obas_of_Benin',['local:kingdom-of-benin'],1200,1897,r'oba of benin|benin'),
 ('List_of_monarchs_of_Sri_Lanka',['local:kingdom-of-kotte','local:kingdom-of-kandy'],1412,1815,r'kotte|kandy'),
]
class RosterTables(Tables):
 def __init__(self):super().__init__();self.serial=0;self.table=0;self.rowTables=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=='table':self.serial+=1;self.table=self.serial
  if t=='a':
   href=d.get('href','')
   if href.startswith('./'):href='https://en.wikipedia.org/wiki/'+href[2:]
   elif href.startswith('/wiki/'):href='https://en.wikipedia.org'+href
   d['href']=href
   if href.startswith('https://en.wikipedia.org/wiki/')and not d.get('title'):d['title']=urllib.parse.unquote(href.split('/wiki/',1)[1].split('#',1)[0]).replace('_',' ')
  super().handle_starttag(t,list(d.items()))
 def handle_endtag(self,t):
  before=len(self.rows);super().handle_endtag(t)
  if len(self.rows)>before:self.rowTables.append(self.table)
def write(name,d):(CACHE/name).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def request(url):
 req=urllib.request.Request(url,headers={'User-Agent':'GuanlanAtlas/1.6 educational historical research'})
 with urllib.request.urlopen(req,timeout=45)as r:return r.read()
def reign(text,bc=False):
 s=re.sub(r'\[[^]]*\]|\([^)]*\)',' ',text)
 months='January|February|March|April|May|June|July|August|September|October|November|December'
 s=re.sub(r'\b\d{1,2}\s+(?:'+months+r')\b',' ',s,flags=re.I)
 s=re.sub(r'\b(?:'+months+r')\s+\d{1,2},?\s+(?=\d)',' ',s,flags=re.I)
 s=re.sub(r'\b(?:'+months+r')\b',' ',s,flags=re.I)
 matches=re.findall(r'(?:(BCE?|AD|CE)\s*)?(?<!\d)(\d{1,4})(?!\d)(?:\s*(BCE?|AD|CE))?',s,re.I)
 if not matches:return None
 if len(matches)>2:return None
 defaultbc=bc or(bool(re.search(r'\bBCE?\b',s,re.I))and not re.search(r'\bAD\b|\bCE\b',s,re.I))
 values=[]
 for pre,n,post in matches:
  era=(pre or post).upper();y=int(n)
  if y==0:return None
  values.append(-y if era.startswith('BC')or(not era and defaultbc)else y)
 a,b=(values[0],values[-1])
 return(a,b)if a<=b else None
def main():
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['download','fetch','apply']);args=parser.parse_args()
 if args.stage=='download':
  candidates=[];failures=[]
  for page,countries,lo,hi,office in CONFIG:
   p=CACHE/(page+'.html')
   if not p.exists():
    try:p.write_bytes(request('https://en.wikipedia.org/api/rest_v1/page/html/'+page));time.sleep(3)
    except Exception as e:
     failures.append({'page':page,'error':str(e)});print('Deferred roster',page,str(e),flush=True)
     if isinstance(e,urllib.error.HTTPError)and e.code==429:break
     continue
   table=RosterTables();table.feed(p.read_text(encoding='utf8'));headers={}
   for row,tid in zip(table.rows,table.rowTables):
    datecols=[i for i,c in enumerate(row)if re.match(r'^(reign|ruled|rule|regnal years)(\b|$)',c['text'],re.I)and len(c['text'])<80]
    if datecols:headers[tid]=datecols;continue
    links=list(dict.fromkeys(t for c in row[:2]for t in c['links']))
    if not links:continue
    text=' – '.join(row[i]['text']for i in headers.get(tid,[])if i<len(row));period=reign(text,hi<0)if text else None
    if not period:continue
    a,b=period
    if a>hi or b<lo:continue
    candidates.append({'page':page,'countries':countries,'lo':lo,'hi':hi,'officePattern':office,'links':links,'from':a,'to':b,'reignText':text,'approximate':bool(re.search(r'circa|\bc\.|\?',text,re.I))})
   print('Roster read',page,'rows',len(candidates),flush=True)
  write('candidates.json',candidates);write('download-failures.json',failures);return
 candidates=json.loads((CACHE/'candidates.json').read_bytes())
 if args.stage=='fetch':
  idsfile=CACHE/'title-ids.json';ids=json.loads(idsfile.read_bytes())if idsfile.exists()else{}
  # Reuse already resolved public identities before asking the API.
  for folder in [ROOT/'.local/historical-review-2026-10-31',ROOT/'.local/postwar-review']:
   for f in folder.glob('*ids.json'):
    d=json.loads(f.read_bytes())
    if isinstance(d,dict):ids.update({k:v for k,v in d.items()if isinstance(v,str)and v.startswith('Q')})
  titles=sorted({t for row in candidates for t in row['links']}-ids.keys())
  for i in range(0,len(titles),40):
   group=titles[i:i+40];params=urllib.parse.urlencode({'action':'query','format':'json','redirects':1,'prop':'pageprops','ppprop':'wikibase_item','titles':'|'.join(group)})
   try:d=json.loads(request('https://en.wikipedia.org/w/api.php?'+params))['query']
   except urllib.error.HTTPError as e:
    if e.code!=429:raise
    print('Name endpoint rate limit: retaining resolved names and continuing with the verified subset.',flush=True);break
   redirects={r['from']:r['to']for r in d.get('normalized',[])+d.get('redirects',[])};pages={r['title']:r.get('pageprops',{}).get('wikibase_item')for r in d['pages'].values()}
   for title in group:
    n=title
    for _ in range(5):n=redirects.get(n,n)
    if pages.get(n):ids[title]=pages[n]
   write('title-ids.json',ids);print('Roster names resolved',min(i+40,len(titles)),'/',len(titles),flush=True);time.sleep(3)
  pool=json.loads((ROOT/'.local/global-archive-review/entities.json').read_bytes())
  # The global fetch helper keeps its own restartable downloaded batch cache.
  fetch({ids[t]for row in candidates for t in row['links']if t in ids},pool,'ancient-roster-people')
  positions={r['value']for row in candidates for t in row['links']if t in ids for c in pool.get(ids[t],{}).get('claims',{}).get('P39',[])if(r:=simplify(c))and isinstance(r['value'],str)}
  fetch(positions,pool,'ancient-roster-offices');write('entities.json',pool);return
 pool=json.loads((CACHE/'entities.json').read_bytes());ids=json.loads((CACHE/'title-ids.json').read_bytes());facts=read('public/data/polity-facts.json');tag='ancient-medieval-rosters-2026-10-31';terms=[];rejected=[]
 names={}
 for path in (ROOT/'public/data/temporal').glob('*.geojson'):
  for f in json.loads(path.read_bytes())['features']:
   p=f['properties'];names[p['NAME']]=p.get('qid')
 delhi={n:q for n,q in names.items()if n in ['Mamluk Dynasty','Mamluk dynasty (Delhi)','Khalji Dynasty','Khalji dynasty','Tughlaq Dynasty','Tughlaq dynasty','Sayyid Dynasty','Lodi Dynasty','Delhi Sultanate']}
 for e in facts['entities'].values():
  e['fields']['ruler']=[r for r in e['fields'].get('ruler',[])if r.get('supplement')!=tag]
 seen=set()
 for row in candidates:
  person=next((ids[t]for t in row['links']if t in ids and human(pool.get(ids[t],{}))),None)
  if not person:continue
  targets=row['countries']or list(delhi.values());exact=[]
  for c in pool[person].get('claims',{}).get('P39',[]):
   t=simplify(c)
   if not t or t['from']is None or t['to']is None:continue
   office=pool.get(t['value'],{}).get('labels',{}).get('en',{}).get('value','')
   if re.search(row['officePattern'],office,re.I)and not re.search(r'consort|crown prince|heir',office,re.I)and t['from']<=row['hi']and t['to']>=row['lo']:exact.append(t)
  dateTerms=exact or[{'from':row['from'],'to':row['to'],'value':'named-reign-column','citation':[]}]
  for country in targets:
   if country not in facts['entities']:continue
   for t in dateTerms:
    a,b=max(row['lo'],t['from']),min(row['hi'],t['to'])
    # Delhi's five houses are separate geographic identities, not five copies
    # of every sultan. Terms only apply while the source house exists.
    if country in delhi.values():
     bounds={'Sayyid Dynasty':(1414,1451),'Lodi Dynasty':(1451,1526),'Tughlaq Dynasty':(1320,1414),'Khalji Dynasty':(1290,1320),'Mamluk Dynasty':(1206,1290)}
     match=next((bounds[n]for n,q in delhi.items()if q==country and n in bounds),None)
     if not match:continue
     a,b=max(a,match[0]),min(b,match[1])
    if country=='local:kingdom-of-kotte'and not re.search(r'kotte',row['reignText'],re.I)and not exact:
     # The pan-island list combines several concurrent courts; an undifferentiated
     # table row cannot become the ruler of both Kotte and Kandy.
     continue
    if country=='local:kingdom-of-kandy'and not any(re.search(r'kandy',pool.get(t.get('value'),{}).get('labels',{}).get('en',{}).get('value',''),re.I)for t in exact):continue
    if a>b or(country,person,a,b)in seen:continue
    seen.add((country,person,a,b));record={'value':person,'label':label(pool[person]),'from':a,'to':b,'at':None,'roleLabel':facts['entities'][country]['label']+'君主','citation':['https://en.wikipedia.org/wiki/'+row['page']],'supplement':tag,'derived':True,'dateSource':'exact named P39'if exact else'explicit Reign column / named roster','inference':'采用对应君主名录中的在位栏或准确职位任期；未使用出生、去世栏。早期年代与争位可能有分歧。','approximate':row['approximate']}
    if exact:record['citation'].extend(t['citation']or['https://www.wikidata.org/wiki/'+person+'#P39'])
    facts['entities'][country]['fields'].setdefault('ruler',[]).append(record);facts['labels'][person]=record['label'];terms.append({'country':country,**record})
 write('verified-people.json',{r['value']:pool[r['value']]for r in terms});write('rejected.json',rejected)
 (ROOT/'public/data/polity-facts.json').write_text(json.dumps(facts,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 report={'reviewedAt':'2026-10-31','records':terms,'summary':{'records':len(terms),'countries':len({r['country']for r in terms}),'people':len({r['value']for r in terms})},'method':'专门君主名录候选 + 人物实体核对 + P39准确职务／明确Reign栏；出生和去世栏不作为任期。'}
 (ROOT/'public/data/ancient-roster-review.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8');print(report['summary'],flush=True)

def read(p):return json.loads((ROOT/p).read_bytes())
if __name__=='__main__':main()
