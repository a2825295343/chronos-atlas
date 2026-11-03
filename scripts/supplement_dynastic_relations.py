"""Constituent-crown rulers and dated common-monarch relationships."""
import json,itertools
from enrich_polities import ROOT,label
from fetch_historical_rulers import CACHE,save
TAG='dynastic-relations-2026-10-31'
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def main():
 facts=read('public/data/polity-facts.json');curated=read('public/data/curated-facts.json');ids=json.loads((CACHE/'resolved-titles.json').read_bytes());ids.update(json.loads((CACHE/'extra-resolved.json').read_bytes()));ids.update(json.loads((CACHE/'succession-resolved.json').read_bytes()));ids.update(json.loads((CACHE/'nordic-late-resolved.json').read_bytes()));ids.update(json.loads((CACHE/'nordic-extra-resolved.json').read_bytes()))
 people=json.loads((CACHE/'verified-ruler-people.json').read_bytes());people.update(json.loads((CACHE/'people.json').read_bytes()));people.update(json.loads((CACHE/'succession-people.json').read_bytes()));people.update(json.loads((CACHE/'nordic-late-people.json').read_bytes()));people.update(json.loads((CACHE/'nordic-extra-people.json').read_bytes()))
 hb='https://www.habsburger.net/en/chapter/reuniting-habsburg-lands-maximilian-i';net='https://www.nam.ac.uk/explore/spanish-succession';jag='https://jagiellonians.site.ox.ac.uk/jagiellonians-timeline';kal='https://www.norgeshistorie.no/kilder/senmiddelalder/K1011-Unionsbrev.html'
 new={}
 def term(country,title,a,b,role,source):
  q=ids[title];new.setdefault(country,[]).append({'value':q,'label':label(people[q]),'from':a,'to':b,'at':None,'roleLabel':role,'citation':[source],'supplement':TAG})
 for n,a,b in [('Mary of Burgundy',1477,1482),('Philip I of Castile',1482,1506),('Charles V, Holy Roman Emperor',1506,1555)]:term('Q157109',n,a,b,'尼德兰各省君主；各省保有独立制度',hb)
 for n,a,b in [('Philip II of Spain',1555,1598),('Isabella Clara Eugenia',1598,1621),('Albert VII, Archduke of Austria',1598,1621),('Philip IV of Spain',1621,1665),('Charles II of Spain',1665,1700),('Philip V of Spain',1700,1714)]:term('Q622783',n,a,b,'西属尼德兰主权君主；不是当地总督',net)
 for n,a,b in [('Charles VI, Holy Roman Emperor',1714,1740),('Maria Theresa',1740,1780),('Joseph II, Holy Roman Emperor',1780,1790),('Leopold II, Holy Roman Emperor',1790,1792),('Francis II, Holy Roman Emperor',1792,1795)]:term('Q700283',n,a,b,'奥属尼德兰主权君主；与奥地利本部分别记载任期',net)
 for n,a,b in [('Mary of Burgundy',1477,1482),('Philip I of Castile',1482,1506),('Charles V, Holy Roman Emperor',1506,1556),('Philip II of Spain',1556,1598),('Isabella Clara Eugenia',1598,1621),('Albert VII, Archduke of Austria',1598,1621),('Philip IV of Spain',1621,1665),('Charles II of Spain',1665,1678)]:term('Q642314',n,a,b,'勃艮第伯爵／伯爵领主权君主',net)
 for n,a,b in [('Qaitbay',1468,1496),('Qansuh al-Ghuri',1501,1516),('Tuman bay II',1516,1517)]:term('Q282428',n,a,b,'马穆鲁克苏丹','https://www.metmuseum.org/ja/toah/ht/08/afe')
 term('Q42585','Henry, King of Bohemia',1307,1310,'波希米亚国王','https://en.wikipedia.org/wiki/List_of_Bohemian_monarchs')
 # The 1569 Commonwealth has its own elected crown; it is not simply the
 # Jagiellon family continuing after 1572.
 plc=[('Sigismund II Augustus',1569,1572),('Henry III of France',1573,1575),('Anna Jagiellon',1575,1586),('Stephen Báthory',1576,1586),('Sigismund III Vasa',1587,1632),('Władysław IV Vasa',1632,1648),('John II Casimir',1648,1668),('Michał Korybut Wiśniowiecki',1669,1673),('John III Sobieski',1674,1696),('Augustus II the Strong',1697,1706),('Augustus II the Strong',1709,1733),('Stanisław Leszczyński',1704,1709),('Stanisław Leszczyński',1733,1736),('Augustus III of Poland',1733,1763),('Stanisław August Poniatowski',1764,1795)]
 for n,a,b in plc:
  if n not in ids:raise ValueError('Missing Commonwealth monarch '+n)
  term('Q172107',n,a,b,'波兰国王兼立陶宛大公；竞争王位的重叠任期不表示领土完全共治','https://en.wikipedia.org/wiki/List_of_Polish_monarchs')
 for y in range(1569,1796):
  if not any(r['from']<=y<=r['to']for r in new['Q172107']):new['Q172107'].append({'value':'local:commonwealth-interregnum','label':'王位出缺，由等级会议与选举体制过渡治理','from':y,'to':y,'at':None,'kind':'vacancy','citation':['https://en.wikipedia.org/wiki/List_of_Polish_monarchs'],'supplement':TAG})
 facts['entities'].setdefault('Q172107',{'label':'波兰立陶宛联邦','en':'Polish-Lithuanian Commonwealth','description':'','fields':{}})['rulerScopeNote']='采用各届君主及争位者的王位任期。斯坦尼斯瓦夫一世与奥古斯特二世／三世等人的重叠表示竞争与分区支持，并非共同无争议统治全境。'
 for y in [1482]:new.setdefault('Q20',[]).append({'value':'local:norway-council-interregnum','label':'挪威参政院（王位过渡期）','from':y,'to':y,'at':None,'kind':'collective','citation':['https://en.wikipedia.org/wiki/List_of_Norwegian_monarchs'],'supplement':TAG})
 nordic='https://www.kongehuset.dk/en/the-monarchy-in-denmark/the-royal-lineage'
 late=[('Frederick I of Denmark',1523,1533),('Christian III of Denmark',1534,1559),('Frederick II of Denmark',1559,1588),('Christian IV of Denmark',1588,1648),('Frederick III of Denmark',1648,1670),('Christian V of Denmark',1670,1699),('Frederick IV of Denmark',1699,1730),('Christian VI of Denmark',1730,1746),('Frederick V of Denmark',1746,1766),('Christian VII of Denmark',1766,1808),('Frederick VI of Denmark',1808,1839)]
 for n,a,b in late:
  for country in ['Q756617','Q35']:term(country,n,a,b,'丹麦国王（1534年拥立，1536年确立统治）'if n=='Christian III of Denmark'else'丹麦国王（与挪威王位分开记载）',nordic)
  na=max(a,1524)if n=='Frederick I of Denmark'else max(a,1537)if n=='Christian III of Denmark'else a
  if na<=1814:term('Q20',n,na,min(b,1814),'挪威国王；丹挪联合不等于两国法律制度合一',nordic)
 for n,a,b in [('Christian VIII of Denmark',1839,1848),('Frederick VII of Denmark',1848,1863),('Christian IX of Denmark',1863,1906),('Frederick VIII of Denmark',1906,1912),('Christian X of Denmark',1912,1947),('Frederick IX of Denmark',1947,1972)]:term('Q35',n,a,b,'丹麦国王',nordic)
 term('Q20','Christian VIII of Denmark',1814,1814,'克里斯蒂安·弗雷德里克（1814年挪威国王）','https://www.kongehuset.no/historie/grunnlov-og-union-1814-1905')
 for n,a,b in [('Charles XIII',1814,1818),('Charles XIV John',1818,1844),('Oscar I of Sweden',1844,1859),('Charles XV',1859,1872),('Oscar II',1872,1905)]:
  for country in ['Q20','Q34']:term(country,n,a,b,'共主君主；两国各有宪法、政府与议会','https://www.forsvaret.no/om-forsvaret/organisasjon/haeren/haeren-400-ar/historien/haeren-i-unionstida/haeren-i-unionstida-18141905-en-introduksjon')
 term('Q20','Haakon VII of Norway',1905,1957,'1905年共主联合结束后当选的挪威国王','https://www.kongehuset.no/historie/et-eget-norsk-kongehus/kongevalget-i-1905')
 for r in new.get('Q20',[]):
  if r['value']==ids['Christian VIII of Denmark']and r['from']==1814:r['label']='克里斯蒂安·弗雷德里克（挪威国王）'
 # A source mask had accidentally pointed Norway at Margaret's person ID.
 facts['entities']['Q20']['rulerScopeNote']='挪威王冠任期与丹麦、瑞典分别记载，联合不代表法律制度合一；年内交接可能显示多位君主。'
 for country,rows in new.items():
  e=facts['entities'].setdefault(country,{'label':country,'en':'','description':'','fields':{}});e['fields']['ruler']=[r for r in e['fields'].get('ruler',[])if r.get('supplement')!=TAG]+rows
 for q,e in people.items():facts['labels'][q]=label(e)
 # Build common-monarch periods by intersecting the same PERSON's actual
 # country-specific reigns, not by shared dynasty or a centuries-long union name.
 relations=[r for r in curated['relations']if r.get('supplement')!=TAG]
 countries={'Austrian Hereditary Lands':'local:austrian-hereditary-lands','Kingdom of Bohemia':'Q42585','Royal Hungary':'Q253094','Crown of the Kingdom of Poland':'Q171348','Grand Duchy of Lithuania':'Q49683','Kingdom of Denmark':'Q756617','Kingdom of Norway':'Q20','Kingdom of Sweden':'Q34'}
 pairs=[('Austrian Hereditary Lands','Kingdom of Bohemia',1438,1805,hb),('Austrian Hereditary Lands','Royal Hungary',1526,1699,hb),('Crown of the Kingdom of Poland','Grand Duchy of Lithuania',1386,1568,jag),('Kingdom of Denmark','Kingdom of Norway',1397,1814,kal),('Kingdom of Denmark','Kingdom of Sweden',1397,1521,kal),('Kingdom of Norway','Kingdom of Sweden',1397,1521,kal),('Kingdom of Norway','Kingdom of Sweden',1814,1905,'https://www.kongehuset.no/historie/grunnlov-og-union-1814-1905')]
 for left,right,lo,hi,source in pairs:
  l=facts['entities'][countries[left]]['fields'].get('ruler',[]);r=facts['entities'][countries[right]]['fields'].get('ruler',[]);spans={}
  for a in l:
   if a.get('from')is None or a.get('to')is None or a.get('kind')or any(t in a.get('roleLabel','')for t in ['摄政','实际执政']):continue
   for b in r:
    if b.get('value')!=a['value']or b.get('from')is None or b.get('to')is None or b.get('kind')or any(t in b.get('roleLabel','')for t in ['摄政','实际执政']):continue
    start=max(lo,a['from'],b['from']);end=min(hi,a['to'],b['to'])
    if start<=end:spans[(a['value'],start,end)]=a['label']
  for (q,a,b),name in spans.items():relations.append({'id':TAG+'|'+left+'|'+right+'|'+q+'|'+str(a),'kind':'personalUnion','from':a,'to':b,'members':[left,right],'title':'共主关系 · '+name,'detail':'同一君主在两个王位的任期交集；两国的疆域、法律与行政制度并不因此合并。各王位任期的出处见统治者档案；摄政、分支统治与年内交接另列。','source':source,'supplement':TAG})
 relations.append({'id':TAG+'|kalmar-charter','kind':'politicalUnion','from':1397,'to':1523,'members':['Kingdom of Denmark','Kingdom of Norway','Kingdom of Sweden'],'title':'卡尔马联合的宪章与王朝框架','detail':'1397年联合宪章所联系的三个王国保有自身制度。瑞典在1448年后多次另立国王或摄政；这一框架记录不表示三国在整个时期持续共主、共同参战或服从统一中央政府。实际共主任期单独列出。','source':kal,'supplement':TAG})
 for title,a,b,members,detail,source in [
  ('马克西米利安 × 勃艮第的玛丽',1477,1482,['Austrian Hereditary Lands','Burgundian Netherlands'],'王室婚姻连接两套世袭领地；玛丽去世后由腓力继承尼德兰，马克西米利安的摄政不能写成奥地利吞并全部尼德兰。',hb),
  ('斐迪南 × 安娜·雅盖洛',1521,1547,['Austrian Hereditary Lands','Kingdom of Bohemia','Kingdom of Hungary'],'1521年成婚。1526年路易二世死亡后发生王位继承与选举；婚姻本身不等于此前已合并三国。',jag),
  ('路易二世 × 奥地利的玛丽',1522,1526,['Kingdom of Bohemia','Kingdom of Hungary','Austrian Hereditary Lands'],'1522年举行婚礼，至1526年路易二世战死；不把1515年的订婚安排误写成已经成婚。',jag)]:relations.append({'id':TAG+'|marriage|'+title,'kind':'royalMarriage','from':a,'to':b,'members':members,'title':title,'detail':detail,'source':source,'supplement':TAG})
 # The Ottoman conquest creates a new province, not an indefinitely surviving
 # tributary Mamluk state. Keep this dated dependency out of the pre-1517 map.
 curated['relations']=relations;write('public/data/curated-facts.json',curated);write('public/data/polity-facts.json',facts)
 report=read('public/data/historical-ruler-supplements.json');report['unresolved']=[n for n in report.get('unresolved',[])if n not in ids]
 for q,rows in new.items():report['entities'].setdefault(q,{'rows':[],'note':''})['rows']=[r for r in report['entities'].get(q,{}).get('rows',[])if r.get('supplement')!=TAG]+rows
 write('public/data/historical-ruler-supplements.json',report);save('verified-ruler-people.json',{q:people[q]for q in {r['value']for item in report['entities'].values()for r in item['rows']}if q in people})
 write('public/data/dynastic-relations-review.json',{'reviewedAt':'2026-10-31','relations':[r for r in relations if r.get('supplement')==TAG],'principle':'Intersect the same person in separate crowns; keep charter claims separate from effective personal union.'})
 print('Constituent reigns',sum(len(v)for v in new.values()),'dated relationships',sum(r.get('supplement')==TAG for r in relations),flush=True)
if __name__=='__main__':main()
