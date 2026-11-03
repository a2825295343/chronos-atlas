"""Dated European reigns, from the official pontiff list and named offices.
Keep separate Austrian branches and distinguish monarchs, regents and vacancies.
"""
import json,re,sys,urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from enrich_polities import ROOT,simplify,label
from fetch_historical_rulers import CACHE,resolve,entities,save
SOURCE='https://www.vatican.va/content/vatican/en/holy-father.html'
TAG='historical-rulers-2026-10-31'

class Tables(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None;self.carry={}
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='table':self.carry={}
  if t=='tr':self.row=[]
  if t in ['td','th']and self.row is not None:self.cell={'text':'','links':[],'rowspan':int(a.get('rowspan','1')),'colspan':int(a.get('colspan','1'))}
  if t=='br'and self.cell is not None:self.cell['text']+=' | '
  if t=='a'and self.cell is not None and a.get('title')and a.get('href','').startswith('https://en.wikipedia.org/wiki/')and ':'not in a['title']:self.cell['links'].append(a['title'])
 def handle_data(self,s):
  if self.cell is not None:self.cell['text']+=s
 def handle_endtag(self,t):
  if t in ['td','th']and self.cell is not None:
   if self.row is not None:self.cell['text']=re.sub(r'\s+',' ',self.cell['text']).strip();self.row.append(self.cell)
   self.cell=None
  if t=='tr'and self.row is not None:
   result={k:v[0]for k,v in self.carry.items()};nextcarry={k:(v[0],v[1]-1)for k,v in self.carry.items()if v[1]>1};i=0
   for cell in self.row:
    while i in result:i+=1
    for k in range(i,i+cell['colspan']):
     result[k]=cell
     if cell['rowspan']>1:nextcarry[k]=(cell,cell['rowspan']-1)
    i+=cell['colspan']
   self.carry=nextcarry;self.rows.append([result.get(i,{'text':'','links':[]})for i in range(max(result,default=-1)+1)]);self.row=None

def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def human(e):return any((s:=simplify(c))and s['value']=='Q5'for c in e.get('claims',{}).get('P31',[]))

def main():
 ids=json.loads((CACHE/'resolved-titles.json').read_bytes());extra=json.loads((CACHE/'extra-resolved.json').read_bytes());ids.update(extra)
 people=json.loads((CACHE/'people.json').read_bytes());people.update(json.loads((CACHE/'extra-people.json').read_bytes()))
 data=read('public/data/polity-facts.json');terms={};notes={};unresolved=[]
 def add(country,q,a,b,source,role,**kw):
  if not human(people.get(q,{})):raise ValueError('Not a verified human '+str(q))
  if a is None or b is None or a>b:raise ValueError('Missing/reversed term '+str(q))
  terms.setdefault(country,[]).append({'value':q,'label':label(people[q]),'from':a,'to':b,'at':None,'citation':[source],'roleLabel':role,'supplement':TAG,**kw})
 # This official list preserves Benedict IX's three separate pontificates.
 for r in json.loads((CACHE/'pontiff-terms.json').read_bytes()):
  q=ids.get('Pope '+r['name'])
  if not q:unresolved.append(r['name']);continue
  add('Q170174',q,max(755,r['from']),min(1870,r['to']),SOURCE,'教皇／教皇国君主',officialStart=r['startText'],officialEnd=r['endText'])
 notes['Q170174']='按圣座官方教皇名录列任期；阿维尼翁时期、教会分裂、罗马公社及法军占领等会影响实际控制。官方名录中的教皇不等于该年直接控制全部教皇国领土；对立教皇不混入正统名录。'
 # Complete calendar years without an elected pope are a genuine sede vacante.
 occupied={y for r in terms['Q170174']for y in range(r['from'],r['to']+1)}
 for y in range(755,1871):
  if y not in occupied:terms['Q170174'].append({'value':'local:papal-sede-vacante','label':'宗座出缺（教皇选举／过渡治理）','from':y,'to':y,'at':None,'kind':'vacancy','roleLabel':'宗座出缺','citation':[SOURCE],'supplement':TAG})
 # Only candidates actually listed in that country's monarch table are eligible.
 rosters={}
 for file in ['poland','hungary','bohemia','germany']:
  parser=Tables();parser.feed((CACHE/(file+'.html')).read_text(encoding='utf8'));roster=set()
  for row in parser.rows:
   if len(row)<4:continue
   for cell in row[:2]:
    q=next((ids[t]for t in cell['links']if t in ids and human(people.get(ids[t],{}))),None)
    if q:roster.add(q);break
  rosters[file]=roster
 configs=[('poland','Q577867',['Q3273712','Q55850874'],962,1572),('hungary','Q171150',['Q6412254'],1000,1918),('bohemia','Q42585',['Q45341328'],1198,1918),('germany','Q12548',['Q181765','Q782985'],962,1806)]
 office_names={'Q3273712':'波兰国王','Q55850874':'波兰公爵','Q6412254':'匈牙利国王','Q45341328':'波希米亚国王','Q181765':'神圣罗马皇帝','Q782985':'罗马人民的国王（德意志王位）'}
 for file,country,offices,lo,hi in configs:
  for q in (people.keys()if file=='germany'else rosters[file]):
   for claim in people[q].get('claims',{}).get('P39',[]):
    r=simplify(claim)
    if not r or r['value']not in offices or r['from']is None or r['to']is None:continue
    a,b=max(lo,r['from']),min(hi,r['to'])
    if a<=b:add(country,q,a,b,'https://www.wikidata.org/wiki/'+q+'#P39',office_names[r['value']],office=r['value'])
 # Named table reigns fill P39 statements which omitted their qualifiers.
 for n,a,b,country,role in [('Béla III of Hungary',1172,1196,'Q171150','匈牙利国王'),('Louis I of Hungary',1342,1382,'Q171150','匈牙利国王'),('Henry of Bohemia',1307,1310,'Q42585','波希米亚国王')]:
  q=ids.get(n)
  if not q:unresolved.append(n);continue
  add(country,q,a,b,'https://en.wikipedia.org/wiki/List_of_Hungarian_monarchs'if country=='Q171150'else'https://en.wikipedia.org/wiki/List_of_Bohemian_monarchs',role)
 terms['Q42585'].append({'value':'local:bohemian-interregnum','label':'波希米亚等级会议治理／王位出缺','from':1439,'to':1453,'at':None,'kind':'vacancy','roleLabel':'王位继承与实际权力存在争议，1453年拉斯洛五世加冕','citation':['https://en.wikipedia.org/wiki/List_of_Bohemian_monarchs'],'supplement':TAG})
 # The Austrian list's REIGN column, with rowspans expanded, describes each
 # constituent territory separately. Birth/death years never become reigns.
 parser=Tables();parser.feed((CACHE/'austria.html').read_text(encoding='utf8'));austrian=[]
 for row in parser.rows:
  if len(row)<4:continue
  q=next((ids[t]for t in row[0]['links']if t in ids and human(people.get(ids[t],{}))),None)
  region=row[3]['text'];dates=re.findall(r'[12]\d{3}',row[2]['text'])
  if not q or not re.search(r'Austria|Styria|Tyrol',region)or not dates:continue
  if 'claimant'in region:continue
  a,b=int(dates[0]),int(dates[-1]);a=max(a,1276);b=min(b,1805)
  if a>b:continue
  scopes=[zh for en,zh in [('Lower','下奥地利'),('Upper','上奥地利'),('Inner','内奥地利'),('Further','外奥地利'),('Tyrol','蒂罗尔')]if en in region]
  role=('摄政'if 'Regency'in region else'世袭领地君主')+' · '+('、'.join(scopes)or'奥地利本部')
  if q==ids.get('Charles V, Holy Roman Emperor')and a==1519:b=min(b,1521);role+='（1521年移交斐迪南一世）'
  record=(q,a,b,role)
  if record in austrian:continue
  austrian.append(record);add('local:austrian-hereditary-lands',q,a,b,'https://en.wikipedia.org/wiki/List_of_rulers_of_Austria',role,territorialReign=True)
 # Use common European regnal numbers in display rather than local archducal
 # numbers, which differ for the same individual.
 notes['local:austrian-hereditary-lands']='奥地利世袭领地是多个公国、伯国及支系领地的集合称谓，不冒称一个正式统一王国。下列任期按奥地利、内奥地利、外奥地利与蒂罗尔分别记载，共存者并非全部共同统治每一块领土。'
 for q,a,b,text in austrian:
  for country in ['Q65968','Q66504140']:add(country,q,a,b,'https://en.wikipedia.org/wiki/List_of_rulers_of_Austria',text,territorialReign=True)
 # Explicit succession rosters fill country-side omissions for the Jagiellons.
 jag=[('Władysław II Jagiełło',1386,1434),('Władysław III of Poland',1434,1444),('Casimir IV Jagiellon',1447,1492),('John I Albert',1492,1501),('Alexander Jagiellon',1501,1506),('Sigismund I the Old',1506,1548),('Sigismund II Augustus',1548,1572)]
 missing=[n for n,_,_ in jag if n not in ids]
 if missing:
  newly=resolve(missing);ids.update(newly);people.update(entities(newly.values(),'reign-people'))
 for n,a,b in jag:
  q=ids.get(n)
  if not q:unresolved.append(n);continue
  for country in ['Q577867','Q171348','Q194355']:add(country,q,a,b,'https://jagiellonians.site.ox.ac.uk/jagiellonians-timeline','波兰国王（雅盖洛家族）')
 for n,a,b in [('Casimir IV Jagiellon',1440,1492),('Alexander Jagiellon',1492,1506),('Sigismund I the Old',1506,1548),('Sigismund II Augustus',1544,1572)]:add('Q49683',ids[n],a,b,'https://jagiellonians.site.ox.ac.uk/jagiellonians-timeline','立陶宛大公；任期按该国王位记载')
 # Scandinavian monarchs and effective Swedish regents. A union claimant is
 # not projected onto Sweden throughout periods of separate government.
 dk=[('Margaret I of Denmark',1387,1412,'实际执政者'),('Eric of Pomerania',1396,1439,'国王'),('Christopher of Bavaria',1440,1448,'国王'),('Christian I of Denmark',1448,1481,'国王'),('John, King of Denmark',1481,1513,'国王'),('Christian II of Denmark',1513,1523,'国王')]
 no=[('Margaret I of Denmark',1388,1412,'实际执政者'),('Eric of Pomerania',1389,1442,'国王'),('Christopher of Bavaria',1442,1448,'国王'),('Charles VIII of Sweden',1449,1450,'国王'),('Christian I of Denmark',1450,1481,'国王'),('John, King of Denmark',1483,1513,'国王'),('Christian II of Denmark',1513,1523,'国王')]
 se=[('Margaret I of Denmark',1389,1412,'实际执政者'),('Eric of Pomerania',1396,1439,'国王'),('Christopher of Bavaria',1441,1448,'国王'),('Charles VIII of Sweden',1448,1457,'国王'),('Christian I of Denmark',1457,1464,'国王'),('Charles VIII of Sweden',1464,1465,'国王'),('Charles VIII of Sweden',1467,1470,'国王'),('Sten Sture the Elder',1470,1497,'摄政'),('John, King of Denmark',1497,1501,'国王'),('Sten Sture the Elder',1501,1503,'摄政'),('Svante Nilsson (regent of Sweden)',1504,1512,'摄政'),('Sten Sture the Younger',1512,1520,'摄政'),('Christian II of Denmark',1520,1521,'国王；1521年失去实际统治'),('Gustav I of Sweden',1521,1523,'摄政，1523年登基'),('Jöns Bengtsson Oxenstierna',1465,1466,'摄政'),('Kettil Karlsson (Vasa)',1464,1464,'摄政'),('Erik Axelsson Tott',1466,1467,'摄政')]
 nordic_source='https://medeltiden.kalmarlansmuseum.se/en/society/the-kalmar-union/the-union-wars/'
 for country,rows in [('Q756617',dk),('Q20',no),('Q34',se)]:
  for n,a,b,role in rows:add(country,ids[n],a,b,nordic_source,role)
  notes[country]='卡尔马联合时期仍区分各王国及瑞典摄政。年度交接可能显示数人；名义王位主张不等于实际控制。'
 # Supplemental royal Hungary uses Hungarian kings, not every Austrian ruler.
 terms['Q253094']=[{**r,'roleLabel':'皇家匈牙利国王'}for r in terms.get('Q171150',[])if r['to']>=1526 and r['from']<=1699 and r['value']in {q for q,_,_,_ in austrian}]
 # Every row is explicit about its field source; a household head never becomes
 # ruler of all lands held by other branches merely through family membership.
 for country,rows in terms.items():
  entity=data['entities'].setdefault(country,{'label':country,'description':'','en':'','fields':{}})
  old=[r for r in entity['fields'].get('ruler',[])if r.get('supplement')!=TAG]
  entity['fields']['ruler']=old+list({(r['value'],r['from'],r['to'],r.get('roleLabel')):r for r in rows}.values())
  if country in notes:entity['rulerScopeNote']=notes[country]
 for q,e in people.items():data['labels'][q]=label(e)
 write('public/data/polity-facts.json',data)
 report={'reviewedAt':'2026-10-31','method':'Official pontiff dates, expanded reign columns, and exact named office matching','entities':{q:{'rows':rs,'note':notes.get(q,'')}for q,rs in terms.items()},'unresolved':unresolved}
 write('public/data/historical-ruler-supplements.json',report);save('verified-ruler-people.json',{q:people[q]for q in {r['value']for rows in terms.values()for r in rows}if q in people})
 print('Reign records',sum(len(r)for r in terms.values()),'polities',len(terms),'unresolved',unresolved,flush=True)
if __name__=='__main__':main()

