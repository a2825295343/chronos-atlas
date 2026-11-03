"""Fill verified archive gaps from exact office terms, institutions and vacancies."""
import json,re,urllib.parse,hashlib
from enrich_modern_archives import ROOT,CACHE,REVIEW,REVIEW_YEAR,read,write,request,entities,qvalues
from enrich_polities import simplify,label
CANDIDATES=[('Q27','ruler','Michael D. Higgins'),('Q730','ruler','Chan Santokhi'),('Q403','ruler','Aleksandar Vučić'),('Q858','ruler','Bashar al-Assad'),('Q717','ruler','Nicolás Maduro'),('Q30','ruler','Joe Biden'),('Q1007','ruler','Horta Inta-A'),('Q1007','headOfGovernment','Ilídio Vieira Té'),('Q28','ruler','László Kövér')]
CANDIDATES += [('Q817','headOfGovernment','Ahmad Al-Abdullah Al-Sabah'),('Q757','headOfGovernment','Godwin Friday'),('Q757','headOfGovernment','Ralph Gonsalves'),('Q403','headOfGovernment','Ana Brnabić'),('Q403','headOfGovernment','Ivica Dačić'),('Q403','headOfGovernment','Miloš Vučević'),('Q1028','headOfGovernment','Aziz Akhannouch'),('Q1019','headOfGovernment','Christian Ntsay'),('Q657','headOfGovernment','Succès Masra'),('Q657','headOfGovernment','Allamaye Halina'),('Q858','headOfGovernment','Hussein Arnous'),('Q858','headOfGovernment','Mohammad Ghazi al-Jalali'),('Q858','headOfGovernment','Mohammed al-Bashir')]
CANDIDATES += [('Q945','headOfGovernment','Victoire Tomegah Dogbé'),('Q686','headOfGovernment','Charlot Salwai'),('Q686','headOfGovernment','Jotham Napat'),('Q851','headOfGovernment','Mohammed bin Salman')]
EXTRA_OFFICES={'Q858':'Prime Minister of Syria'}
EXTRA_SOURCES={'Q817':'https://pm.gov.kw/en/administration/prime-minister/','Q757':'https://pmoffice.gov.vc/pmoffice/images/stories/Speeches/ADDRESS_TO_THE_8TH_SUMMIT_OF_CELAC_FINAL.pdf','Q403':'https://www.srbija.gov.rs/vest/en/222196/new-government-of-serbia-elected.php'}
def cached(scope):
 result={}
 for p in CACHE.glob(scope+'-*.json'):result.update(json.loads(p.read_bytes()))
 return result
def add(fields,field,row):
 rows=fields.setdefault(field,[]);key=(row['value'],row.get('from'),row.get('to'),row.get('at'))
 if key not in{(r['value'],r.get('from'),r.get('to'),r.get('at'))for r in rows}:rows.append(row);return True
 return False
