"""Exact person identities and sourced reigns for previously uncovered polities.

Transition years may show successive holders. No lifespan-to-reign inference.
"""
import argparse,hashlib,json,subprocess,urllib.parse,copy
from territory_repair_stage import ROOT,read,write
from prepare_global_archive_review import human
from enrich_polities import label,simplify
TAG='global-reigns-2026-11-02';CACHE=ROOT/'.local/global-reigns-nov02';CACHE.mkdir(exist_ok=True)
ROWS=[]
ALIASES={'Jeongjong of Goryeo (3rd monarch)':'Jeongjong, 3rd monarch of Goryeo','Jeongjong of Goryeo (10th monarch)':'Jeongjong, 10th monarch of Goryeo','Sunni Ali':'Sonni Ali','Sunni Baru':'Sonni Baru','Askia Muhammad Benkan':'Askia Mohammad Benkan','Muhammad bin Abdullah Al Khalili':'Muhammad al-Khalili'}
def roster(q,source,role,rows):
 for title,zh,a,b in rows:ROWS.append(dict(country=q,title=title,label=zh,start=a,end=b,source=source,role=role))

roster('Q28208','https://db.history.go.kr/goryeo/','高丽国王',[
 ('Taejo of Goryeo','高丽太祖王建',918,943),('Hyejong of Goryeo','高丽惠宗',943,945),('Jeongjong of Goryeo (3rd monarch)','高丽定宗',945,949),('Gwangjong of Goryeo','高丽光宗',949,975),('Gyeongjong of Goryeo','高丽景宗',975,981),('Seongjong of Goryeo','高丽成宗',981,997),('Mokjong of Goryeo','高丽穆宗',997,1009),('Hyeonjong of Goryeo','高丽显宗',1009,1031),('Deokjong of Goryeo','高丽德宗',1031,1034),('Jeongjong of Goryeo (10th monarch)','高丽靖宗',1034,1046),('Munjong of Goryeo','高丽文宗',1046,1083),('Sunjong of Goryeo','高丽顺宗',1083,1083),('Seonjong of Goryeo','高丽宣宗',1083,1094),('Heonjong of Goryeo','高丽献宗',1094,1095),('Sukjong of Goryeo','高丽肃宗',1095,1105),('Yejong of Goryeo','高丽睿宗',1105,1122),('Injong of Goryeo','高丽仁宗',1122,1146),('Uijong of Goryeo','高丽毅宗',1146,1170),('Myeongjong of Goryeo','高丽明宗',1170,1197),('Sinjong of Goryeo','高丽神宗',1197,1204),('Huijong of Goryeo','高丽熙宗',1204,1211),('Gangjong of Goryeo','高丽康宗',1211,1213),('Gojong of Goryeo','高丽高宗',1213,1259),('Wonjong of Goryeo','高丽元宗',1259,1274),('Chungnyeol of Goryeo','高丽忠烈王',1274,1298),('Chungnyeol of Goryeo','高丽忠烈王',1298,1308),('Chungseon of Goryeo','高丽忠宣王',1298,1298),('Chungseon of Goryeo','高丽忠宣王',1308,1313),('Chungsuk of Goryeo','高丽忠肃王',1313,1330),('Chungsuk of Goryeo','高丽忠肃王',1332,1339),('Chunghye of Goryeo','高丽忠惠王',1330,1332),('Chunghye of Goryeo','高丽忠惠王',1339,1344),('Chungmok of Goryeo','高丽忠穆王',1344,1348),('Chungjeong of Goryeo','高丽忠定王',1348,1351),('Gongmin of Goryeo','高丽恭愍王',1351,1374),('U of Goryeo','高丽禑王',1374,1388),('Chang of Goryeo','高丽昌王',1388,1389),('Gongyang of Goryeo','高丽恭让王',1389,1392)])
