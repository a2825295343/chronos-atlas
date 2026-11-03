"""Typed archive context for new coverage, with no invented prehistoric kings."""
import json
from pathlib import Path
from territory_repair_stage import ROOT,read,write
TAG='coverage-archive-2026-11-01'

def main():
 definitions={**read('public/data/regional-coverage-definitions.json'),**read('public/data/early-coverage-definitions.json')};facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json');records=[]
 for e in facts['entities'].values():
  for k,rows in e['fields'].items():e['fields'][k]=[r for r in rows if r.get('supplement')!=TAG]
 def add(q,field,text,a,b,url,only_uncovered=False,**extra):
  e=facts['entities'][q];periods=[(a,b)]
  if only_uncovered:
   for old in e['fields'].get(field,[]):
    if old.get('from')is None or old.get('to')is None:continue
    x,y=old['from'],old['to'];more=[]
    for lo,hi in periods:
     if y<lo or x>hi:more.append((lo,hi))
     else:
      if lo<x:more.append((lo,x-1))
      if y<hi:more.append((y+1,hi))
    periods=more
  for lo,hi in periods:
   r={'value':text,'label':text,'from':lo,'to':hi,'at':None,'citation':[url],'supplement':TAG,**extra};e['fields'].setdefault(field,[]).append(r);records.append({'country':q,'field':field,**r})
 for n,d in definitions.items():
  q=d['qid'];e=facts['entities'].setdefault(q,{'label':d['label'],'en':n,'description':d['note'],'fields':{}});e['label']=d['label'];facts['labels'][q]=d['label'];cur['identities'][n]=q
  a,b=d['from'],d['to'];url=d['source'];arch=d.get('representationKind')in ['archaeological-culture','human-presence']
  if arch:
   e.update(description='人群活动与文化分布的概览；具体年代、轮廓和推断方法以当前地图记录的说明及来源为准，不把某一分期的参考年份套用到其他时期。',rulerScopeNote='考古文化是依据遗址、器物与生活方式划分的研究单位，不能直接等同国家、民族或一个王朝。')
   add(q,'government','依据聚落、墓葬、生产与交换网络研究其社会组织；各中心可能存在差异，不能据分布范围推定一个统一中央政府',a,b,url)
   add(q,'ruler','尚无适用于整个文化分布区的、可由史料确定的共同统治者姓名',a,b,url,kind='unrecorded',roleLabel='考古记录与具名人物的区别')
   add(q,'religion','可研究仪式场所、墓葬、图像与器物所反映的信仰活动；具体神名、统一国教及其覆盖人群不能仅凭图案确定',a,b,url)
   add(q,'ideology','不将近现代意识形态类别回填到史前社群；社会结构的解释须与遗址证据对应',a,b,url)
   add(q,'conflictEvidence','城墙、防御设施、武器和创伤须按具体遗址与年代判断；分布重合或文化更替本身不能证明发生过一场有明确双方的战争',a,b,url)
  elif d['regional']:
   add(q,'government','多个地方政权、君长、村社或议事网络并存；该地域集合不是一个统一中央政府',a,b,url,only_uncovered=True)
   add(q,'ruler','各地统治者与地方议事机构（不存在可适用于全域的共同君主）',a,b,url,only_uncovered=True,kind='collective',roleLabel='地域集合，不代替逐邦君主名录')
   add(q,'religion','地方信仰、礼制与宗教联系存在差异；不推定整个集合有统一国教',a,b,url,only_uncovered=True)
  elif not e['fields'].get('government'):
   add(q,'government','有据可查的历史王权或地方政权；具体官制、继承与地方行政仍需按年份细分',a,b,url,derived=True,inference='仅补政治组织的最低限度概括，不从名称猜测宗教或具体君主。')
 # Actual institutional and court context, not guesses from a modern ethnicity.
 groups=[
 (['Ahmadnagar Sultanate','Bijapur Sultanate','Golconda Sultanate','Bidar Sultanate'],'苏丹、宫廷官僚与军事贵族构成的德干苏丹国；继承、财政与地方行政随时期变化','苏丹宫廷以伊斯兰教礼制为主，逊尼派／什叶派取向随王室和时期变化；境内印度教与其他信仰社群并存','艾哈迈德讷格尔、比贾布尔、戈尔康达或比达尔等各自王都，不设共同首都'),
 (['Gujarat Sultanate','Malwa Sultanate'],'苏丹王权与地方军政官署','王室伊斯兰教与苏菲网络具有重要地位，印度教、耆那教及其他社群并存','艾哈迈达巴德（古吉拉特）；曼杜（马尔瓦），按本国区分'),
 (['Madurai Nayak Kingdom','Thanjavur Nayak Kingdom'],'纳亚克王权与地方领主、寺庙和财政网络；早期与毗奢耶那伽罗有隶属联系','王室主要奉印度教礼制，湿婆与毗湿奴传统、寺庙赞助及地方信仰并存','马杜赖；坦贾武尔，按本国区分'),
 (['Kingdom of Cochin','Kingdom of Travancore'],'地方君主制；与欧洲商贸、保护及殖民体系的关系分阶段变化','王室以印度教礼制为主；境内有基督徒、穆斯林、犹太人等不同社群','科钦诸王室中心；帕德马纳巴普拉姆／特里凡得琅，按国家和年代区分'),
 (['Ahom Kingdom'],'阿洪王权、派克劳役与军政职官体系；制度与莫卧儿关系经历变化','阿洪本土礼制与印度教传统逐渐融合，不表示所有时期或所有居民信奉同一种宗教','迦尔冈、朗布尔等王室中心，随年代变化'),
 (['Nabhani Oman'],'纳卜汉王权、伊玛目与部族首领竞争并存的格局','伊巴德派伊斯兰教与地方宗教机构具有重要地位，王权与伊玛目权威不能始终等同','拜赫莱及阿曼内陆诸中心'),
 (['Yaruba Imamate'],'伊玛目领导的亚鲁卜政权；晚期存在王位争夺与部族分裂','伊巴德派伊斯兰教政治与宗教传统','鲁斯塔克、尼兹瓦等中心'),
 (['Omani Al Busaidi State'],'布赛义德王权及其地方军政与商贸网络；与内陆伊玛目的关系分期变化','伊巴德派王室传统；沿海与内陆社群并不完全同质','马斯喀特、鲁斯塔克等政治中心，随时期变化'),
 (['Emirate of Diriyah','Emirate of Nejd'],'沙特家族伊玛目／埃米尔统治，与宗教权威、绿洲首领和部族网络相联系','逊尼派伊斯兰教，18世纪改革运动与王室联盟是重要政治基础','德拉伊耶（第一国家）；利雅得（第二国家），按时期区分'),
 (['Qasimid Imamate of Yemen'],'卡西姆家族宰德派伊玛目政权及地方军政网络','宰德派什叶派王室与学者传统；也门其他地区并非全部同一教派','萨那及也门高地政治中心，实际驻地曾变化'),
 (['Caucasian Imamate'],'伊玛目、纳伊卜与地方军事行政组成的山地政权','逊尼派伊斯兰教及苏菲网络，在不同山社的影响力存在差异','达尔戈、韦杰诺等阶段性政治与军事中心'),
 (['British India'],'东印度公司殖民行政与英国政治监督；土邦的间接统治、贸易据点和直接管辖区分开理解','殖民机构不能代表全体居民的宗教；印度教、伊斯兰教、锡克教、基督教、耆那教等并存','加尔各答等公司行政中心；孟买、马德拉斯为不同管区中心'),
 ]
 capitals={'Ahmadnagar Sultanate':'艾哈迈德讷格尔；后期有其他驻地','Bijapur Sultanate':'比贾布尔','Golconda Sultanate':'戈尔康达；1591年后海得拉巴逐渐成为重要王都','Bidar Sultanate':'比达尔','Gujarat Sultanate':'艾哈迈达巴德','Malwa Sultanate':'曼杜','Madurai Nayak Kingdom':'马杜赖／蒂鲁吉拉帕利，随王廷迁移而变','Thanjavur Nayak Kingdom':'坦贾武尔','Kingdom of Cochin':'科钦与特里普尼图拉等王室中心','Kingdom of Travancore':'帕德马纳巴普拉姆；后期为特里凡得琅','Emirate of Diriyah':'德拉伊耶','Emirate of Nejd':'利雅得'}
 for names,gov,religion,capital in groups:
  for n in names:
   if n not in definitions:continue
   d=definitions[n];q=d['qid'];a,b=d['from'],d['to'];url=d['source']
   for field,text in [('government',gov),('religion',religion),('capital',capitals.get(n,capital))]:add(q,field,text,a,b,url)
 # Period-specific context for the named ancient rulers added separately.
 ancient=[
 ('Q177819',-2686,-2181,'法老王权、中央官署与地方诺姆行政，王室礼制与官僚体系逐渐发展','多神祭祀、太阳神与地方神传统，王室丧葬与金字塔礼制重要','孟斐斯及王室墓地、地方行政中心','https://www.ucl.ac.uk/museums-static/digitalegypt/chronology/index.html'),
 ('Q191324',-2055,-1650,'法老王权与中央、地方官署的重组，地方权力随阶段变化','王室与地方神祭祀、奥西里斯信仰及丧葬礼制','底比斯、伊奇塔维等王室中心，按时期变化','https://www.ucl.ac.uk/museums-static/digitalegypt/chronology/index.html'),
 ('Q180568',-1550,-1070,'法老与中央官僚、军队、地方行政和神庙机构组成的王权体制','阿蒙、拉、奥西里斯等多神传统；阿肯那顿时期的阿顿政策是重要例外，不等于全时期单一礼制','底比斯、阿玛尔纳、比拉美西斯等随王廷迁移的中心','https://www.ucl.ac.uk/museums-static/digitalegypt/chronology/index.html'),
 ('Q2320005',-305,-30,'托勒密王室的希腊化君主制，保留并调整埃及官僚、财政与神庙机构','希腊与埃及宗教传统、王室祭祀及地方社群信仰并存','亚历山大里亚','https://egymonuments.gov.eg/en/historical-periods/ptolemaic-period/'),
 ('Q389688',-550,-330,'大王、宫廷与行省总督体系；不同地区保留差异化行政与法律传统','王室铭文重视阿胡拉·马兹达，帝国内多种地方祭祀传统持续存在；不简单等同全国统一国教','帕萨尔加德、苏萨、波斯波利斯等多个王室中心','https://www.livius.org/articles/dynasty/achaemenids/achaemenid-kings/'),
 ('Q4461035',-2334,-2154,'以阿卡德王权为核心的跨城邦统治，王室、地方官署和军队相联系','苏美尔与阿卡德地区多神传统，城市守护神与王室祭祀并存','阿卡德城（确切遗址位置尚未最终确定）','https://www.metmuseum.org/essays/art-of-the-first-cities-in-the-third-millennium-b-c'),
 ('Q624887',-626,-539,'巴比伦王权及其宫廷、神庙与地方行政体系','马尔杜克与巴比伦多神宗教传统，存在其他地方与外来社群','巴比伦','https://en.wikipedia.org/wiki/Neo-Babylonian_Empire'),
 ('Q12490507',632,661,'哈里发、军政精英与部族网络组成的早期统治体系；继承、战争及内战改变政治秩序','早期伊斯兰教政权，境内有基督徒、犹太人及其他宗教社群','麦地那；阿里时期为库法','https://en.wikipedia.org/wiki/Rashidun_Caliphate'),
 ('Q8575586',661,750,'倭马亚哈里发王权与行省总督、军区和财政行政机构','伊斯兰教国家礼制；穆斯林内部派别与其他宗教社群并存','大马士革','https://en.wikipedia.org/wiki/Umayyad_Caliphate'),
 ('Q12536',750,1258,'阿拔斯哈里发及军政、财政官署；后期哈里发与布韦希、塞尔柱等实权集团的关系须分期理解','伊斯兰教国家礼制与多宗派社会；不同教法、思想和地方宗教社群并存','库法、巴格达、萨迈拉等阶段性中心','https://en.wikipedia.org/wiki/Abbasid_Caliphate'),
 ('Q139377',100,940,'阿克苏姆王权与红海贸易、地方行政及贵族网络','埃扎纳时期由旧有王室礼制转向基督教，具体改宗年有不同说法；之后基督教传统重要，仍有其他社群','阿克苏姆及其港口与贸易中心','https://whc.unesco.org/en/list/15/'),
 ('Q207521',1270,1974,'皇帝、地方贵族、教会及军政精英构成的复合王权，中央实际控制随年代变化','埃塞俄比亚正教在王室礼制中重要；苏塞尼约斯推行天主教的阶段须另分，境内有穆斯林与地方信仰社群','王廷驻地曾迁移；贡德尔、马格达拉、默克莱、亚的斯亚贝巴分别属于不同阶段','https://whc.unesco.org/en/list/19/'),
 ]
 for q,a,b,gov,religion,capital,url in ancient:
  if q not in facts['entities']:continue
  for field,text in [('government',gov),('religion',religion),('capital',capital)]:add(q,field,text,a,b,url,only_uncovered=True)
 # Fix the source's Scottish-family/language-style identity collision in Yemen.
 for path in (ROOT/'public/data/temporal').glob('*.geojson'):
  d=json.loads(path.read_bytes());changed=False
  for f in d['features']:
   p=f['properties']
   if p['NAME']=='Qasimids':p.update(sourceQid=p.get('sourceQid',p.get('qid')),qid='local:qasimid-yemen',entityId='local:qasimid-yemen',displayName='也门卡西姆伊玛目国',identityCorrection='按也门卡西姆国家关联，不使用苏格兰同名家族实体。');changed=True
  if changed:path.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 cur['identities']['Qasimids']='local:qasimid-yemen'
 translations={n:d['label']for n,d in definitions.items()};translations['Qasimids']='也门卡西姆伊玛目国'
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json','src/localization/names.zh.json']:
  labels=read(path);labels.update(translations);write(path,labels)
 provenance=read('src/localization/provenance.json');provenance.update({n:'reviewed-historical-context'for n in translations});write('src/localization/provenance.json',provenance)
 reviewed={}
 for r in read('public/data/chronology-corrections.json')['identityCorrections']:reviewed.setdefault(r['name'],set()).add(r['qid'])
 for n,qs in reviewed.items():
  if n in definitions or len(qs)>1:cur['identities'].pop(n,None)
 write('public/data/polity-facts.json',facts);write('public/data/curated-facts.json',cur)
 write('public/data/coverage-archive-review.json',{'reviewedAt':'2026-11-01','records':records,'summary':{'datedContextRecords':len(records),'identities':len(definitions)},'limitations':['地域集合与考古文化不虚构统一君主和国家旗帜。','补绘多边形的面积不是考古文化精确占地面积，也不是人口分布密度。']});print('Coverage archive rows',len(records),'identities',len(definitions),flush=True)
if __name__=='__main__':main()