def main():
 titles=[r[2]for r in CANDIDATES]+list(EXTRA_OFFICES.values())
 cache=CACHE/('supplement-identities-'+hashlib.sha256('|'.join(titles).encode()).hexdigest()[:12]+'.json')
 if cache.exists():d=json.loads(cache.read_bytes())
 else:
  query=urllib.parse.urlencode({'action':'query','format':'json','redirects':1,'prop':'pageprops','ppprop':'wikibase_item','titles':'|'.join(titles)})
  d=json.loads(request('https://en.wikipedia.org/w/api.php?'+query));cache.write_text(json.dumps(d,ensure_ascii=False),encoding='utf8')
 pages={r['title']:r.get('pageprops',{}).get('wikibase_item')for r in d['query']['pages'].values()};redirects={r['from']:r['to']for r in d['query'].get('redirects',[])};normalized={r['from']:r['to']for r in d['query'].get('normalized',[])};resolved=[]
 for country,field,title in CANDIDATES:
  name=normalized.get(title,title)
  for _ in range(5):name=redirects.get(name,name)
  q=pages.get(name)
  if q:resolved.append((country,field,title,q))
  else:print('Unresolved supplement identity',title.encode('unicode_escape').decode(),flush=True)
 humans=entities({r[3]for r in resolved},'officeholders');raw=cached('countries');offices=cached('offices');all_people=cached('officeholders');facts=read('public/data/polity-facts.json');evidence=read('public/data/modern-term-evidence.json');changes=[]
 for q,e in humans.items():facts['labels'][q]=label(e)
 # Never use an opposition-leader term as a prime-minister term.
 fields=facts['entities']['Q757']['fields']
 fields['headOfGovernment']=[r for r in fields.get('headOfGovernment',[])if r.get('office')!='Q2741536']
 evidence['records']=[r for r in evidence['records']if not(r['country']=='Q757'and r.get('office')=='Q2741536')]
 # A fresh preferred country claim must not be ended from an earlier electoral
 # term in P39. Successive terms can be recorded separately on the person.
 # Hungary has an explicitly observed successor in the same single presidency;
 # cap the predecessor at the transition year, not at an arbitrary term length.
 for row in facts['entities']['Q28']['fields'].get('ruler',[]):
  if row['value']=='Q28599854'and row.get('to')is None:
   successors=[r for r in facts['entities']['Q28']['fields']['ruler']if r.get('rank')=='preferred'and r.get('from')is not None and r['from']>row.get('from',0)]
   if successors:row.update(to=min(r['from']for r in successors),derived=True,inference='同一总统职位已有明确后继者，按交接年份补全年度上界；不推定具体离任日',dateSource='dated successor in same presidency',citation=['https://www.wikidata.org/wiki/Q28#P35'])
 for country,field,title,q in resolved:
  e=raw[country];person=humans[q]
  if 'Q5'not in qvalues(person,'P31'):raise ValueError('Resolved officeholder is not a human: '+title)
  allowed=qvalues(e,'P1906'if field=='ruler'else'P1313')
  if field=='headOfGovernment'and country in EXTRA_OFFICES:
   office=pages.get(EXTRA_OFFICES[country])
   if office:allowed.add(office)
  for claim in person.get('claims',{}).get('P39',[]):
   term=simplify(claim)
   if not term or term['value']not in allowed or term.get('from')is None:continue
   row={'value':q,'label':label(person),'from':term['from'],'to':term['to'],'at':None,'rank':'normal','derived':True,'inference':'据已核对人物的对应国家职务任期补回国家条目遗漏记录','dateSource':'office-matched P39 / '+term['value'],'office':term['value'],'citation':term['citation']or['https://www.wikidata.org/wiki/'+q+'#P39'],'verifiedThrough':REVIEW_YEAR,'reviewedAt':REVIEW}
   if country in EXTRA_SOURCES:row['citation']=list(dict.fromkeys([EXTRA_SOURCES[country],*row['citation']]))
   if add(facts['entities'][country]['fields'],field,row):changes.append({'country':country,'field':field,**row})
 # Independent official records repair missing/obsolete country claims.
 for q in ['Q686','Q851']:
  predecessor='Q16190741'if q=='Q686'else'Q367825';end=2022
  for r in facts['entities'][q]['fields'].get('headOfGovernment',[]):
   if r['value']==predecessor and r.get('from')is not None and r.get('to')is None:
    r.update(to=end,derived=True,dateSource='verified corresponding office end',inference='对应总理职务已明确结束，修正国家条目未封闭的旧任期',citation=['https://www.wikidata.org/wiki/'+predecessor+'#P39'])
 verified=[('Q817','Ahmad Al-Abdullah Al-Sabah',2024,None,'https://pm.gov.kw/en/administration/prime-minister/'),('Q757','Godwin Friday',2025,None,'https://www.gov.vc/index.php/home/cabinet'),('Q945','Victoire Tomegah Dogbé',2020,2025,'https://www.republiquetogolaise.tg/politique/2809-4672-le-chef-de-l-etat-nomme-victoire-tomegah-dogbe-premier-ministre'),('Q686','Charlot Salwai',2023,2025,'https://pmo.gov.vu/en/public-information/press-release/1065-salwai-government-marks-1-year-in-office.html'),('Q686','Jotham Napat',2025,None,'https://pmo.gov.vu/en/public-information/press-release/1079-hon-jotham-napat-elected-new-prime-minister-of-the-14th-legislature.html'),('Q851','Mohammed bin Salman',2022,None,'https://www.spa.gov.sa/2387811')]
 for country,title,a,b,source in verified:
  person=next((r[3]for r in resolved if r[0]==country and r[2]==title),None)
  if not person:raise ValueError('Unresolved verified officeholder '+title)
  row={'value':person,'label':label(humans[person]),'from':a,'to':b,'at':None,'rank':'normal','citation':[source],'verifiedThrough':REVIEW_YEAR,'reviewedAt':REVIEW}
  if add(facts['entities'][country]['fields'],'headOfGovernment',row):changes.append({'country':country,'field':'headOfGovernment',**row})
 # Where one exact office is both head of state and head of government, an
 # explicit dated term in either field can complete the other field.
 for q,e in raw.items():
  if q!='Q30'or not(qvalues(e,'P1906')&qvalues(e,'P1313')):continue
  fields=facts['entities'][q]['fields']
  for origin,target in [('headOfGovernment','ruler'),('ruler','headOfGovernment')]:
   for r in list(fields.get(origin,[])):
    if r.get('from')is None and r.get('at')is None:continue
    row={**r,'derived':True,'inference':'国家元首与政府首脑明确对应同一职务，按已有任期补全另一角色','dateSource':'matching P1906 and P1313 office'}
    if add(fields,target,row):changes.append({'country':q,'field':target,**row})
 # A dated office definition can establish that a president is also the head
 # of government. Require exactly one identical office in both roles in that
 # year; a shared historical office among several candidates is insufficient.
 def office_set(e,prop,y):
  result=set()
  for claim in e.get('claims',{}).get(prop,[]):
   r=simplify(claim)
   if r and(r.get('from')is None or r['from']<=y)and(r.get('to')is None or y<=r['to'])and(r.get('at')is None or y==r['at']):result.add(r['value'])
  return result
 for q,e in raw.items():
  fields=facts['entities'][q]['fields']
  fields['headOfGovernment']=[r for r in fields.get('headOfGovernment',[])if r.get('dateSource')!='unique matching P1906 and P1313 office']
  for y in [2024,2025,2026]:
   a,b=office_set(e,'P1906',y),office_set(e,'P1313',y)
   active_heads={r['value']for r in fields.get('ruler',[])if(r.get('from')is None or r['from']<=y)and(r.get('to')is None or y<=r['to'])and(r.get('at')is None or r['at']==y)and(r.get('from')is not None or r.get('at')is not None)}
   if any((r.get('from')is not None or r.get('at')is not None)and(r.get('from')is None or r['from']<=y)and(r.get('to')is None or y<=r['to'])and(r.get('at')is None or r['at']==y)and r['value']not in active_heads for r in fields.get('headOfGovernment',[])):continue
   if len(a)!=1 or a!=b:continue
   for h in list(fields.get('ruler',[])):
    if h.get('from')is None and h.get('at')is None:continue
    if not((h.get('from')is None or h['from']<=y)and(h.get('to')is None or y<=h['to'])and(h.get('at')is None or h['at']==y)):continue
    row={**h,'from':None,'to':None,'at':y,'derived':True,'inference':'该年国家元首与政府首脑唯一对应同一职务，依据明确的角色定义补全兼任关系；未虚构独立任期','dateSource':'unique matching P1906 and P1313 office','citation':['https://www.wikidata.org/wiki/'+q+'#P1906','https://www.wikidata.org/wiki/'+q+'#P1313']}
    if add(fields,'headOfGovernment',row):changes.append({'country':q,'field':'headOfGovernment',**row})
 # Syria's 2025 transitional arrangement has a president-led executive with
 # no separate prime minister. This is a sourced institutional change, not an
 # arbitrary assignment from the president's name.
 for h in facts['entities']['Q858']['fields'].get('ruler',[]):
  if h['value']!='Q7934206':continue
  row={**h,'from':2025,'to':None,'at':None,'derived':True,'inference':'2025年过渡宪制取消独立总理职位，由总统领导行政机关；按已核定制度安排补全角色','dateSource':'2025 transitional executive arrangement','citation':['https://www.euaa.europa.eu/coi/syria/2025/country-focus/1-state-structure-and-governance/11-separation-powers-and-government-formation']}
  if add(facts['entities']['Q858']['fields'],'headOfGovernment',row):changes.append({'country':'Q858','field':'headOfGovernment',**row})
 # Institutional continuity and genuine presidential vacancies are states of
 # office, not missing people. Sources explicitly establish these arrangements.
 collective={'value':'Q30917','label':'瑞士联邦委员会（集体国家元首及政府）','from':1848,'to':None,'at':None,'kind':'collective','citation':['https://www.admin.ch/en/federal-presidency-role'],'verifiedThrough':REVIEW_YEAR,'reviewedAt':REVIEW}
 for field in ['ruler','headOfGovernment']:add(facts['entities']['Q39']['fields'],field,collective)
 vacancy={'value':'local:lebanon-presidential-vacancy','label':'总统职位空缺（部长会议代行相关职权）','from':2022,'to':2024,'at':None,'kind':'vacancy','citation':['https://2021-2025.state.gov/reports/2024-investment-climate-statements/lebanon/'],'verifiedThrough':REVIEW_YEAR,'reviewedAt':REVIEW}
 add(facts['entities']['Q822']['fields'],'ruler',vacancy)
 inventory=read('.local/modern-polities.json')
 for r in inventory:
  if r['category']!='territory'or not r.get('sovereignQid'):continue
  own=facts['entities'].get(r['qid'],{}).get('fields',{});parent=facts['entities'].get(r['sovereignQid'],{}).get('fields',{})
  for p in parent.get('ruler',[]):
   if p.get('from')is None and p.get('at')is None:continue
   row={**p,'derived':True,'inference':'按明确的海外领地所属关系补充主权方国家元首；不代替当地总督或政府首脑','dateSource':'territory sovereign relationship / '+r['sovereignQid']}
   if add(own,'ruler',row):changes.append({'country':r['qid'],'field':'ruler',**row})
 # The latest independent observed leadership record fills an otherwise missing
 # 2026 entry; no unverified historical start date is invented.
 cia='https://www.cia.gov/resources/world-leaders/foreign-governments/guinea-bissau'
 for field,title,name in [('ruler','Horta Inta-A','奥尔塔·因塔阿（过渡总统）'),('headOfGovernment','Ilídio Vieira Té','伊利迪奥·维埃拉·特（总理）')]:
  q=next((r[3]for r in resolved if r[2]==title),'local:guinea-bissau-'+field)
  row={'value':q,'label':name,'from':None,'to':None,'at':2026,'rank':'preferred','citation':[cia],'verifiedThrough':REVIEW_YEAR,'reviewedAt':REVIEW,'observationDate':'2026-06-04'}
  if add(facts['entities']['Q1007']['fields'],field,row):changes.append({'country':'Q1007','field':field,**row})
 # Keep one current-year observed government, rather than presenting a stale
 # open-ended predecessor as still in office in that same observed year.
 for field in ['ruler','headOfGovernment']:
  for row in facts['entities']['Q1007']['fields'].get(field,[]):
   if row.get('at')is None and row.get('to')is None and row.get('from')is not None and row['from']<2026:
    row.update(to=2025,derived=True,inference='独立来源已记录2026年后继者，旧条目未记终止；以2025年为年度展示上界，不声称精确离任日',dateSource='2026 observed successor',citation=list(dict.fromkeys([*(row.get('citation')or[]),cia])))
 # Curated display transliterations do not change the person identifier.
 translations=read('src/localization/modern-person-names.zh.json')
 facts['labels'].update(translations)
 for entity in facts['entities'].values():
  for field in ['ruler','headOfGovernment']:
   for r in entity.get('fields',{}).get(field,[]):
    if r['value']in translations:r['label']=translations[r['value']]
 # Prefer the verified official presidency source over an inherited reference
 # that points to a predecessor's biography.
 for r in facts['entities']['Q40']['fields'].get('ruler',[]):
  if r['value']=='Q78869':r['citation']=['https://www.bundespraesident.at/en/index']
 # Friday's dated succession closes the preceding prime-minister term.
 for r in facts['entities']['Q757']['fields'].get('headOfGovernment',[]):
  if r['value']=='Q57800'and r.get('from')is not None and r.get('to')is None:r.update(to=2025,citation=['https://www.nbcsvg.com/2025/11/28/pm-designate-dr-godwin-friday-to-be-worn-in-as-this-countrys-fifth-prime-minister/'])
 # Surface contradictory end-date evidence instead of presenting an
 # unclosed country claim as independently verified current leadership.
 for country,e in raw.items():
  for field,prop in [('ruler','P1906'),('headOfGovernment','P1313')]:
   allowed=qvalues(e,prop)
   for row in facts['entities'][country]['fields'].get(field,[]):
    row.pop('reviewAfter',None);row.pop('reviewNote',None)
    if row.get('from')is None or row.get('to')is not None:continue
    terms=[t for c in all_people.get(row['value'],{}).get('claims',{}).get('P39',[])if(t:=simplify(c))and t['value']in allowed and t.get('from')is not None]
    if terms and all(t.get('to')is not None for t in terms):
     end=max(t['to']for t in terms)
     if end<REVIEW_YEAR:row.update(reviewAfter=end,reviewNote=f'国家条目未记终止，但人物对应职务记录截至{end}年；可能存在遗漏任期或职务转换，尚需独立核定，不能据此断言仍任职。')
 facts['modernReview']['supplementedTerms']=len(changes);write('public/data/polity-facts.json',facts);evidence['records'].extend(changes);evidence['specialOfficeStates']=[collective,vacancy];write('public/data/modern-term-evidence.json',evidence)
 print('Supplemented/reconciled terms',len(changes),flush=True)
if __name__=='__main__':main()
