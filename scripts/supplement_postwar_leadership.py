"""Office-matched post-war terms; no use of a roster's surrounding country text.
The long source pages mix dependent states, offices and regional headings. They
only supply CANDIDATE PEOPLE. Actual country assignment requires an exact named
office in P39 and the target country's P1906/P1313, with dated terms.
"""
import json,re
from collections import defaultdict
from enrich_polities import ROOT,simplify,label
CACHE=ROOT/'.local/postwar-review'
TAG='postwar-leadership-1945-1955-v1'
# Exceptional historical offices are not mapped to today's republican office.
# Explicit country assignments below were reviewed separately from list headings.
MANUAL=[
 ('Q1658411','ruler','Charles Vyner Brooke',1917,1946,'沙捞越白人拉惹；1946年将统治权移交英国'),
 ('Q1240096','ruler','Mir Osman Ali Khan',1911,1948,'海得拉巴尼扎姆；1948年印度军事行动后失去独立统治权'),
 ('local:second-hungarian-republic','ruler','Zoltán Tildy',1946,1948,'匈牙利第二共和国总统'),
 ('local:second-hungarian-republic','ruler','Árpád Szakasits',1948,1949,'匈牙利第二共和国总统；1949年改制后另为主席团职务'),
 ('Q736','ruler','José María Velasco Ibarra',1944,1947,'厄瓜多尔总统'),
 ('Q736','ruler','José María Velasco Ibarra',1952,1956,'厄瓜多尔总统；第三次总统任期'),
 ('Q241','ruler','Ramón Grau',1944,1948,'古巴总统'),
 ('Q157734','ruler','Said bin Taimur',1932,1970,'马斯喀特与阿曼苏丹'),
 ('Q17427','ruler','Mao Zedong',1945,1976,'中共控制区政治领导人／中央委员会主席；此为势力而非国家记录'),
 ('Q129286','ruler','George VI',1936,1947,'英属印度皇帝；1947年印度与巴基斯坦独立前的管理阶段'),
 ('Q668','ruler','George VI',1947,1950,'印度自治领国王；1950年1月改为共和国'),
 ('Q13426199','ruler','Chiang Kai-shek',1943,1948,'国民政府主席'),
 ('Q13426199','ruler','Chiang Kai-shek',1948,1949,'中华民国总统；1949年引退'),
 ('Q13426199','ruler','Li Zongren',1949,1950,'代总统；1949年底离开中国大陆'),
 ('Q786','ruler','Héctor Trujillo',1952,1960,'多米尼加总统；拉斐尔·特鲁希略仍掌握实际政治权力'),
 ('Q804','ruler','Alcibíades Arosemena',1951,1952,'巴拿马总统'),
 ('Q804','ruler','José Antonio Remón Cantera',1952,1955,'巴拿马总统'),
 ('Q804','ruler','José Ramón Guizado',1955,1955,'巴拿马总统；1955年1月短期任职'),
 ('Q804','ruler','Ricardo Arias (politician)',1955,1956,'巴拿马总统'),
 ('Q739','ruler','Laureano Gómez Castro',1950,1953,'哥伦比亚总统；1951年后由代理总统履职'),
 ('Q739','ruler','Roberto Urdaneta Arbeláez',1951,1953,'代理哥伦比亚总统'),
 ('Q142','ruler','Charles de Gaulle',1944,1946,'法国临时政府主席；不是当时的第五共和国总统'),
 ('Q142','ruler','Félix Gouin',1946,1946,'法国临时政府主席'),
 ('Q142','ruler','Georges Bidault',1946,1946,'法国临时政府主席'),
 ('Q142','ruler','Léon Blum',1946,1947,'法国临时政府主席／过渡政府首脑'),
 ('Q69829','ruler','Charles de Gaulle',1944,1946,'临时政府阶段国家领导人；源GIS此时提前沿用第四共和国名称'),
 ('Q69829','ruler','Félix Gouin',1946,1946,'法国临时政府主席'),
 ('Q69829','ruler','Georges Bidault',1946,1946,'法国临时政府主席'),
 ('Q69829','ruler','Léon Blum',1946,1947,'法国临时政府／第四共和国初期过渡领导人'),
 ('Q792','ruler','Salvador Castaneda Castro',1945,1948,'总统'),
 ('Q792','ruler','Óscar Osorio',1950,1956,'总统；1950年正式就职'),
 ('Q837','ruler','Tribhuvan of Nepal',1911,1950,'国王；1950年出走印度'),
 ('Q837','ruler','Tribhuvan of Nepal',1951,1955,'复位后的国王'),
 ('Q837','ruler','Gyanendra of Nepal',1950,1951,'拉纳政府拥立的幼王；非2001年再次即位任期'),
 ('Q837','ruler','Mahendra of Nepal',1955,1972,'国王'),
 ('Q258','ruler','George VI',1936,1952,'南非联邦国王；总督为君主代表'),
 ('Q258','ruler','Elizabeth II',1952,1961,'南非联邦女王；1961年改为共和国'),
 ('Q1998401','ruler','Yahya Muhammad Hamid ed-Din',1918,1948,'也门穆塔瓦基利亚王国国王／伊玛目'),
 ('Q1998401','ruler','Ahmad bin Yahya',1948,1962,'国王／伊玛目'),
 ('Q115','ruler','Haile Selassie',1941,1974,'返回埃塞俄比亚后的皇帝任期'),
 ('Q149805','ruler','Faisal II of Iraq',1939,1958,'伊拉克国王；1953年前有摄政'),
 ('Q149805','ruler',"'Abd al-Ilah",1939,1953,'摄政；不能与国王合并为同一人'),
 ('Q207991','ruler','Mohammad Reza Pahlavi',1941,1979,'伊朗沙阿'),
 ('Q944391','ruler','Abdullah bin Jassim Al Thani',1913,1949,'卡塔尔统治者'),
 ('Q944391','ruler','Ali bin Abdullah Al Thani',1949,1960,'卡塔尔统治者'),
 ('Q843','ruler','George VI',1947,1952,'巴基斯坦自治领国王；非当代共和国总统'),
 ('Q843','ruler','Elizabeth II',1952,1956,'巴基斯坦自治领女王；1956年改为共和国'),
 ('Q854','ruler','George VI',1948,1952,'锡兰自治领国王；总督为君主代表'),
 ('Q854','ruler','Elizabeth II',1952,1972,'锡兰自治领女王；1972年改为共和国'),
 ('Q1138904','ruler','Mohammed Zahir Shah',1933,1973,'阿富汗国王'),
 ('Q842794','ruler','Michael I of Romania',1940,1947,'罗马尼亚国王；1947年末退位'),
 ('Q842794','ruler','Constantin Ion Parhon',1947,1952,'人民共和国大国民议会主席团主席'),
 ('Q842794','ruler','Petru Groza',1952,1958,'大国民议会主席团主席'),
 ('Q842794','headOfGovernment','Petru Groza',1945,1952,'部长会议主席／总理'),
 ('Q842794','headOfGovernment','Gheorghe Gheorghiu-Dej',1952,1955,'部长会议主席'),
 ('Q842794','headOfGovernment','Chivu Stoica',1955,1961,'部长会议主席'),
 ('Q121932','ruler','Vasil Kolarov',1946,1947,'人民共和国临时主席团主席'),
 ('Q121932','ruler','Mincho Neychev',1947,1950,'国民议会主席团主席'),
 ('Q121932','ruler','Georgi Damyanov',1950,1958,'国民议会主席团主席'),
 ('Q146885','ruler','Shukri al-Quwatli',1943,1949,'叙利亚总统'),
 ('Q146885','ruler','Hashim al-Atassi',1949,1951,'叙利亚总统'),
 ('Q146885','ruler','Fawzi Selu',1951,1953,'军事政变后的国家元首'),
 ('Q146885','ruler','Adib Shishakli',1953,1954,'总统；军人政治领袖'),
 ('Q146885','ruler','Maamun al-Kuzbari',1954,1954,'代理总统'),
 ('Q146885','ruler','Hashim al-Atassi',1954,1955,'恢复宪政后的总统'),
 ('Q146885','ruler','Shukri al-Quwatli',1955,1958,'第二次总统任期'),
 ('Q467864','ruler','Omer Nishani',1944,1953,'1946年起任人民议会主席团主席；此前为反法西斯议会主席'),
 ('Q222','ruler','Omer Nishani',1944,1953,'战后阿尔巴尼亚反法西斯议会／人民议会主席团主席'),
 ('Q467864','ruler','Haxhi Lleshi',1953,1982,'人民议会主席团主席'),
 ('Q467864','headOfGovernment','Enver Hoxha',1944,1954,'部长会议主席／总理；党领导职务另计'),
 ('Q209065','ruler','George II of Greece',1935,1947,'希腊国王；战后返回希腊前另有摄政'),
 ('Q209065','ruler','Paul of Greece',1947,1964,'希腊国王'),
 ('Q83286','ruler','Ivan Ribar',1945,1953,'联邦人民议会主席团主席'),
 ('Q83286','ruler','Josip Broz Tito',1953,1980,'南斯拉夫总统；不能把1953年前的总理职务写成总统'),
 ('Q83286','headOfGovernment','Josip Broz Tito',1945,1963,'联邦政府总理／联邦行政委员会主席'),
 ('Q124943','ruler','Farouk of Egypt',1936,1952,'埃及国王'),
 ('Q124943','ruler','Fuad II of Egypt',1952,1953,'幼王；实际由摄政机构代表'),
 ('Q521263','ruler','14th Dalai Lama',1950,1959,'1950年11月17日起亲政；此前由摄政处理政务'),
 ('Q521263','ruler','Taktra Rinpoche',1941,1950,'摄政；与达赖喇嘛的宗教身份分开'),
 ('Q212056','ruler','Gonchigiin Bumtsend',1940,1953,'小呼拉尔主席团／大人民呼拉尔主席团主席'),
 ('Q212056','ruler','Sükhbaataryn Yanjmaa',1953,1954,'代理大人民呼拉尔主席团主席'),
 ('Q212056','ruler','Jamsrangiin Sambuu',1954,1972,'大人民呼拉尔主席团主席'),
 ('Q212056','headOfGovernment','Khorloogiin Choibalsan',1939,1952,'部长会议主席'),
 ('Q212056','headOfGovernment','Yumjaagiin Tsedenbal',1952,1974,'部长会议主席'),
 ('local:cyrenaica-emirate','ruler','Idris of Libya',1949,1951,'昔兰尼加埃米尔；1951年底起任利比亚国王'),
 ('Q31454','ruler','Idris of Libya',1951,1969,'利比亚国王'),
 ('Q752431','ruler','George VI',1936,1952,'英法共管方之一的英国国王；非统一新赫布里底国家元首'),
 ('Q752431','ruler','Elizabeth II',1952,1980,'英法共管方之一的英国女王'),
 ('Q752431','ruler','Vincent Auriol',1947,1954,'英法共管方之一的法国总统'),
 ('Q752431','ruler','René Coty',1954,1959,'英法共管方之一的法国总统'),
]
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')