roster('Q28179','https://sillok.history.go.kr/main/main.do','朝鲜国王',[
 ('Taejo of Joseon','朝鲜太祖李成桂',1392,1398),('Jeongjong of Joseon','朝鲜定宗',1398,1400),('Taejong of Joseon','朝鲜太宗',1400,1418),('Sejong the Great','朝鲜世宗',1418,1450),('Munjong of Joseon','朝鲜文宗',1450,1452),('Danjong of Joseon','朝鲜端宗',1452,1455),('Sejo of Joseon','朝鲜世祖',1455,1468),('Yejong of Joseon','朝鲜睿宗',1468,1469),('Seongjong of Joseon','朝鲜成宗',1469,1494),('Yeonsangun of Joseon','燕山君',1494,1506),('Jungjong of Joseon','朝鲜中宗',1506,1544),('Injong of Joseon','朝鲜仁宗',1544,1545),('Myeongjong of Joseon','朝鲜明宗',1545,1567),('Seonjo of Joseon','朝鲜宣祖',1567,1608),('Gwanghaegun of Joseon','光海君',1608,1623),('Injo of Joseon','朝鲜仁祖',1623,1649),('Hyojong of Joseon','朝鲜孝宗',1649,1659),('Hyeonjong of Joseon','朝鲜显宗',1659,1674),('Sukjong of Joseon','朝鲜肃宗',1674,1720),('Gyeongjong of Joseon','朝鲜景宗',1720,1724),('Yeongjo of Joseon','朝鲜英祖',1724,1776),('Jeongjo of Joseon','朝鲜正祖',1776,1800),('Sunjo of Joseon','朝鲜纯祖',1800,1834),('Heonjong of Joseon','朝鲜宪宗',1834,1849),('Cheoljong of Joseon','朝鲜哲宗',1849,1863),('Gojong of Korea','朝鲜高宗',1863,1897)])
roster('Q1115291','https://www.thaiembassy.at/en/content_page/item/18-thailands-history.html','吞武里国王',[('Taksin','郑信（达信大帝）',1767,1782)])
roster('Q1155700','https://www.thaiembassy.at/en/content_page/item/18-thailands-history.html','暹罗国王',[
 ('Rama I','拉玛一世',1782,1809),('Rama II','拉玛二世',1809,1824),('Rama III','拉玛三世',1824,1851),('Mongkut','拉玛四世（蒙固）',1851,1868),('Chulalongkorn','拉玛五世（朱拉隆功）',1868,1910),('Vajiravudh','拉玛六世（瓦栖拉兀）',1910,1925),('Prajadhipok','拉玛七世（巴差提朴）',1925,1932)])
roster('Q202687','https://openstax.org/books/world-history-volume-2/pages/3-2-the-songhai-empire','桑海统治者',[
 ('Sunni Ali','逊尼·阿里',1464,1492),('Sunni Baru','逊尼·巴鲁',1492,1493),('Askia Muhammad I','阿斯基亚·穆罕默德一世',1493,1528),('Askia Musa','阿斯基亚·穆萨',1528,1531),('Askia Muhammad Benkan','阿斯基亚·穆罕默德·本坎',1531,1537),('Askia Isma\'il','阿斯基亚·伊斯迈尔',1537,1539),('Askia Ishaq I','阿斯基亚·伊沙克一世',1539,1549),('Askia Daoud','阿斯基亚·达乌德',1549,1582),('Askia Ishaq II','阿斯基亚·伊沙克二世',1588,1591)])
roster('Q1071439','https://en.wikipedia.org/wiki/List_of_Imerina_monarchs','伊默里纳君主',[
 ('Andrianampoinimerina','安德里亚南普伊奈梅里纳',1787,1810),('Radama I','拉达马一世',1810,1828),('Ranavalona I','腊纳瓦洛娜一世',1828,1861),('Radama II','拉达马二世',1861,1863),('Rasoherina','腊佐赫里纳',1863,1868),('Ranavalona II','腊纳瓦洛娜二世',1868,1883),('Ranavalona III','腊纳瓦洛娜三世',1883,1897)])
