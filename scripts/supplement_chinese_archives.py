"""Named Chinese monarchs from explicit reign columns, never lifespan columns.

The cached complete list is pinned by SHA in the review. Separate political
identities prevent the many Liang/Qin/Zhou homonyms from sharing ruler lists.
"""
import argparse, hashlib, json, re, subprocess, urllib.parse
import copy
from collections import defaultdict
from html.parser import HTMLParser
from prepare_ancient_rosters import RosterTables, reign
from territory_repair_stage import ROOT, read, write

TAG='chinese-archives-2026-11-01';CACHE=ROOT/'.local/chinese-archives'
SOURCE='https://en.wikipedia.org/wiki/List_of_Chinese_monarchs'
MOE='https://dict.revised.moe.edu.tw/appendix.jsp?ID=2&ver=5'
CONFIG={3:('Zhou Dynasty','周'),4:('Qin Dynasty','秦'),5:('Han Dynasty','汉'),
 6:('Cao Wei','曹魏'),7:('Shu Han','蜀汉'),8:('Eastern Wu','孙吴'),9:('Western Jin','西晋'),
 10:('Cheng Han','成汉'),11:('Former Zhao','汉赵'),12:('Later Zhao','后赵'),13:('Former Liang','前凉'),
 14:('Former Yan','前燕'),15:('Former Qin','前秦'),16:('Later Yan','后燕'),17:('Later Qin','后秦'),
 18:('Western Qin','西秦'),19:('Later Liang','后凉'),20:('Southern Liang','南凉'),21:('Northern Liang','北凉'),
 22:('Southern Yan','南燕'),23:('Western Liang','西凉'),24:('Xia','夏'),25:('Northern Yan','北燕'),
 26:('Northern Wei','北魏'),27:('Eastern Wei','东魏'),28:('Northern Qi','北齐'),29:('Western Wei','西魏'),
 30:('Northern Zhou','北周'),31:('Liu Song Dynasty','刘宋'),32:('Southern Qi','南齐'),33:('Liang Dynasty','南梁'),
 34:('Later Western Liang','西梁'),35:('Chen Dynasty','陈朝'),36:('Sui Dynasty','隋'),37:('Tang Dynasty','唐'),
 38:('Later Liang Dynasty','后梁'),39:('Later Tang','后唐'),40:('Later Jin','后晋'),41:('Later Han','后汉'),42:('Later Zhou','后周'),
 43:('Former Shu','前蜀'),44:('Southern Wu','杨吴'),45:('Southern Chu','马楚'),46:('Wuyue','吴越'),47:('Min','闽'),
 48:('Southern Han','南汉'),49:('Jingnan','荆南'),50:('Later Shu','后蜀'),51:('Southern Tang','南唐'),52:('Northern Han','北汉'),
 53:('Northern Song','宋'),54:('Liao Dynasty','辽'),55:('Western Xia','西夏'),56:('Great Jin','金')}
STATE_PAGES={'Qin':'Qin_(state)','Jin':'Jin_(Chinese_state)','Chu':'Chu_(state)','Qi':'Qi_(state)',
 'Lu':'Lu_(state)','Song':'Song_(state)','Zheng':'Zheng_(state)','Cai':'Cai_(state)','Yan':'Yan_(state)',
 'Zhao':'Zhao_(state)','Wei':'Wei_(state)','Han':'Han_(state)','Yue':'Yue_(state)','Wu':'Wu_(state)','Chen':'Chen_(state)'}
STATE_LABELS=dict(zip(STATE_PAGES,['秦','晋','楚','齐','鲁','宋','郑','蔡','燕','赵','魏','韩','越','吴','陈']))
SAFE={'Han Dynasty':'Q7209','Tang Dynasty':'Q9683','Northern Song':'Q7462','Southern Song':'Q7462',
      'Cao Wei':'Q320930','Shu Han':'Q320925','Eastern Wu':'Q274488','Qin Dynasty':'Q7183',
      'Eastern Zhou':'local:eastern-zhou','Eastern Jin':'local:eastern-jin','Qin':'Q34756','Yue':'local:yue-state',
      'Liu Song Dynasty':'Q49697'}

