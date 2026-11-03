"""Dated leader candidates from cached rosters, verified through person entities.
The official Wikidata query service was rate-limited during this review.
Keep polity headings and role descriptions; never infer a ruler from birth dates.
"""
import json,re
from html.parser import HTMLParser
from enrich_polities import ROOT
from fetch_historical_rulers import entities,resolve
CACHE=ROOT/'.local/postwar-review'

class Lists(HTMLParser):
 def __init__(self):super().__init__();self.stack=[];self.rows=[];self.order=0
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='li':
   self.order+=1;self.stack.append({'order':self.order,'text':'','links':[]})
  if t=='a'and a.get('title')and a.get('href','').startswith('./')and self.stack and not a['title'].startswith(('File:','List of','Template:')):self.stack[-1]['links'].append(a['title'])
 def handle_data(self,s):
  if self.stack:self.stack[-1]['text']+=s
 def handle_endtag(self,t):
  if t=='li'and self.stack:self.rows.append(self.stack.pop())

def parse(path):
 parser=Lists();parser.feed(path.read_text(encoding='utf8'));country=None;role='';rows=[]
 for r in sorted(parser.rows,key=lambda r:r['order']):
  text=re.sub(r'\s+',' ',r['text']).strip();links=list(dict.fromkeys(r['links']))
  if not links:continue
  if 'complete list'in text and text.endswith(('–','—','-')):
   if not re.search(r'^(Presidents?|Prime [Mm]inisters?|Kings?|Queens?|Monarchs?|[A-Za-z -]*[Ss]ecretar(?:y|ies)|[A-Za-z -]*[Cc]hairm[ae]n|Heads? of|[A-Za-z -]*[Gg]overnors?|Co-Princes?|Sultans?|Emirs?|Popes?)\b',text):country=links[0];role=''
   else:role=text
  if not country or 'complete list'in text:continue
  for start,end in re.findall(r'\((\d{4})(?:[–—-](\d{4}|present))?\)',text):
   a=int(start);b=int(end)if end and end!='present'else(2026 if end=='present'else a)
   if a<=1955 and b>=1945:rows.append({'countryTitle':country,'personTitle':links[0],'from':a,'to':b,'text':text,'roleContext':role})
 return rows

def main():
 rows=[]
 for year in [1950,1955]:
  for r in parse(CACHE/f'leaders-{year}.html'):rows.append({**r,'rosterSource':f'https://en.wikipedia.org/wiki/List_of_state_leaders_in_{year}'})
 rows=list({tuple(r[k]for k in ['countryTitle','personTitle','from','to','text']):r for r in rows}.values())
 (CACHE/'roster-rows.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
 ids=resolve(sorted({r[k]for r in rows for k in ['countryTitle','personTitle']}))
 (CACHE/'roster-ids.json').write_text(json.dumps(ids,ensure_ascii=False),encoding='utf8')
 people=entities({ids[r['personTitle']]for r in rows if r['personTitle']in ids},'postwar-roster-people')
 (CACHE/'people.json').write_text(json.dumps(people,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 # Build office eligibility explicitly. Historical PMs cannot be replaced by
 # the country's present executive-presidency definition.
 from enrich_polities import simplify
 cached=json.loads((CACHE/'cached-entities.json').read_bytes());inventory=json.loads((CACHE/'inventory.json').read_bytes());offices={}
 aliases={'Q713750':'Q183','Q69829':'Q142','Q149805':'Q796','Q124943':'Q79','Q207991':'Q794','Q209065':'Q41','Q185682':'Q142'}
 targets={r['qid']for r in inventory if r.get('qid','').startswith('Q')}|{r['sovereignQid']for r in inventory if r.get('sovereignQid')}
 for country in sorted(targets):
  for prop,field in [('P1906','ruler'),('P1313','headOfGovernment')]:
   for c in cached.get(aliases.get(country,country),{}).get('claims',{}).get(prop,[]):
    t=simplify(c)
    if t and(t['from']is None or t['from']<=1955)and(t['to']is None or t['to']>=1945):offices.setdefault(t['value'],[]).append({'country':country,'field':field})
 extra=resolve(['Prime Minister of Indonesia','Prime Minister of Turkey']);cached.update(entities(extra.values(),'postwar-role-offices'))
 for title,country in [('Prime Minister of Indonesia','Q252'),('Prime Minister of Turkey','Q43')]:
  row={'country':country,'field':'headOfGovernment'}
  if row not in offices.setdefault(extra[title],[]):offices[extra[title]].append(row)
 (CACHE/'office-map.json').write_text(json.dumps(offices,ensure_ascii=False),encoding='utf8');(CACHE/'cached-entities.json').write_text(json.dumps(cached,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print('Postwar roster rows',len(rows),'entities',len(people),flush=True)

if __name__=='__main__':main()