roster('Q156418','https://www.nps.gov/articles/000/iolani-palace-a-hawaiian-place-of-history-power-and-prestige.htm','夏威夷君主',[
 ('Kamehameha I','卡美哈梅哈一世',1810,1819),('Kamehameha II','卡美哈梅哈二世',1819,1824),('Kamehameha III','卡美哈梅哈三世',1825,1854),('Kamehameha IV','卡美哈梅哈四世',1855,1863),('Kamehameha V','卡美哈梅哈五世',1863,1872),('Lunalilo','卢纳利洛',1873,1874),('Kalākaua','卡拉卡瓦',1874,1891),('Liliʻuokalani','利留卡拉尼',1891,1893)])
for q in ['local:qatar-protectorate','Q846']:
 roster(q,'https://diwan.gov.qa/en/About-Qatar/History-of-Qatar','卡塔尔统治者',[
  ('Mohammed bin Thani','穆罕默德·本·萨尼',1851,1878),('Jassim bin Mohammed Al Thani','贾西姆·本·穆罕默德·阿勒萨尼',1878,1913),('Abdullah bin Jassim Al Thani','阿卜杜拉·本·贾西姆·阿勒萨尼',1913,1949),('Ali bin Abdullah Al Thani','阿里·本·阿卜杜拉·阿勒萨尼',1949,1960),('Ahmad bin Ali Al Thani','艾哈迈德·本·阿里·阿勒萨尼',1960,1972),('Khalifa bin Hamad Al Thani','哈利法·本·哈马德·阿勒萨尼',1972,1995)])
roster('local:oman-imamate-1913','https://www.rafmuseum.org.uk/research/online-exhibitions/an-enduring-relationship-a-history/oman-and-the-cold-war/','阿曼伊玛目',[
 ('Salim bin Rashid al-Kharusi','萨利姆·本·拉希德·哈鲁西',1913,1920),('Muhammad bin Abdullah Al Khalili','穆罕默德·本·阿卜杜拉·哈利利',1920,1954),('Ghalib bin Ali','加利卜·本·阿里·希纳伊',1954,1959)])
roster('Q2571484','https://jklokbhavan.nic.in/aboutjk/','查谟和克什米尔大君；本条仅列土邦阶段，1947年为战争及归属交接年',[('Hari Singh','哈里·辛格',1925,1947)])

def fetch():
 pool=read('.local/global-reigns-nov02/verified-people.json')if(CACHE/'verified-people.json').exists()else{}
 have={e.get('sitelinks',{}).get('enwiki',{}).get('title')for e in pool.values()}
 titles=sorted({ALIASES.get(r['title'],r['title'])for r in ROWS}-have)
 for i in range(0,len(titles),25):
  params=urllib.parse.urlencode(dict(action='wbgetentities',format='json',sites='enwiki',titles='|'.join(titles[i:i+25]),props='labels|claims|sitelinks',languages='zh-hans|zh|en',redirects='yes'))
  p=CACHE/(hashlib.sha1(params.encode()).hexdigest()+'.json')
  if not p.exists():subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','--retry','2','https://www.wikidata.org/w/api.php?'+params,'--output',str(p)],check=True)
  pool.update({q:e for q,e in json.loads(p.read_bytes())['entities'].items()if human(e)})
 # The English Muhammad al-Khalili is a different scholar (d.1734).
 # Resolve the Omani imam through his exact Arabic biography instead.
 params=urllib.parse.urlencode(dict(action='wbgetentities',format='json',sites='arwiki',titles='محمد بن عبد الله الخليلي',props='labels|claims|sitelinks',languages='zh-hans|zh|en',redirects='yes'))
 p=CACHE/(hashlib.sha1(params.encode()).hexdigest()+'.json')
 if not p.exists():subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','https://www.wikidata.org/w/api.php?'+params,'--output',str(p)],check=True)
 for q,e in json.loads(p.read_bytes())['entities'].items():
  if human(e):e['reviewedExactTitle']='Muhammad bin Abdullah Al Khalili';pool[q]=e
 pool.pop('Q111696671',None)
 write('.local/global-reigns-nov02/verified-people.json',pool)
 print('Verified people',len(pool))