def chinese(text):
 return ''.join(re.findall(r'[\u3400-\u9fff]+',text.split('Other names')[0]))

def date_column(text,bc=False):
 text=text.lstrip(' |').split('|')[0]
 if re.search(r'century|\?|\bd\.',text,re.I):return None
 return reign(text,bc)

class StateLists(HTMLParser):
 def __init__(self):super().__init__();self.heading='';self.h=None;self.li=None;self.links=[];self.rows=[];self.section=False
 def handle_starttag(self,t,a):
  d=dict(a)
  if t in ['h2','h3','h4']:self.h=''
  if t=='li'and self.section:self.li='';self.links=[]
  if t=='a'and self.li is not None:
   href=d.get('href','')
   if href.startswith('./'):self.links.append(urllib.parse.unquote(href[2:]).replace('_',' '))
 def handle_data(self,d):
  if self.h is not None:self.h+=d
  if self.li is not None:self.li+=d
 def handle_endtag(self,t):
  if t in ['h2','h3','h4']and self.h is not None:
   self.heading=self.h;self.h=None
   if t=='h2':self.section=bool(re.search('ruler|monarch',self.heading,re.I))
  if t=='li'and self.li is not None:self.rows.append((self.li,self.links));self.li=None

def candidates():
 parser=RosterTables();parser.feed((CACHE/'monarchs.html').read_text(encoding='utf8'))
 headers={};out=[];reject=[];sub={}
 for row,tid in zip(parser.rows,parser.rowTables):
  if tid not in CONFIG:continue
  if any(re.match(r'^(?:Tentative )?Reign\b',c['text'],re.I)for c in row):
   dc=next(i for i,c in enumerate(row)if re.match(r'^(?:Tentative )?Reign\b',c['text'],re.I))
   nc=next((i for i,c in enumerate(row)if re.match(r'^Personal\s+name',c['text'],re.I)),0)
   headers[tid]=(nc,dc);continue
  if tid not in headers:continue
  if len({c['text']for c in row})==1:
   text=row[0]['text']
   if tid==3 and 'Eastern Zhou'in text:sub[tid]='Eastern Zhou'
   if tid==5 and 'Xin dynasty'in text:sub[tid]='Xin Dynasty'
   if tid==5 and ('Western Han'in text or'Eastern Han'in text):sub[tid]='Han Dynasty'
   if tid==5 and 'Restoration'in text:sub[tid]='Han Dynasty'
   if tid==9 and 'Eastern Jin'in text:sub[tid]='Eastern Jin'
   if tid==53 and 'Southern Song'in text:sub[tid]='Southern Song'
   continue
  nc,dc=headers[tid]
  if max(nc,dc)>=len(row):continue
  dates=date_column(row[dc]['text'],tid in [3,4]);name=sub.get(tid,CONFIG[tid][0]);prefix=CONFIG[tid][1]
  if not dates:continue
  a,b=dates
  if a>1279 or b< -841:continue
  # No legendary / long-disputed pre-841 regnal years presented as exact dates.
  a=max(a,-841);zh=chinese(row[nc]['text']);links=row[nc]['links']
  if tid==5 and '劉玄'in zh:name='Han Dynasty'
  if name=='Eastern Jin':prefix='东晋'
  if not zh or len(zh)>20:continue
  if tid==37 and a>=690 and b<=705 and '武'in zh:name='Wu Zhou'
  out.append({'country':name,'label':prefix+' '+zh,'title':links[0]if links else None,
              'from':a,'to':b,'source':SOURCE,'reignText':row[dc]['text'],'table':tid})
 for name,page in STATE_PAGES.items():
  file=CACHE/(page+'.html')
  if not file.exists():continue
  p=RosterTables();html=file.read_text(encoding='utf8');p.feed(html);heads={}
  for row,tid in zip(p.rows,p.rowTables):
   if any(re.match(r'^Reign\b',c['text'],re.I)for c in row):
    dc=next(i for i,c in enumerate(row)if re.match(r'^Reign\b',c['text'],re.I))
    nc=next((i for i,c in enumerate(row)if re.match(r'^Title\s*(?:\(Chinese\))?$',c['text'],re.I)),0)
    heads[tid]=(nc,dc);continue
   if tid not in heads:continue
   nc,dc=heads[tid]
   if max(nc,dc)>=len(row):continue
   dates=date_column(row[dc]['text'],True);zh=chinese(row[nc]['text'])
   if not dates or dates[0]< -841 or dates[1]>=0:continue
   links=row[nc]['links'];title=links[0]if links else None
   if not zh:
    # English title with no Chinese cell: preserve the named person link;
    # resolve its Chinese human label in the next stage.
    zh=STATE_LABELS[name]+'国君主（'+row[nc]['text']+'）'
   elif not zh.startswith(STATE_LABELS[name]):zh=STATE_LABELS[name]+zh
   out.append({'country':name,'label':zh,'title':title,'from':dates[0],'to':dates[1],
               'source':'https://en.wikipedia.org/wiki/'+page,'reignText':row[dc]['text']})
  p=StateLists();p.feed(html)
  for text,links in p.rows:
   # Only a stated reign/ruler-list date range, not family-tree lifespans.
   match=re.search(r'(?:ruled\s*)?(\d{3})\s*(?:BCE?)?\s*[–−—-]\s*(?:Spring\s+|Autumn\s+)?(\d{3})(?:\s*BC)?',text)
   if not match:continue
   a,b=-int(match[1]),-int(match[2])
   if not(-841<=a<=b<0):continue
   before=text[:match.start()];zh=chinese(before.split(':')[0])
   if not zh or len(zh)>25:continue
   if not zh.startswith(STATE_LABELS[name]):zh=STATE_LABELS[name]+zh
   out.append({'country':name,'label':zh,'title':links[0]if links else None,'from':a,'to':b,
               'source':'https://en.wikipedia.org/wiki/'+page,'reignText':match.group(0)})
  if name=='Yue':
   # This family tree explicitly labels the named kings' reign ranges; do not
   # apply this extraction to arbitrary trees containing birth/death dates.
   seen_cells={}
   for row in RosterTablesRows(html):
    for cell in row:
     text=cell['text'];match=re.search(r'\((?:r\.\s*)?(\d{3})\s*[─–—-]\s*(\d{3})\s*BC\)',text)
     if match and re.search(r'King|Marquis',text)and'越'in text:
      a,b=-int(match[1]),-int(match[2]);zh=chinese(text[:match.start()])
      if a<=b:seen_cells[(zh,a,b)]={'country':name,'label':zh,'title':cell['links'][0]if cell['links']else None,
            'from':a,'to':b,'source':'https://en.wikipedia.org/wiki/'+page,'reignText':match.group(0)}
   out.extend(seen_cells.values())
 # Explicitly reviewed Wu reigns; the family tree's preceding '?' is an
 # unknown birth date, never used as either boundary of a reign.
 for zh,a,b,title in [('寿梦',-586,-561,'Shoumeng'),('诸樊',-561,-548,'Zhufan'),('余祭',-548,-531,'Yuji (king of Wu)'),
                      ('余眛',-531,-527,'Yumei (king of Wu)'),('吴王僚',-527,-515,'Liao (king of Wu)'),
                      ('阖闾',-515,-496,'Helü'),('夫差',-496,-473,'Fuchai')]:
  out.append({'country':'Wu','label':zh,'title':title,'from':a,'to':b,'source':'https://en.wikipedia.org/wiki/Wu_(state)','reignText':f'{a}—{b}（具名任期）'})
 unique={}
 for r in out:unique[(r['country'],r['title']or r['label'],r['from'],r['to'])]=r
 rows=list(unique.values());write('.local/chinese-archives/candidates.json',rows)
 print('Chinese named reign candidates',len(rows),'countries',len({r['country']for r in rows}),flush=True)

