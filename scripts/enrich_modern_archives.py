"""Refresh modern state archives and derive terms only from matching offices.
The dated snapshot cache is separate from older enrichment caches. Every inferred
date retains its P39/country/office evidence and is bounded by the review year.
"""
import argparse,concurrent.futures,hashlib,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error,sys
from enrich_polities import ROOT,PROPS,simplify,label,CC
REVIEW='2026-10-30';REVIEW_YEAR=2026;CACHE=ROOT/'.local/modern-archive'/REVIEW;CACHE.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def request(url):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'GuanlanAtlas/1.4 (local educational historical atlas)'}),timeout=40)as r:return r.read()
  except urllib.error.HTTPError as error:
   if error.code==429:
    if attempt==2:raise
    delay=min(60,max(20,int(error.headers.get('Retry-After','60'))));print('Source rate limit; retry after',delay,'seconds',flush=True);time.sleep(delay);continue
   if attempt==2:raise
   time.sleep(3+attempt*2)
  except Exception:
   if attempt==2:raise
   time.sleep(2+attempt*2)
def entities(ids,scope,props='labels|descriptions|claims'):
 ids=sorted(set(q for q in ids if re.fullmatch(r'Q\d+',q or '')));result={}
 for cached in CACHE.glob(scope+'-*.json'):
  for q,e in json.loads(cached.read_bytes()).items():
   if q in ids:result[q]=e
 ids=[q for q in ids if q not in result]
 if result:print(scope,'reused cached entities',len(result),flush=True)
 for i in range(0,len(ids),40):
  group=ids[i:i+40];path=CACHE/(scope+'-'+hashlib.sha256((props+'|'.join(group)).encode()).hexdigest()[:16]+'.json')
  if path.exists():data=json.loads(path.read_bytes())
  else:
   params=urllib.parse.urlencode({'action':'wbgetentities','ids':'|'.join(group),'props':props,'languages':'zh-hans|zh|en','format':'json'})
   data=json.loads(request('https://www.wikidata.org/w/api.php?'+params))['entities'];path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8');time.sleep(1.6)
  result.update(data);print(scope,min(i+40,len(ids)),'/',len(ids),flush=True)
 return result
def value(c):return c.get('mainsnak',{}).get('datavalue',{}).get('value')
def qvalues(e,prop):return {v.get('id')for c in e.get('claims',{}).get(prop,[])if c.get('rank')!='deprecated'and isinstance(v:=value(c),dict)and v.get('id')}
def entity_fields(e):
 return {field:rows for prop,field in PROPS.items()if(rows:=[s for c in e.get('claims',{}).get(prop,[])if(s:=simplify(c))])}