def apply():
 pool=read('.local/global-reigns-nov02/verified-people.json');bytitle={e.get('sitelinks',{}).get('enwiki',{}).get('title'):q for q,e in pool.items()}
 # No exact Wikidata biography is available for this imam. Keep an explicit
 # sourced local person identity rather than borrowing a namesake's portrait.
 imam='local:person-muhammad-bin-abdullah-al-khalili'
 pool[imam]={'id':imam,'labels':{'zh':{'value':'穆罕默德·本·阿卜杜拉·哈利利'}},'claims':{},'reviewedExactTitle':'Muhammad bin Abdullah Al Khalili'}
 pool['local:person-salim-bin-rashid-al-kharusi']={'id':'local:person-salim-bin-rashid-al-kharusi','labels':{'zh':{'value':'萨利姆·本·拉希德·哈鲁西'}},'claims':{},'reviewedExactTitle':'Salim bin Rashid al-Kharusi'}
 # Only exact canonical titles or exact English person labels are allowed.
 for q,e in pool.items():bytitle.setdefault(e.get('labels',{}).get('en',{}).get('value'),q)
 for q,e in pool.items():
  if e.get('reviewedExactTitle'):bytitle[e['reviewedExactTitle']]=q
 aliases=ALIASES
 missing=[r['title']for r in ROWS if aliases.get(r['title'],r['title'])not in bytitle and r['title']not in bytitle]
 if missing:raise ValueError('Unresolved exact identities: '+str(sorted(set(missing))))
 facts=read('public/data/polity-facts.json');review=[]
 for q in {r['country']for r in ROWS}:facts['entities'][q]['fields']['ruler']=[r for r in facts['entities'][q]['fields'].get('ruler',[])if r.get('supplement')!=TAG]
 for r in ROWS:
  q=bytitle.get(r['title'])or bytitle[aliases[r['title']]];a,b=r['start'],r['end']
  e=pool[q]
  def years(prop):return [int(s['value']['time'][:5])for c in e.get('claims',{}).get(prop,[])if(s:=simplify(c))and isinstance(s['value'],dict)and'time'in s['value']]
  if any(y>b for y in years('P569'))or any(y<a for y in years('P570')):raise ValueError('Person lifespan contradicts reign: '+r['title']+' '+q)
  if r['country']=='local:qatar-protectorate':a,b=max(1916,a),min(1971,b)
  if a>b:continue
  citations=[r['source'],'https://en.wikipedia.org/wiki/'+urllib.parse.quote(ALIASES.get(r['title'],r['title']).replace(' ','_')),'https://www.wikidata.org/wiki/'+q]if q.startswith('Q')else['https://www.jstor.org/stable/jj.17634940','https://ediss.sub.uni-hamburg.de/bitstream/ediss/11759/1/Dissertation%20.pdf']
  if r['title']=='Salim bin Rashid al-Kharusi':citations=['https://www.qdl.qa/en/archive/81055/vdc_100048152712.0x00008e','https://etheses.whiterose.ac.uk/id/eprint/3257/']
  row=dict(value=q,label=r['label'],at=None,roleLabel=r['role'],rank='preferred',supplement=TAG,citation=citations,**{'from':a,'to':b})
  facts['entities'][r['country']]['fields']['ruler'].append(row);facts['labels'][q]=r['label'];review.append(dict(country=r['country'],**row))
 for q in {r['country']for r in ROWS}:
  facts['entities'][q]['rulerScopeNote']='按在位或任职年代列出具名统治者；交接年份可先后有多位。君主名单不等于对摄政、权臣、议会及实际军政控制者的完整描述。'
 write('public/data/polity-facts.json',facts)
 write('public/data/global-reigns-nov02-review.json',dict(reviewedAt='2026-11-02',appointments=review,people=len({r['value']for r in review}),polities=len({r['country']for r in review}),limitations=['并非所有时代所有国家均已补齐。','桑海1582—1588年多次交接尚未在本轮加入；不自动延长前任任期。','年表采用公历换算；史书即位年、改元年和正式登基日可能不同。']))
 print('Added appointments',len(review),'people',len({r['value']for r in review}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['fetch','apply']);args=p.parse_args();globals()[args.stage]()