def RosterTablesRows(html):
 p=RosterTables();p.feed(html);return p.rows

def fetch_people():
 rows=read('.local/chinese-archives/candidates.json')
 people=read('.local/chinese-archives/verified-people.json')if(CACHE/'verified-people.json').exists()else{}
 ids=read('.local/chinese-archives/title-ids.json')if(CACHE/'title-ids.json').exists()else{}
 titles=sorted({r['title']for r in rows if r['title']and r['title']not in ids})
 for i in range(0,len(titles),35):
  group=titles[i:i+35];key=hashlib.sha1('|'.join(group).encode()).hexdigest()[:16];file=CACHE/('people-'+key+'.json')
  if not file.exists():
   query=urllib.parse.urlencode({'action':'wbgetentities','format':'json','sites':'enwiki','titles':'|'.join(group),
                                 'props':'labels|claims|sitelinks','languages':'zh-hans|zh|en','redirects':'yes'})
   result=subprocess.run(['curl.exe','--fail','--silent','--show-error','--location','--max-time','45',
                         'https://www.wikidata.org/w/api.php?'+query,'-o',str(file)],capture_output=True,text=True)
   if result.returncode:print('Deferred identity batch',i,result.stderr,flush=True);continue
  d=json.loads(file.read_bytes()).get('entities',{})
  for q,e in d.items():
   if not any(c.get('mainsnak',{}).get('datavalue',{}).get('value',{}).get('id')=='Q5'for c in e.get('claims',{}).get('P31',[])):continue
   people[q]=e;en=e.get('sitelinks',{}).get('enwiki',{}).get('title')
   if en:ids[en]=q
   for v in e.get('labels',{}).values():
    if v.get('language')=='en':ids.setdefault(v['value'],q)
  print('Chinese identities',min(i+35,len(titles)),'/',len(titles),flush=True)
 write('.local/chinese-archives/verified-people.json',people);write('.local/chinese-archives/title-ids.json',ids)