def valid_qualified(r):return r.get('from')is not None or r.get('to')is not None or r.get('at')is not None
def enrich():
 inventory=read('.local/modern-polities.json');applicable=[r for r in inventory if r['category']!='non-state'];ids={r['qid']for r in applicable}|{r['sovereignQid']for r in applicable if r.get('sovereignQid')}
 raw=entities(ids,'countries');people=set();offices=set()
 for q,e in raw.items():
  for field in ['P35','P6']:
   for c in e.get('claims',{}).get(field,[]):
    s=simplify(c)
    if s and isinstance(s['value'],str)and s['value'].startswith('Q'):
     modern=any((s.get('from')is None or s['from']<=y)and(s.get('to')is None or y<=s['to'])and(s.get('at')is None or y==s['at'])for y in [2024,2026])
     if not valid_qualified(s)or modern:people.add(s['value'])
  offices|=qvalues(e,'P1906')|qvalues(e,'P1313')
 print('Officeholders to inspect',len(people),'offices',len(offices),flush=True)
 humans=entities(people,'officeholders');office_data=entities(offices,'offices')
 data=read('public/data/polity-facts.json');derived=[];country_parents={r['qid']:r.get('sovereignQid')for r in applicable}
 # Labels from fresh country, person, and office entities supplement existing
 # translations; labels for unrelated historical facts remain untouched.
 combined={**raw,**humans,**office_data};data['labels'].update({q:label(e)for q,e in combined.items()})
 refs=set()
 for q,e in raw.items():
  fields=entity_fields(e);parent=country_parents.get(q)
  for field,prop,office_prop in [('ruler','P35','P1906'),('headOfGovernment','P6','P1313')]:
   allowed=qvalues(e,office_prop)
   if field=='ruler'and parent in raw:allowed|=qvalues(raw[parent],office_prop)
   target={q}|({parent}if field=='ruler'and parent else set());rows=[]
   for c in e.get('claims',{}).get(prop,[]):
    r=simplify(c)
    if not r:continue
    person=humans.get(r['value'],{});is_human='Q5'in qvalues(person,'P31')
    if valid_qualified(r):
     # Retain source date qualifiers, including turnover years with two people.
     r.update(verifiedThrough=REVIEW_YEAR,reviewedAt=REVIEW);rows.append(r);continue
    matches=[]
    for pc in person.get('claims',{}).get('P39',[]):
     term=simplify(pc)
     if not term or term.get('from')is None:continue
     office=term['value'];jurisdictions=qvalues(office_data.get(office,{}),'P1001')|qvalues(office_data.get(office,{}),'P17')
     if office not in allowed:continue
     # An exact matching office is essential; another job by
     # the same person must never become a term as this country's ruler.
     row={**r,'from':term['from'],'to':term['to'],'at':None,'derived':True,'dateSource':'office-matched P39 / '+str(office),'inference':'据同一人物所任同一国家对应职务的任期补全，并非凭任期长度猜测','citation':term['citation']or['https://www.wikidata.org/wiki/'+str(r['value'])+'#P39'],'office':office,'verifiedThrough':REVIEW_YEAR,'reviewedAt':REVIEW}
     deaths=[simplify(dc)['value']for dc in person.get('claims',{}).get('P570',[])if simplify(dc)]
     if row['to']is None and deaths and isinstance(deaths[0],int):row['to']=deaths[0];row['inference']+='；未记终止时以已知去世年为上界'
     matches.append(row);derived.append({'country':q,'field':field,**row})
    if matches:rows.extend(matches)
    else:
     # No invented start date: preserve the unscoped source as background only.
     r.update(reviewedAt=REVIEW);rows.append(r)
   fields[field]=list({(r['value'],r.get('from'),r.get('to'),r.get('at')):r for r in rows}.values())
  # Supplement fields without replacing carefully sourced historical terms.
  old=data['entities'].get(q,{});old_fields=old.get('fields',{})
  for field in ['ruler','headOfGovernment']:
   fresh=fields[field];keys={(r['value'],r.get('from'),r.get('to'),r.get('at'))for r in fresh}
   fresh.extend(r for r in old_fields.get(field,[])if r.get('dateSource')not in ['office-matched P39 end date','matching P1906 and P1313 office']and valid_qualified(r)and(r['value'],r.get('from'),r.get('to'),r.get('at'))not in keys and r.get('to')is not None and r['to']<2024)
  desc=e.get('descriptions',{});description=next((desc[k]['value']for k in ['zh-hans','zh','en']if k in desc),'')
  data['entities'][q]={'label':label(e),'en':e.get('labels',{}).get('en',{}).get('value',''),'description':CC.convert(description),'fields':fields,'reviewedAt':REVIEW}
  refs.update(r['value']for rs in fields.values()for r in rs if isinstance(r['value'],str)and re.fullmatch(r'Q\d+',r['value']))
 missing=refs-data['labels'].keys();labels=entities(missing,'references','labels')if missing else {};data['labels'].update({q:label(e)for q,e in labels.items()})
 for q in raw:
  for rows in data['entities'][q]['fields'].values():
   for r in rows:r['label']=data['labels'].get(str(r['value']),str(r['value']))
 data['modernReview']={'date':REVIEW,'countries':len(raw),'derivedTerms':len(derived),'method':'Exact office/jurisdiction matching, dated qualifiers and review-year bound'}
 write('public/data/polity-facts.json',data);write('public/data/modern-term-evidence.json',{'reviewedAt':REVIEW,'policy':'仅按明确对应职务任期补齐；保留来源和推定说明，不跨无依据的空缺插值','records':derived})
 print('Updated modern archives',len(raw),'derived terms',len(derived),flush=True)
def main():enrich()
if __name__=='__main__':main()