def main():
 people=json.loads((CACHE/'people.json').read_bytes());cached=json.loads((CACHE/'cached-entities.json').read_bytes());offices=json.loads((CACHE/'office-map.json').read_bytes())
 ids=json.loads((CACHE/'roster-ids.json').read_bytes())
 if (CACHE/'extra-ids.json').exists():ids.update(json.loads((CACHE/'extra-ids.json').read_bytes()))
 if (CACHE/'extra-people.json').exists():people.update(json.loads((CACHE/'extra-people.json').read_bytes()))
 facts=read('public/data/polity-facts.json');changes=[]
 for e in facts['entities'].values():
  for field in ['ruler','headOfGovernment']:
   if field in e.get('fields',{}):e['fields'][field]=[r for r in e['fields'][field]if r.get('supplement')!=TAG]
 for person,e in people.items():
  if not any((s:=simplify(c))and s['value']=='Q5'for c in e.get('claims',{}).get('P31',[])):continue
  for c in e.get('claims',{}).get('P39',[]):
   term=simplify(c)
   if not term or term['value']not in offices or term['from']is None or term['to']is None or term['from']>1955 or term['to']<1945:continue
   for target in offices[term['value']]:
    country,field=target['country'],target['field'];entity=facts['entities'].get(country)
    if not entity:continue
    if country=='Q185682':continue  # Colonial archive uses the explicit parent.
    if field=='headOfGovernment'and country in ['Q43','Q252']and any(t['country']==country and t['field']=='ruler'for t in offices[term['value']]):continue
    rows=entity['fields'].setdefault(field,[])
    if any(r['value']==person and r.get('from')==term['from']and r.get('to')==term['to']for r in rows):continue
    office=cached.get(term['value'],{});role=label(office)if office else('国家元首对应职务'if field=='ruler'else'政府首脑对应职务')
    role={'President of the Council':'法国部长会议主席／总理','French co-prince of Andorra':'安道尔法国方大公','Episcopal Co-Prince':'安道尔主教方大公','King of Jordan':'约旦国王'}.get(role,role).removesuffix('列表')
    row={**term,'value':person,'label':label(e),'roleLabel':role,'office':term['value'],'citation':term['citation']or[f'https://www.wikidata.org/wiki/{person}#P39'],'dateSource':'exact dated P39 / '+term['value'],'supplement':TAG,'derived':True,'inference':'历史年表仅用于选取候选人物；依该国元首／政府首脑的准确职位及人物任期补录，未按邻近标题推定所属国。'}
    rows.append(row);changes.append({'country':country,'field':field,**row})
 for country,field,title,a,b,role in MANUAL:
  q=ids.get(title)
  if not q or not any((s:=simplify(c))and s['value']=='Q5'for c in people.get(q,{}).get('claims',{}).get('P31',[])):raise ValueError('Unverified manual candidate '+title)
  entity=facts['entities'].setdefault(country,{'label':country,'en':'','description':'','fields':{}})
  source='https://en.wikipedia.org/wiki/'+title.replace(' ','_')
  row={'value':q,'label':label(people[q]),'from':a,'to':b,'at':None,'roleLabel':role,'citation':[source,f'https://www.wikidata.org/wiki/{q}#P39'],'supplement':TAG,'dateSource':'reviewed exceptional historical role'}
  if title=='14th Dalai Lama':row['citation'].insert(0,'https://www.dalailama.com/the-dalai-lama/biography-and-daily-life/birth-to-exile')
  if title=='Vincent Auriol':row['citation'].insert(0,'https://www.elysee.fr/vincent-auriol')
  rows=entity['fields'].setdefault(field,[])
  if not any(r['value']==q and r.get('from')==a and r.get('to')==b for r in rows):rows.append(row);changes.append({'country':country,'field':field,**row})
 # Explicit institutions are preferable to inventing a personal president.
 for country,a,b,value,text,source in [('Q792',1948,1950,'local:salvador-council','革命执政委员会（集体政府，1950年交接）','https://en.wikipedia.org/wiki/Revolutionary_Council_of_Government'),('Q3497642',1945,1956,'local:tangier-institutions','丹吉尔国际管制委员会与国际立法会议（多国管理机构）','https://en.wikipedia.org/wiki/Tangier_International_Zone'),('Q77',1952,1967,'local:uruguay-national-council','全国政府委员会（九人集体元首／政府机关，非单一总统）','https://www.impo.com.uy/bases/leyes-originales/11789-1952/1'),('Q79',1954,1956,'local:egypt-rcc','革命指挥委员会（纳赛尔领导的过渡权力机构）','https://en.wikipedia.org/wiki/Egyptian_Revolutionary_Command_Council'),('Q840601',1944,1949,'local:ili-governing-institutions','伊犁等三区政权领导机构（1946年后为三区革命领导机构，非持续不变的独立总统制）','https://en.wikipedia.org/wiki/Second_East_Turkestan_Republic'),('local:berlin-four-powers',1945,1948,'local:berlin-kommandatura','盟国管制委员会／柏林盟国管理机构（四国共管）','https://history.state.gov/milestones/1945-1952/germany'),('local:hungary-national-council',1945,1946,'local:hungary-high-council','匈牙利国家最高委员会（战后集体临时元首机关）','https://en.wikipedia.org/wiki/High_National_Council'),('local:palestinian-arab-control-1948',1948,1948,'local:palestinian-local-institutions','分散的地方政治与军事机构（非统一政府，不适用单一国家元首）','https://www.un.org/unispal/timeline/')]:
  row={'value':value,'label':text,'from':a,'to':b,'at':None,'kind':'collective','roleLabel':'集体管理机构；非单一总统','citation':[source],'supplement':TAG}
  facts['entities'].setdefault(country,{'label':text,'en':'','description':'','fields':{}})['fields'].setdefault('ruler',[]).append(row);changes.append({'country':country,'field':'ruler',**row})
 for q,e in people.items():facts['labels'][q]=label(e)
 translations=read('src/localization/postwar-person-names.zh.json')
 for e in facts['entities'].values():
  for field in ['ruler','headOfGovernment']:
   for r in e.get('fields',{}).get(field,[]):
    if r.get('supplement')==TAG and r['value']in translations:r['label']=translations[r['value']]
 for r in changes:
  if r['value']in translations:r['label']=translations[r['value']]
 facts['labels'].update(translations)
 # Constitutional role changes must not be projected backwards. Turkey was
 # parliamentary before 2018; Indonesia had separate PMs in 1945–1959.
 role_corrections=[]
 for country in ['Q43','Q252']:
  fields=facts['entities'][country]['fields'];heads={r['value']for r in fields.get('ruler',[])if(r.get('from')is None or r['from']<=1955)and(r.get('to')is None or r['to']>=1945)};kept=[]
  for r in fields.get('headOfGovernment',[]):
   if r['value']in heads and r.get('from')is not None and r['from']<=1955 and(r.get('to')is None or r['to']>=1945):
    if country=='Q252':
     for a,b in [(r['from'],min(r.get('to') or 1959,1945)),(max(r['from'],1959),r.get('to'))]:
      if b is None or a<=b:kept.append({**r,'from':a,'to':b,'roleLabel':'总统兼政府首脑（依宪制阶段）','dateSource':'constitutional role boundary','citation':['https://setkab.go.id/profil-kabinet/']})
    role_corrections.append({'country':country,'removedFromPostwarGovernmentRole':r['value'],'reason':'不能将后来的总统兼任政府首脑制度倒推到议会制阶段'})
   else:kept.append(r)
  fields['headOfGovernment']=kept
 # Administration centres are labelled as such, not invented national capitals.
 for q,government,centre in [
  ('local:british-tripolitania','英国管理下的战后过渡行政区','的黎波里（管理驻地）'),
  ('local:french-fezzan','法国管理下的战后过渡行政区','塞卜哈（管理驻地）'),
  ('local:british-cyrenaica','英国管理下的昔兰尼加行政区','班加西（管理驻地）'),
  ('local:cyrenaica-emirate','埃米尔制；处于英国影响下的过渡政治安排','班加西'),
  ('local:british-eritrea','英国军事／过渡行政管理','阿斯马拉（管理驻地）'),
  ('local:eritrea-federation','与埃塞俄比亚联邦下的自治组成地区','阿斯马拉（自治政府驻地）'),
  ('local:british-somaliland','英国保护地；1948年11月恢复民政','哈尔格萨（行政驻地）'),
  ('local:portuguese-timor','葡萄牙殖民管理；1951年起改称海外省','帝力（行政驻地）'),
  ('local:falklands-postwar','英国实际管理的争议领地','斯坦利港（管理驻地）'),
  ('local:gaza-egyptian-administration','埃及管理的巴勒斯坦地区；管理不等于领土主权归属','加沙城（地方行政中心）')]:
  e=facts['entities'].get(q)
  if not e:continue
  source=read('public/data/curated-facts.json')['polities'].get(q,{}).get('source','https://www.wikidata.org/')
  for field,text in [('government',government),('capital',centre)]:
   rows=e['fields'].setdefault(field,[]);rows[:]=[r for r in rows if r.get('supplement')!=TAG]
   rows.append({'value':text,'label':text,'from':1945,'to':1955,'at':None,'citation':[source],'supplement':TAG})
 # The French Fourth Republic is the contemporary France behind colonial
 # archive links, not the current Fifth Republic officeholder.
 previous_path=ROOT/'public/data/postwar-leadership-review.json'
 if previous_path.exists():role_corrections=[*json.loads(previous_path.read_bytes()).get('constitutionalRoleCorrections',[]),*role_corrections]
 role_corrections=list({(r['country'],r['removedFromPostwarGovernmentRole']):r for r in role_corrections}.values())
 write('public/data/polity-facts.json',facts)
 write('public/data/postwar-leadership-review.json',{'reviewedAt':'2026-10-31','window':[1945,1955],'method':'Candidate roster + exact named office + bounded person term; country heading text never used as a country match.','records':changes,'constitutionalRoleCorrections':role_corrections})
 actual={r['value']for r in changes if r['value']in people};(CACHE/'verified-people.json').write_text(json.dumps({q:people[q]for q in actual},ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print('Postwar office-matched records',len(changes),'country entities',len({r['country']for r in changes}),'people',len(actual),flush=True)

if __name__=='__main__':main()