def apply():
 facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json')
 for e in facts['entities'].values():
  if 'ruler'in e.get('fields',{}):e['fields']['ruler']=[r for r in e['fields']['ruler']if r.get('supplement')!=TAG]
 labels=read('src/localization/display-names.zh.json');rows=read('.local/chinese-archives/candidates.json')
 ids=read('.local/chinese-archives/title-ids.json');people=read('.local/chinese-archives/verified-people.json');bycountry=defaultdict(list)
 original_ids={};owners=defaultdict(set)
 for file in (ROOT/'public/data/temporal').glob('*.geojson'):
  for f in json.loads(file.read_bytes())['features']:
   p=f['properties'];original_ids[p['NAME']]=p.get('qid');owners[p.get('qid')].add(p['NAME'])
 for r in rows:bycountry[r['country']].append(r)
 bycountry.setdefault('Southern Song',[]);applied=[]
 for name,reigns in bycountry.items():
  if name=='Southern Song'and not reigns:continue
  q=SAFE.get(name,'local:china-'+name.lower().replace(' ','-'))
  cur['identities'][name]=q
  label={'Eastern Zhou':'东周','Eastern Jin':'东晋','Yue':'越国','Liang Dynasty':'南梁','Later Western Liang':'西梁'}.get(name,labels.get(name,name))
  if name in STATE_LABELS:label=STATE_LABELS[name]+'国'
  labels[name]=label
  e=facts['entities'].setdefault(q,{'label':label,'en':name,'description':'按具体政权与在位区间补录的中国历史档案。','fields':{}})
  original=original_ids.get(name)
  if original!=q and len(owners.get(original,[]))==1:
   for field,records in facts['entities'].get(original,{}).get('fields',{}).items():
    if field not in ['ruler','headOfGovernment','founded','dissolved']and not e['fields'].get(field):
     e['fields'][field]=copy.deepcopy(records)
  e['label']=label;facts['labels'][q]=label
  rs=e['fields'].setdefault('ruler',[])
  for r in reigns:
   pid=ids.get(r['title']);pe=people.get(pid,{})
   title=r['label']
   human_label=next((pe.get('labels',{}).get(k,{}).get('value')for k in ['zh-hans','zh']if pe.get('labels',{}).get(k)),None)
   if human_label and re.search(r'[\u3400-\u9fff]',human_label):title=human_label
   if re.search('[A-Za-z]',title):
    fixes={('Qi',-686):'齐无知',('Qi',-643):'齐无亏',('Qi',-613):'齐君舍',('Qi',-383):'齐侯剡',('Qi',-264):'齐王田建',
           ('Lu',-806):'鲁伯御',('Lu',-542):'鲁子野'}
    title=fixes.get((name,r['from']),title)
    lu={'Xiao':'孝','Hui':'惠','Zhao':'昭','Dao':'悼','Yuan':'元','Mu':'穆','Gong':'共','Kang':'康','Jing':'景','Ping':'平','Wen II':'文','Qing':'顷'}
    if name=='Lu':
     for en,zh in lu.items():
      if 'Duke '+en+'）'in title:title='鲁'+zh+'公';break
   if re.search('[A-Za-z]',title):
    raise ValueError('Unreviewed untranslated ruler '+str(r))
   if not pid:pid='local:chinese-ruler:'+hashlib.sha1((name+'|'+str(r['title']or title)).encode()).hexdigest()[:16]
   record={'value':pid,'label':title,'from':r['from'],'to':r['to'],'at':None,'kind':'person',
           'roleLabel':label+'统治者','citation':[r['source']],'supplement':TAG,'derived':True,
           'approximate':r['from']< -221,'dateSource':'明确在位栏／具名君主序列',
           'inference':'取具名在位区间，未用生卒年；先秦纪年与短期争位存在异说，交接年可并列。'}
   rs.append(record);facts['labels'][pid]=title;applied.append({'country':name,'identity':q,**record})
  lo=min((r['from']for r in reigns),default=0);hi=max((r['to']for r in reigns),default=0)
  overview={
   'government':'诸侯君主制；宗法、卿大夫与封邑关系随时代变化'if name in STATE_LABELS or lo< -221 else'君主制与官僚政治；中央、地方及军事集团的权力随时期变化',
   'religion':'祖先祭祀、宗庙社稷与地方祭祀；不等同现代意义的统一国教'if hi<0 else'祖先祭祀及国家礼制；佛教、道教与地方信仰的地位依时代和地区变化，并非统一国教',
   'ideology':'宗法礼制与诸侯政治；战国时期儒、墨、法、道等思想并存'if hi<0 else'皇帝正统与官僚治理；儒学、礼制及宗教思想的政治地位不断变化'}
  if name in ['Zhou Dynasty','Eastern Zhou']:overview['government']='周王权与宗法分封体系；诸侯、卿族和地方势力的实际权力随时期变化'
  for field,text in overview.items():
   if not e['fields'].get(field):e['fields'][field]=[{'value':text,'label':text,'from':lo,'to':hi,'at':None,'citation':[SOURCE],'derived':True,'supplement':TAG}]
  capitals={'Eastern Zhou':'洛邑（今洛阳一带）','Eastern Jin':'建康','Liang Dynasty':'建康；侯景之乱后朝廷分立并曾迁江陵',
            'Later Western Liang':'江陵','Sui Dynasty':'大兴城、洛阳（两京地位依时期变化）','Later Zhao':'襄国、邺（分期迁都）',
            'Former Qin':'长安','Southern Liang':'乐都及西平一带（分期迁治）','Former Liang':'姑臧',
            'Former Yan':'龙城、蓟、邺（分期迁都）','Later Yan':'中山、龙城（分期迁都）','Later Qin':'长安',
            'Northern Liang':'张掖、姑臧（分期迁都）','Southern Yan':'广固','Western Liang':'敦煌、酒泉（分期迁治）',
            'Northern Yan':'龙城','Xia':'统万城','Cheng Han':'成都','Northern Qi':'邺',
            'Eastern Wei':'邺','Western Wei':'长安','Northern Zhou':'长安'}
  if name in capitals and not e['fields'].get('capital'):
   text=capitals[name];e['fields']['capital']=[{'value':text,'label':text,'from':None,'to':None,'at':None,'citation':[SOURCE],'supplement':TAG}]
  state_capitals={
   'Jin':[(-841,-586,'绛（早期都城沿革另有研究）'),(-585,-376,'新田（新绛，今侯马一带）')],
   'Qin':[(-677,-384,'雍'),(-383,-351,'栎阳'),(-350,-221,'咸阳')],
   'Qi':[(-841,-221,'临淄一带（早期称营丘）')], 'Lu':[(-841,-249,'曲阜')],
   'Zheng':[(-769,-375,'新郑')], 'Song':[(-841,-286,'商丘')], 'Chen':[(-841,-479,'宛丘')],
   'Cai':[(-841,-531,'上蔡'),(-530,-494,'新蔡'),(-493,-447,'州来（下蔡）')],
   'Han':[(-375,-230,'新郑')], 'Zhao':[(-386,-222,'邯郸')], 'Yan':[(-600,-222,'蓟')],
   'Wei':[(-445,-365,'安邑'),(-364,-339,'安邑—大梁迁都阶段（具体年份有异说）'),(-338,-225,'大梁')],
   'Chu':[(-706,-279,'郢；早期迁徙与都城定位有研究分歧'),(-278,-254,'陈（陈郢）'),(-253,-242,'钜阳'),(-241,-223,'寿春')],
   'Wu':[(-514,-473,'姑苏')]}
  if name in state_capitals:
   capital_source={'Jin':'https://klast.sdu.edu.cn/info/1031/1673.htm',
                   'Wei':'https://www.cssn.cn/skgz/bwyc/202208/t20220803_5464162.shtml'}.get(name,'https://en.wikipedia.org/wiki/'+STATE_PAGES[name])
   e['fields']['capital']=[{'value':text,'label':text,'from':a,'to':b,'at':None,'citation':[capital_source],
                           'supplement':TAG,'approximate':('异说'in text or'分歧'in text)}for a,b,text in state_capitals[name]]
  e['rulerScopeNote']='按政权分别补录具名统治者；同年交接、短期称帝、追尊、摄政与割据可能有不同口径。未以一位君主覆盖全部中国。'
 # Preserve existing dated Han/Tang/Song manual rosters; the new rows supply
 # other dynasties and machine-readable person identities, not duplicate cards.
 cur['identities']['Southern Song']='Q7462';cur['identities']['Eastern Zhou']='local:eastern-zhou'
 for f in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  d=read(f);d.update({n:labels[n]for n in bycountry if n in labels});d.update({'Eastern Zhou':'东周','Eastern Jin':'东晋','Yue':'越国'});write(f,d)
 write('public/data/curated-facts.json',cur);write('public/data/polity-facts.json',facts)
 write('public/data/chinese-archives-review.json',{'revision':TAG,'records':applied,
       'summary':{'reignRecords':len(applied),'polities':len(bycountry),'verifiedPeople':len(people)},
       'sourceSha256':hashlib.sha256((CACHE/'monarchs.html').read_bytes()).hexdigest(),
       'sources':[SOURCE,MOE],'limitations':['先秦纪年及少数争位君主有异说。','未解析出的任期不以生卒年或邻国君主填充。','政体与思想为分期制度概览，非现代国教或政党分类。']})
 print('Chinese archives applied',len(applied),'polities',len(bycountry),'people',len(people),flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['candidates','fetch','apply']);args=parser.parse_args()
 {'candidates':candidates,'fetch':fetch_people,'apply':apply}[args.stage]()
