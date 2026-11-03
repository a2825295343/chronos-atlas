"""Dated institutions, religion, imperial relations, and reviewed identity fixes.
Regional collections are not assigned fictitious common kings or state faiths.
"""
import copy,json,re,hashlib
from pathlib import Path
from territory_repair_stage import ROOT,read,write
TAG='global-historical-context-2026-10-31'
LIVONIA='https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/20/71/66/01/2020716601/2020716601.pdf'
HRE='https://www.historisches-lexikon-bayerns.de/Lexikon/EN%3AElectors'
MAGHRIB='https://doi.org/10.1093/acrefore/9780190277734.013.415'
FIAV='https://fiav.org/wp-content/uploads/2021/05/17-30-Martykan-HistoryOfOttomanNavalFlags.pdf'
KOTTE='https://www.uda.gov.lk/attachments/dev-plans-2021-2030/kotte_development_plan_Eng.pdf.pdf'
def main():
 facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json');identities={};catalog={};changed=[]
 aliases={'Livonian Conference':('Livonian Confederation','利沃尼亚邦联','Q1064825','Q33698')}
 for path in(ROOT/'public/data/temporal').glob('*.geojson'):
  data=json.loads(path.read_bytes());dirty=False
  for f in data['features']:
   p=f['properties'];n=p['NAME']
   if n in aliases:
    name,label,q,old=aliases[n];p.update(NAME=name,SUBJECTO=name,qid=q,entityId=q,sourceQid=old,displayName=label,wikipedia='Terra Mariana',identityReviewed=True,identityCorrection='源记录Livonian Conference错误关联立窝尼亚语；改为利沃尼亚诸领地／邦联，语言不是领土政权。',sourceUrl=LIVONIA,regionalCollection=True,representationNote='骑士团、主教领和城市的松散政治联合；没有一位统治全邦联的共同国王。此轮保留外部轮廓，未补造各成员精确内界。');dirty=True;identities[n]=q;identities[name]=q
   if p['NAME']=='Sasanian Empire':p.update(qid='Q83891',entityId='Q83891',sourceQid=p.get('sourceQid','Q1661685'),identityReviewed=True,identityCorrection='萨珊帝国与印度—萨珊地方政权分开，不复用错误实体。');dirty=True;identities[p['NAME']]='Q83891'
   if p['NAME']=='Qajar Dynasty':p['displayName']='伊朗';dirty=True
   if p.get('sourceUrl')=='https://www.nationalarchives.gov.uk/education/resources/british-empire/iraq/':p['sourceUrl']='https://searcharchives.bl.uk/catalog/040-000545804';dirty=True
   q=cur['identities'].get(p['NAME'],p.get('qid'))
   if p['NAME']=='Sasanian Empire':q='Q83891'
   if q:
    entry=catalog.setdefault(q,{'from':p['validFrom'],'to':p['validTo'],'names':set(),'label':p.get('displayName',p['NAME']),'regional':False})
    entry['from']=min(entry['from'],p['validFrom']);entry['to']=max(entry['to'],p['validTo']);entry['names'].add(p['NAME']);entry['regional']|=p.get('regionalCollection',False)
  if dirty:path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 cur['identities'].update(identities)
 names=read('src/localization/display-names.zh.json');names.update({'Livonian Conference':'利沃尼亚邦联','Livonian Confederation':'利沃尼亚邦联','Qajar Dynasty':'伊朗'});write('src/localization/display-names.zh.json',names)
 names=read('src/localization/temporal.zh.json');names.update({'Livonian Conference':'利沃尼亚邦联','Livonian Confederation':'利沃尼亚邦联'});write('src/localization/temporal.zh.json',names)
 for e in facts['entities'].values():
  for field,rows in list(e['fields'].items()):e['fields'][field]=[r for r in rows if r.get('supplement')!=TAG]
 def add(q,field,label,a,b,source,value=None,**extra):
  e=facts['entities'].setdefault(q,{'label':catalog.get(q,{}).get('label',q),'en':next(iter(catalog.get(q,{}).get('names',[])),''),'description':'','fields':{}})
  row={'value':value or field+':'+hashlib.sha1(label.encode()).hexdigest()[:12],'label':label,'from':a,'to':b,'at':None,'citation':[source],'supplement':TAG,**extra};e['fields'].setdefault(field,[]).append(row);changed.append({'country':q,'field':field,**row})
 # Explicit profiles use the period's institution, not a modern regime or a
 # claim that every inhabitant held the court's faith.
 profiles=[
 ('Q389688',-550,-330,'大王／万王之王统辖的帝国，行省总督与地方政治结构并行','波斯波利斯、苏萨、巴比伦等多处王室中心','伊朗传统宗教与阿胡拉·马兹达王权礼制；不是所有臣民统一信仰','https://www.iranicaonline.org/articles/achaemenid-dynasty/'),
 ('Q83891',224,651,'沙汗沙阿统辖的萨珊君主国，贵族、官僚与宗教机构共同构成权力结构','泰西封；伊斯塔赫尔为早期王朝中心','琐罗亚斯德教在王权与国家礼制中居重要地位；亦有基督徒、犹太人及其他信仰社群','https://www.iranicaonline.org/articles/sasanian-dynasty/'),
 ('Q2320005',-305,-30,'希腊化君主制；托勒密王室统治埃及，延用法老王权礼制','亚历山大里亚','埃及传统神祇与希腊宗教、王室崇拜并存；不能概括为单一民族宗教','https://www.metmuseum.org/essays/the-ptolemaic-period'),
 ('Q705904',-305,-63,'塞琉古王朝君主制，城市与地方总督体系并存','塞琉西亚、安条克等王室中心，随时期变迁','希腊与西亚地方神祇、王室崇拜等并存，地区差异显著','https://www.britannica.com/topic/Seleucid-kingdom'),
 ('Q62943',-322,-185,'以摩揭陀为核心的孔雀帝国君主制，中央与地方官员治理并行','华氏城','婆罗门传统、佛教、耆那教等并存；阿育王时期倡导法与宗教宽容，不等于全体臣民改宗','https://digital.library.cornell.edu/catalog/ss%3A3856336'),
 ('Q11774',320,550,'笈多王朝君主制，地方王侯与封臣关系具有重要作用','华氏城等政治中心，王室驻地随时期变化','婆罗门教／印度教王室礼制居重要地位；佛教、耆那教等亦有发展','https://www.britannica.com/place/India/The-Guptas'),
 ('Q6806806',848,1279,'朱罗王朝君主制，地方行政、寺庙机构与自治村社并存','坦贾武尔；11世纪起有甘盖孔达朱罗普兰','以湿婆崇拜为主的印度教王室传统，同时存在毗湿奴、佛教与耆那教社群','https://www.metmuseum.org/essays/the-chola-dynasty-ca-850-1279'),
 ('Q167639',1336,1646,'毗奢耶那伽罗君主国，王室、地方那耶克与寺庙政治并存','胜利城（亨比）；1565年以后王室中心迁移','印度教王室礼制与多元信仰社群并存，不将教派和臣民信仰统一化','https://whc.unesco.org/en/list/241/'),
 ('Q33296',1526,1857,'莫卧儿皇帝统治的君主帝国；曼萨卜与地方财政、行政制度随时期发展','阿格拉、德里等王室中心，随时期迁移','穆斯林王室，臣民信仰多样；阿克巴等时期政策与后世不同','https://www.metmuseum.org/essays/the-art-of-the-mughal-period-1526-1858'),
 ('Q161205',1501,1736,'萨法维沙阿君主制，部族军事与中央官僚结构随时期变化','大不里士、加兹温，1598年起主要为伊斯法罕','十二伊玛目派什叶派在国家礼制中居主导地位；臣民仍有宗教差异','https://www.metmuseum.org/essays/the-art-of-the-safavids-before-1600'),
 ('Q184536',1235,1600,'曼萨统治的马里王国／帝国，地方王侯与政治联盟并存','尼亚尼传统王都及随王室迁移的政治中心','王室与城市精英中的伊斯兰教，与曼德地方宗教传统并存','https://www.metmuseum.org/essays/the-empire-of-mali-1230-1600'),
 ('Q28573',1200,1572,'萨帕·印加王权统辖的政体；帝国扩张时期以四方之地及地方首领体系治理','库斯科；抵抗时期的政权另有比尔卡班巴中心','太阳神因蒂、瓦卡圣地与祖先崇拜等国家与地方礼制并存','https://www.metmuseum.org/essays/the-incas'),
 ('Q2608489',1428,1521,'以特诺奇蒂特兰、特斯科科与特拉科潘三邦联盟为基础的霸权与贡赋体系，不是所有成员完全行政合并','特诺奇蒂特兰等三邦中心','纳瓦多神教与各城市祭祀体系并存','https://www.metmuseum.org/essays/the-aztec-empire'),
 ('local:great-zimbabwe',1220,1450,'以大津巴布韦为核心的君主政体；早期王名与详细任期缺乏充分文献','大津巴布韦','地方祖先与圣地祭祀传统；具体国家礼制仍有研究分歧','https://whc.unesco.org/en/list/364/'),
 ('local:kingdom-of-benin',1200,1897,'奥巴君主、宫廷与贵族／行会等机构共同构成的贝宁王国；与现代贝宁共和国分开','贝宁城（今尼日利亚埃多地区）','王室祖先祭祀与埃多地方神祇传统；不概括为统一现代国教','https://www.britishmuseum.org/about-us/british-museum-story/contested-objects-collection/benin-bronzes'),
 ('local:kingdom-of-kongo',1390,1884,'曼尼刚果君主制与地方省侯体系；内战时可能存在多个竞争王位中心','姆班扎刚果（圣萨尔瓦多）','刚果地方宗教传统；1491年后王室与部分精英接受天主教，地方传统继续存在','https://whc.unesco.org/en/list/1511/'),
 ('local:mutapa',1450,1760,'穆塔帕君主国及其地方首领网络；不与更早的大津巴布韦所有时期混同','穆塔帕王室政治中心随时期迁移','祖先祭祀与地方宗教传统；传教与贸易接触不等于全国改宗','https://www.britannica.com/place/Monomotapa'),
 ('local:kingdom-of-kotte',1412,1556,'僧伽罗君主制，科提与其他岛上王国的控制范围随时期变化','斯里贾亚瓦德纳普拉科提','上座部佛教王权礼制占重要地位；仍有其他信仰社群',KOTTE),
 ('local:kingdom-of-kandy',1469,1815,'康提君主制；早期与科提的关系及自主程度经历变化','康提','上座部佛教王权传统，寺院和地方贵族具有重要作用','https://www.britannica.com/place/Kandy-historical-kingdom-Sri-Lanka'),
 ('local:yettishar',1865,1877,'阿古柏领导的军事君主政权；与清朝、俄国及地方力量的关系分开理解','喀什','逊尼派伊斯兰教王室与地方宗教机构','https://islamansiklopedisi.org.tr/yakub-beg'),
 ('local:tomara-delhi',900,1151,'托马拉王权政体；早期年代与领主世系仍有研究分歧','德里及其周边政治中心','印度教王权与地方宗教传统','https://www.britannica.com/place/Delhi/History'),
 ('local:gajapati-kingdom',1434,1541,'加贾帕提王权的奥里萨君主国','克塔克；普里为重要宗教中心','印度教王室礼制，贾格纳特崇拜具有重要地位','https://www.britannica.com/place/Odisha/History'),
 ('local:cahokia',1050,1350,'密西西比文化的大型城市与酋邦政治中心；不是无政治组织的空白地带','卡霍基亚','地方圣地、祖先与仪式传统；不能推定一个有文献确证的统一国教','https://whc.unesco.org/en/list/198/'),
 ('Q1064825',1237,1561,'骑士团、主教领与城市组成的松散政治体系；1435年以后邦联协议具有重要作用，不是统一君主国','里加等多个成员中心，不设一个共同王都','统治机构以拉丁基督教传统为主；当地居民及城市信仰并非没有差异',LIVONIA),
 ]
 for q,a,b,gov,capital,religion,source in profiles:
  for field,text in [('government',gov),('capital',capital),('religion',religion)]:add(q,field,text,a,b,source,derived=True,inference='依该政权历史制度与宗教背景补充；不把王室礼制等同所有居民信仰。')
 for q in ['Q12544','Q112039853']:
  add(q,'government','东罗马皇帝、宫廷官僚与教会等机构构成的帝国体制；行政和军事制度随时代变化',395,1453,'https://www.metmuseum.org/essays/byzantium-330-1453')
  add(q,'capital','君士坦丁堡；1204年失陷后的流亡与重建阶段须分别理解',395,1453,'https://www.metmuseum.org/essays/byzantium-330-1453')
  add(q,'religion','基督教与东部教会传统；1054年后的时期通常称东正教，存在教派与地方差异',395,1453,'https://www.metmuseum.org/essays/byzantium-330-1453')
 add('Q2277','government','元首制下的皇帝权力与元老院等共和国形式并存',-27,283,'https://www.britannica.com/place/Roman-Empire')
 add('Q2277','government','后期罗马皇帝统治与中央官僚、军队体系；共治与东西分治另按任期表示',284,394,'https://www.britannica.com/place/Roman-Empire')
 for a,b,text in [(-27,312,'罗马与地方多神教、国家祭祀及皇帝崇拜并存；亦有犹太教与早期基督徒'),(313,379,'基督教获得合法地位并扩大影响；不是313年所有臣民统一改宗'),(380,394,'尼西亚派基督教获得国家支持，仍存在其他宗教社群')]:add('Q2277','religion',text,a,b,'https://www.britannica.com/place/Roman-Empire')
 for q,e in list(catalog.items()):
  if not e['regional']:continue
  a,b=e['from'],e['to'];source=next((r['source']for r in read('public/data/expanded-territory-review.json')['records']if r['name']in e['names']),'https://github.com/aourednik/historical-basemaps')
  fields=facts['entities'].setdefault(q,{'label':e['label'],'en':next(iter(e['names'])),'description':'','fields':{}})['fields']
  if not fields.get('government'):add(q,'government','多个地方政权、君长或议事机构并存；此地域集合不是一个统一中央政府',a,b,source,derived=True)
  if not fields.get('ruler'):add(q,'ruler','各地君长／议事机构（无适用于全域的单一共同统治者）',a,b,source,value='local:plural-authorities:'+q,kind='collective',roleLabel='地域集合，不是已补齐每位地方统治者')
  if not fields.get('religion'):add(q,'religion','各地信仰与礼制存在差异；不推定一个统一国家宗教',a,b,source,derived=True)
 # Explicitly inferred constitutional type is used only where the actual name
 # already establishes it. A dynasty name alone proves neither religion nor an
 # administrative system.
 inferred=0
 for q,e in catalog.items():
  entity=facts['entities'].get(q)
  if not entity or entity['fields'].get('government')or e['regional']:continue
  text=' '.join(e['names'])
  gov='以君主为核心的政体（由王国／帝国称谓推断，具体制度待逐年细分）'if re.search(r'Kingdom|Empire|Sultanate|Caliphate|Principality|Duchy',text)else'共和国称谓下的政体，具体权力结构仍需按年代区分'if'Republic'in text else None
  if gov:add(q,'government',gov,e['from'],e['to'],'https://github.com/Seshat-Global-History-Databank/cliopatria',derived=True,inference='仅由已知政治称谓作最低限度制度推断；不宣称已核定具体宪制。');inferred+=1
 # Imperial allegiances are separate from colonial administration and common
 # crowns. Existing reciprocal/membership records are deduplicated in the UI.
 relations=[r for r in cur['relations']if r.get('supplement')!=TAG]
 imperial=['Ascanian Saxon Duchies','Bavarian Wittelsbach Duchies','Swabian Hohenstaufen Lands','Habsburg Upper Rhine Lands','Austrian Hereditary Lands','Kingdom of Bohemia','County of Luxembourg','Duchy of Luxembourg','Electorate of Brandenburg','Margraviate of Brandenburg','Duchy of Bavaria','Electorate of Bavaria','Electorate of Saxony','Duchy of Saxony','Electoral Palatinate','Palatinate of the Rhine','Duchy of Württemberg','Wuerttemburg','Baden','Duchy of Lorraine','Archbishopric of Mainz','Archbishopric of Trier','Archbishopric of Cologne','Duchy of Brunswick-Lüneburg','Duchy of Mecklenburg','Landgraviate of Hesse']
 namebounds={n:(e['from'],e['to'])for e in catalog.values()for n in e['names']}
 for n in imperial:
  if n not in namebounds:continue
  lo,hi=namebounds[n];a,b=max(962,lo),min(1806,hi)
  if a<=b:relations.append({'id':TAG+':hre:'+n,'kind':'vassal','child':n,'parent':'Holy Roman Empire','from':a,'to':b,'title':'神圣罗马帝国诸侯／领地关系','detail':'帝国框架内的诸侯或领地关系；可保有地方行政和等级权利。不是现代国家间平等联盟，不是殖民地；特殊豁免与实际自主权随时期变化。','source':HRE,'supplement':TAG})
 for q,lo,hi,detail in [('Q3045696',1519,1829,'阿尔及尔接受奥斯曼宗主权，其地方军政与德伊体制逐渐取得较大自主权。'),('Q4899891',1574,1880,'1574年后处于奥斯曼政治框架；贝伊世袭与实际自主不等于完全不存在宗主关系。'),('Q1929987',1711,1835,'卡拉曼利家族统治的的黎波里在奥斯曼宗主权下具有显著自主权；1835年后中央重新加强控制。'),('Q1529261',1864,1912,'奥斯曼的黎波里维拉耶，1911年意大利入侵与1912年条约交接发生在年内。')]:
  for n in catalog.get(q,{}).get('names',[]):relations.append({'id':TAG+':ottoman:'+n,'kind':'vassal','child':n,'parent':'Ottoman Empire','from':lo,'to':hi,'title':'奥斯曼宗主权／地方自治关系','detail':detail+'宗主权、实际军政控制及地方统治者分开表示。','source':MAGHRIB,'supplement':TAG})
 for n in namebounds:
  if re.search(r'^(Tripoli Eyalet|Ottoman Tripolitania|Regency of Tripoli)$',n):relations.append({'id':TAG+':tripoli:'+n,'kind':'vassal','child':n,'parent':'Ottoman Empire','from':1551,'to':1912,'detail':'奥斯曼北非省区／地方自治统治；不把摩洛哥列为奥斯曼属国。','source':MAGHRIB,'supplement':TAG})
 cur['relations']=relations;write('public/data/curated-facts.json',cur);write('public/data/polity-facts.json',facts)
 # Replace the visually blank white early Ottoman placeholder with a sourced
 # naval-type identification reconstruction. Its retrospective early use is
 # conspicuously labelled rather than asserted to be a proven original flag.
 config=read('public/data/historical-flag-supplements.json');config['records']=[r for r in config['records']if not(r['qid']=='Q12560'and r['file']=='White flag 3 to 2.svg')]
 for a,b,role,note in [(1305,1361,'早期奥斯曼识别参考 · 回溯推定','此阶段缺少可核实的统一旗式；借14世纪后期有记载的红底新月海军旗作政权识别参考，不表示1305年已采用此旗。'),(1362,1511,'红底新月海军旗 · 文字史料复原','依据早期奥斯曼舰船使用红底横向新月旗的研究重绘，比例与细节为识别性复原；不是现代五星国旗，也不声称全国只有一种旗。')]:
  row={'qid':'Q12560','file':'Guanlan early Ottoman naval banner reconstruction.svg','path':'/data/flags/ottoman-early-naval-reconstruction.svg','from':a,'to':b,'at':None,'role':role,'periodNote':note,'periodSource':FIAV,'source':FIAV,'commons':FIAV,'artist':'观澜：按文字史料作基本几何复原','license':'CC0（本项目基本几何重绘；史料图源另见出处）','representative':True,'reconstructed':True}
  config['records']=[r for r in config['records']if not(r['qid']=='Q12560'and r.get('from')==a)];config['records'].append(row)
 for q in ['local:kingdom-of-kotte']:
  row={'qid':q,'file':'Flag of Kotte.svg','from':1412,'to':1597,'role':'科提王国代表旗 · 博物馆旗式重绘','periodNote':'图像作者依据科提博物馆现存旗式重绘；政府发展规划亦展示15世纪—1597年的科提旗。不能把这幅后世重绘当作1506年留存的原件。','periodSource':KOTTE,'representative':True}
  config['records']=[r for r in config['records']if not(r['qid']==q and r.get('from')==1412)];config['records'].append(row)
 write('public/data/historical-flag-supplements.json',config)
 flags=read('public/data/flags.json');flags['entities']['Q12560']=[r for r in flags['entities']['Q12560']if r['file']!='White flag 3 to 2.svg'];write('public/data/flags.json',flags)
 report={'reviewedAt':'2026-10-31','records':changed,'relations':[r for r in relations if r.get('supplement')==TAG],'summary':{'datedFacts':len(changed),'relationshipRecords':sum(r.get('supplement')==TAG for r in relations),'constitutionalInferences':inferred},'limitations':['地域集合的无共同君主，不等于已补齐所有地方王名。','称谓推断的政体明确标注，不按国家名称猜测宗教。','奥斯曼早期军旗识别复原标明回溯阶段，未伪称原旗出土。']};write('public/data/global-context-review.json',report);print(report['summary'],flush=True)
if __name__=='__main__':main()
