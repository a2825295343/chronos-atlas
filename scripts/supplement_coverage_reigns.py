"""Review exact named reigns; resolve real people, never fill with office titles."""
import argparse,json,time,urllib.parse,urllib.request,urllib.error
from collections import defaultdict
from pathlib import Path
from prepare_global_archive_review import ROOT,human,fetch
from enrich_polities import label
CACHE=ROOT/'.local/coverage-reigns';CACHE.mkdir(exist_ok=True)
TAG='coverage-named-reigns-2026-11-01'
# country key, source roster, dates approximate, person | Chinese | from | to
ROSTERS=[
 ('local:gujarat-sultanate','Gujarat_Sultanate',False,'''Mahmud Begada|马哈茂德·贝加达|1458|1511
Muzaffar Shah II|穆扎法尔沙二世|1511|1526
Bahadur Shah of Gujarat|巴哈杜尔沙|1526|1537
Mahmud Shah III|马哈茂德沙三世|1538|1554
Ahmad Shah III|艾哈迈德沙三世|1554|1561
Muzaffar Shah III|穆扎法尔沙三世|1561|1573'''),
 ('local:malwa-sultanate','Malwa_Sultanate',False,'''Dilawar Khan|迪拉瓦尔汗|1401|1405
Hoshang Shah|胡尚沙|1405|1435
Mahmud Khalji|马哈茂德·卡尔吉|1436|1469
Ghiyath Shah|吉亚斯沙|1469|1500
Nasir Shah|纳西尔沙|1500|1510
Mahmud Khalji II|马哈茂德·卡尔吉二世|1510|1531
Baz Bahadur|巴兹·巴哈杜尔|1555|1562'''),
 ('Q400998','Ahmadnagar_Sultanate',False,'''Ahmad Nizam Shah I|艾哈迈德·尼扎姆沙一世|1490|1510
Burhan Nizam Shah I|布尔汉·尼扎姆沙一世|1510|1553
Hussain Nizam Shah I|侯赛因·尼扎姆沙一世|1553|1565
Murtaza Nizam Shah I|穆尔塔扎·尼扎姆沙一世|1565|1588
Chand Bibi|钱德·比比（摄政）|1595|1599
Murtaza Nizam Shah III|穆尔塔扎·尼扎姆沙三世|1633|1636'''),
 ('Q83821','Adil_Shahi_dynasty',False,'''Yusuf Adil Shah|优素福·阿迪勒沙|1490|1510
Ismail Adil Shah|伊斯迈尔·阿迪勒沙|1510|1534
Ibrahim Adil Shah I|易卜拉欣·阿迪勒沙一世|1534|1558
Ali Adil Shah I|阿里·阿迪勒沙一世|1558|1579
Ibrahim Adil Shah II|易卜拉欣·阿迪勒沙二世|1580|1627
Mohammed Adil Shah|穆罕默德·阿迪勒沙|1627|1656
Ali Adil Shah II|阿里·阿迪勒沙二世|1656|1672
Sikandar Adil Shah|西坎达尔·阿迪勒沙|1672|1686'''),
 ('Q1148042','Qutb_Shahi_dynasty',False,'''Sultan Quli Qutb-ul-Mulk|苏丹库利·库特布穆尔克|1518|1543
Jamsheed Quli Qutb Shah|贾姆希德·库利·库特布沙|1543|1550
Subhan Quli Qutb Shah|苏布汉·库利·库特布沙|1550|1550
Ibrahim Quli Qutb Shah Wali|易卜拉欣·库利·库特布沙|1550|1580
Muhammad Quli Qutb Shah|穆罕默德·库利·库特布沙|1580|1612
Sultan Muhammad Qutb Shah|苏丹·穆罕默德·库特布沙|1612|1626
Abdullah Qutb Shah|阿卜杜拉·库特布沙|1626|1672
Abul Hasan Qutb Shah|阿布尔·哈桑·库特布沙|1672|1687'''),
 ('Q33296','List_of_Mughal_emperors',False,'''Babur|巴布尔|1526|1530
Humayun|胡马雍|1530|1540
Humayun|胡马雍|1555|1556
Akbar|阿克巴|1556|1605
Jahangir|贾汉吉尔|1605|1627
Shah Jahan|沙贾汗|1628|1658
Aurangzeb|奥朗则布|1658|1707
Bahadur Shah I|巴哈杜尔沙一世|1707|1712
Jahandar Shah|贾汉达尔沙|1712|1713
Farrukhsiyar|法鲁克锡亚尔|1713|1719
Rafi ud-Darajat|拉菲·乌德·达拉贾特|1719|1719
Shah Jahan II|沙贾汗二世|1719|1719
Muhammad Shah|穆罕默德沙|1719|1748
Ahmad Shah Bahadur|艾哈迈德沙·巴哈杜尔|1748|1754
Alamgir II|阿拉姆吉尔二世|1754|1759
Shah Alam II|沙阿拉姆二世|1759|1806
Akbar II|阿克巴二世|1806|1837
Bahadur Shah II|巴哈杜尔沙二世|1837|1857'''),
 ('Q266923','Kingdom_of_Mysore',False,'''Raja Wodeyar I|罗阇·沃德亚尔一世|1578|1617
Chamaraja Wodeyar VI|查马拉阇·沃德亚尔六世|1617|1637
Kanthirava Narasaraja I|坎提拉瓦·纳拉萨罗阇一世|1638|1659
Dodda Devaraja|多达·德瓦罗阇|1659|1673
Chikka Devaraja|奇卡·德瓦罗阇|1673|1704
Krishnaraja Wodeyar I|克里希纳罗阇·沃德亚尔一世|1714|1732
Krishnaraja Wodeyar II|克里希纳罗阇·沃德亚尔二世|1734|1766
Hyder Ali|海德尔·阿里（实际执政者）|1761|1782
Tipu Sultan|蒂普苏丹|1782|1799
Krishnaraja Wodeyar III|克里希纳罗阇·沃德亚尔三世|1799|1868
Chamarajendra Wadiyar X|查马拉金德拉·沃德亚尔十世|1868|1894
Krishnaraja Wadiyar IV|克里希纳罗阇·沃德亚尔四世|1894|1940
Jayachamarajendra Wadiyar|贾亚查马拉金德拉·沃德亚尔|1940|1950'''),
 ('Q146871','Emirate_of_Diriyah',False,'''Muhammad bin Saud|穆罕默德·本·沙特|1744|1765
Abdulaziz bin Muhammad Al Saud|阿卜杜勒阿齐兹·本·穆罕默德|1765|1803
Saud bin Abdulaziz Al Saud|沙特·本·阿卜杜勒阿齐兹|1803|1814
Abdullah bin Saud Al Saud|阿卜杜拉·本·沙特|1814|1818'''),
 ('Q146862','Emirate_of_Nejd',False,'''Turki bin Abdullah Al Saud|图尔基·本·阿卜杜拉|1824|1834
Faisal bin Turki Al Saud|费萨尔·本·图尔基|1834|1838
Faisal bin Turki Al Saud|费萨尔·本·图尔基|1843|1865
Khalid bin Saud Al Saud|哈立德·本·沙特|1838|1841
Abdullah bin Thunayan Al Saud|阿卜杜拉·本·苏奈延|1841|1843
Abdullah bin Faisal Al Saud|阿卜杜拉·本·费萨尔|1865|1871
Abdullah bin Faisal Al Saud|阿卜杜拉·本·费萨尔|1876|1889
Saud bin Faisal Al Saud|沙特·本·费萨尔|1871|1875
Abdul Rahman bin Faisal Al Saud|阿卜杜勒拉赫曼·本·费萨尔|1889|1891'''),
 ('local:jabal-shammar','Emirate_of_Jabal_Shammar',False,'''Abdullah bin Ali Al Rashid|阿卜杜拉·本·阿里·拉希德|1836|1848
Talal bin Abdullah Al Rashid|塔拉勒·本·阿卜杜拉|1848|1868
Muhammad bin Abdullah Al Rashid|穆罕默德·本·阿卜杜拉·拉希德|1869|1897
Abdulaziz bin Mutaib Al Rashid|阿卜杜勒阿齐兹·本·穆塔伊卜|1897|1906
Saud bin Abdulaziz Al Rashid|沙特·本·阿卜杜勒阿齐兹·拉希德|1908|1920
Abdullah bin Mutaib Al Rashid|阿卜杜拉·本·穆塔伊卜|1920|1921
Muhammad bin Talal Al Rashid|穆罕默德·本·塔拉勒|1921|1921'''),
 ('local:yaruba-oman','Yaruba_dynasty',False,'''Nasir bin Murshid|纳西尔·本·穆尔希德|1624|1649
Sultan bin Saif|苏丹·本·赛义夫|1649|1679
Bil'arab bin Sultan|比拉拉卜·本·苏丹|1679|1692
Saif bin Sultan|赛义夫·本·苏丹|1692|1711
Sultan bin Saif II|苏丹·本·赛义夫二世|1711|1718'''),
 ('local:albusaidi-oman','List_of_rulers_of_Oman',False,'''Ahmad bin Said|艾哈迈德·本·赛义德|1749|1783
Said bin Ahmad|赛义德·本·艾哈迈德|1783|1786
Hamad bin Said|哈马德·本·赛义德|1786|1792
Sultan bin Ahmad|苏丹·本·艾哈迈德|1792|1804
Said bin Sultan|赛义德·本·苏丹|1804|1856
Thuwaini bin Said|苏韦尼·本·赛义德|1856|1866
Salim bin Thuwaini|萨利姆·本·苏韦尼|1866|1868
Azzan bin Qais|阿赞·本·盖斯|1868|1871
Turki bin Said|图尔基·本·赛义德|1871|1888
Faisal bin Turki, Sultan of Muscat and Oman|费萨尔·本·图尔基|1888|1913'''),
 ('Q2088141','Caucasian_Imamate',False,'''Ghazi Muhammad|加齐·穆罕默德|1829|1832
Hamzat Bek|哈姆扎特·贝克|1832|1834
Imam Shamil|伊玛目沙米尔|1834|1859'''),
 ('local:company-india','Governor-General_of_India',False,'''Warren Hastings|沃伦·黑斯廷斯（总督）|1773|1785
Charles Cornwallis, 1st Marquess Cornwallis|查尔斯·康沃利斯（总督）|1786|1793
Richard Wellesley, 1st Marquess Wellesley|理查德·韦尔斯利（总督）|1798|1805
Francis Rawdon-Hastings, 1st Marquess of Hastings|黑斯廷斯侯爵（总督）|1813|1823
Lord William Bentinck|威廉·本廷克（总督）|1828|1835
James Broun-Ramsay, 1st Marquess of Dalhousie|达尔豪西侯爵（总督）|1848|1856
Charles Canning, 1st Earl Canning|查尔斯·坎宁（总督）|1856|1858'''),
 ('local:awadh-rebel-government','Indian_Rebellion_of_1857',False,'''Begum Hazrat Mahal|贝古姆·哈兹拉特·玛哈尔（摄政与抵抗领袖）|1857|1858
Birjis Qadr|比尔吉斯·卡德尔|1857|1858'''),
 ('Q389688','List_of_Achaemenid_emperors',True,'''Cyrus the Great|居鲁士二世| -550|-530
Cambyses II|冈比西斯二世|-530|-522
Darius the Great|大流士一世|-522|-486
Xerxes I|薛西斯一世|-486|-465
Artaxerxes I|阿尔塔薛西斯一世|-465|-424
Darius II|大流士二世|-423|-404
Artaxerxes II|阿尔塔薛西斯二世|-404|-358
Artaxerxes III|阿尔塔薛西斯三世|-358|-338
Arses|阿尔塞斯|-338|-336
Darius III|大流士三世|-336|-330'''),
 ('Q2320005','Ptolemaic_dynasty',True,'''Ptolemy I Soter|托勒密一世|-305|-282
Ptolemy II Philadelphus|托勒密二世|-283|-246
Ptolemy III Euergetes|托勒密三世|-246|-222
Ptolemy IV Philopator|托勒密四世|-222|-204
Ptolemy V Epiphanes|托勒密五世|-204|-180
Ptolemy VI Philometor|托勒密六世|-180|-145
Ptolemy VIII Physcon|托勒密八世|-170|-163
Ptolemy VIII Physcon|托勒密八世|-145|-116
Ptolemy IX Soter|托勒密九世|-116|-107
Ptolemy IX Soter|托勒密九世|-88|-81
Ptolemy X Alexander I|托勒密十世|-107|-88
Ptolemy XII Auletes|托勒密十二世|-80|-58
Ptolemy XII Auletes|托勒密十二世|-55|-51
Cleopatra|克娄巴特拉七世|-51|-30
Ptolemy XIII Theos Philopator|托勒密十三世|-51|-47
Ptolemy XIV Philopator|托勒密十四世|-47|-44
Caesarion|托勒密十五世（凯撒里昂）|-44|-30'''),
 ('Q177819','List_of_pharaohs',True,'''Djoser|左塞尔|-2686|-2648
Sneferu|斯尼夫鲁|-2613|-2589
Khufu|胡夫|-2589|-2566
Djedefre|拉杰德夫|-2566|-2558
Khafre|哈夫拉|-2558|-2532
Menkaure|门卡乌拉|-2532|-2503
Userkaf|乌塞尔卡夫|-2494|-2487
Sahure|萨胡拉|-2487|-2475
Unas|乌纳斯|-2375|-2345
Teti|特提|-2345|-2333
Pepi I Meryre|佩皮一世|-2332|-2283
Pepi II Neferkare|佩皮二世|-2278|-2184'''),
 ('Q180568','List_of_pharaohs',True,'''Ahmose I|雅赫摩斯一世|-1550|-1525
Amenhotep I|阿蒙霍特普一世|-1525|-1504
Thutmose I|图特摩斯一世|-1504|-1492
Thutmose II|图特摩斯二世|-1492|-1479
Hatshepsut|哈特谢普苏特|-1479|-1458
Thutmose III|图特摩斯三世|-1479|-1425
Amenhotep II|阿蒙霍特普二世|-1427|-1401
Thutmose IV|图特摩斯四世|-1401|-1391
Amenhotep III|阿蒙霍特普三世|-1391|-1353
Akhenaten|阿肯那顿|-1353|-1336
Tutankhamun|图坦卡蒙|-1332|-1323
Ay|阿伊|-1323|-1319
Horemheb|霍伦海布|-1319|-1292
Ramesses I|拉美西斯一世|-1292|-1290
Seti I|塞提一世|-1290|-1279
Ramesses II|拉美西斯二世|-1279|-1213
Merneptah|麦伦普塔|-1213|-1203
Ramesses III|拉美西斯三世|-1186|-1155
Ramesses XI|拉美西斯十一世|-1107|-1077'''),
 ('Q12490507','Rashidun_Caliphate',False,'''Abu Bakr|阿布·伯克尔|632|634
Umar|欧麦尔·本·哈塔卜|634|644
Uthman|奥斯曼·本·阿凡|644|656
Ali|阿里·本·阿比·塔利卜|656|661
Hasan ibn Ali|哈桑·本·阿里|661|661'''),
 ('Q8575586','Umayyad_Caliphate',False,'''Mu'awiya I|穆阿维叶一世|661|680
Yazid I|叶齐德一世|680|683
Mu'awiya II|穆阿维叶二世|683|684
Marwan I|马尔万一世|684|685
Abd al-Malik ibn Marwan|阿卜杜勒马利克|685|705
Al-Walid I|瓦利德一世|705|715
Sulayman ibn Abd al-Malik|苏莱曼|715|717
Umar II|欧麦尔二世|717|720
Yazid II|叶齐德二世|720|724
Hisham ibn Abd al-Malik|希沙姆|724|743
Al-Walid II|瓦利德二世|743|744
Yazid III|叶齐德三世|744|744
Ibrahim ibn al-Walid|易卜拉欣|744|744
Marwan II|马尔万二世|744|750'''),
 ('Q12536','Abbasid_Caliphate',False,'''As-Saffah|萨法赫|750|754
Al-Mansur|曼苏尔|754|775
Al-Mahdi|马赫迪|775|785
Al-Hadi|哈迪|785|786
Harun al-Rashid|哈伦·拉希德|786|809
Al-Amin|阿明|809|813
Al-Ma'mun|马蒙|813|833
Al-Mu'tasim|穆塔西姆|833|842
Al-Wathiq|瓦西格|842|847
Al-Mutawakkil|穆塔瓦基勒|847|861
Al-Muqtadir|穆克塔迪尔|908|932
Al-Nasir|纳赛尔|1180|1225
Al-Mustansir (Abbasid caliph in Baghdad)|穆斯坦绥尔|1226|1242
Al-Musta'sim|穆斯塔绥木|1242|1258'''),
]

ROSTERS.extend([
 ('Q4461035','Akkadian_Empire',True,'''Sargon of Akkad|阿卡德的萨尔贡|-2334|-2279
Rimush|里穆什|-2278|-2270
Manishtushu|玛尼什图苏|-2269|-2255
Naram-Sin of Akkad|纳拉姆辛|-2254|-2218
Shar-Kali-Sharri|沙尔卡利沙里|-2217|-2193
Shu-turul|舒图鲁尔|-2168|-2154'''),
 ('Q624887','Neo-Babylonian_Empire',True,'''Nabopolassar|那波帕拉萨尔|-626|-605
Nebuchadnezzar II|尼布甲尼撒二世|-605|-562
Amel-Marduk|阿梅尔马尔杜克|-562|-560
Neriglissar|涅里格利萨尔|-560|-556
Labashi-Marduk|拉巴施马尔杜克|-556|-556
Nabonidus|那波尼德|-556|-539'''),
 ('Q207521','List_of_emperors_of_Ethiopia',True,'''Yekuno Amlak|耶库诺·阿姆拉克|1270|1285
Yagbe'u Seyon|耶格贝乌·塞永|1285|1294
Amda Seyon I|阿姆达·塞永一世|1314|1344
Zara Yaqob|扎拉·雅各布|1434|1468
Eskender|伊斯坎德尔|1478|1494
Dawit II|达维特二世（莱布纳·登格尔）|1508|1540
Gelawdewos|格拉乌德沃斯|1540|1559
Susenyos I|苏塞尼约斯一世|1606|1632
Fasilides|法西利德斯|1632|1667
Iyasu I|伊亚苏一世|1682|1706
Tewodros II|特沃德罗斯二世|1855|1868
Yohannes IV|约翰尼斯四世|1872|1889
Menelik II|孟尼利克二世|1889|1913'''),
 ('Q139377','Kingdom_of_Aksum',True,'''Ezana|埃扎纳|320|360
Kaleb of Axum|卡莱布|510|540'''),
])

def rows():
 for country,source,approx,text in ROSTERS:
  for line in text.splitlines():
   title,cn,a,b=map(str.strip,line.split('|'));yield{'country':country,'source':source,'approximate':approx,'title':title,'label':cn,'from':int(a),'to':int(b)}
def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['fetch','resolve','apply']);args=p.parse_args();candidates=list(rows());idsfile=CACHE/'title-ids.json';ids=json.loads(idsfile.read_bytes())if idsfile.exists()else{}
 peoplefile=CACHE/'people.json';people=json.loads(peoplefile.read_bytes())if peoplefile.exists()else{}
 if args.stage=='resolve':
  missing=sorted({r['title']for r in candidates}-ids.keys())
  for i in range(0,len(missing),35):
   group=missing[i:i+35];params=urllib.parse.urlencode({'action':'query','format':'json','redirects':1,'prop':'pageprops','ppprop':'wikibase_item','titles':'|'.join(group)})
   req=urllib.request.Request('https://en.wikipedia.org/w/api.php?'+params,headers={'User-Agent':'GuanlanAtlas/1.7 educational historical research'})
   try:
    with urllib.request.urlopen(req,timeout=45)as response:d=json.load(response)['query']
   except urllib.error.HTTPError as e:
    if e.code!=429:raise
    print('Name resolver rate limited; verified subset retained.',flush=True);break
   redirect={r['from']:r['to']for r in d.get('normalized',[])+d.get('redirects',[])};pages={r['title']:r.get('pageprops',{}).get('wikibase_item')for r in d['pages'].values()}
   for title in group:
    n=title
    for _ in range(6):n=redirect.get(n,n)
    if pages.get(n):ids[title]=pages[n]
   idsfile.write_text(json.dumps(ids,ensure_ascii=False),encoding='utf8');time.sleep(3)
  fetch({ids[r['title']]for r in candidates if r['title']in ids},people,'coverage-ruler-people');peoplefile.write_text(json.dumps(people,ensure_ascii=False),encoding='utf8');return
 if args.stage=='fetch':
  pool=json.loads((ROOT/'.local/global-archive-review/entities.json').read_bytes())
  for extra in ['.local/ancient-roster-review/verified-people.json','.local/reviewed-reigns/verified-people.json']:
   if(ROOT/extra).exists():pool.update(json.loads((ROOT/extra).read_bytes()))
  byname=defaultdict(list)
  for q,e in pool.items():
   if human(e):byname[e.get('labels',{}).get('en',{}).get('value')].append(q)
  for r in candidates:
   if len(byname[r['title']])==1:ids[r['title']]=byname[r['title']][0];people[ids[r['title']]]=pool[ids[r['title']]]
  missing=sorted({r['title']for r in candidates}-ids.keys())
  for i in range(0,len(missing),35):
   group=missing[i:i+35];params=urllib.parse.urlencode({'action':'wbgetentities','format':'json','sites':'enwiki','titles':'|'.join(group),'props':'labels|claims|sitelinks','languages':'zh-hans|zh|en','redirects':'yes'})
   req=urllib.request.Request('https://www.wikidata.org/w/api.php?'+params,headers={'User-Agent':'GuanlanAtlas/1.7 educational historical research'})
   with urllib.request.urlopen(req,timeout=45)as response:data=json.load(response)
   for q,e in data.get('entities',{}).items():
    if not human(e):continue
    people[q]=e;title=e.get('sitelinks',{}).get('enwiki',{}).get('title');en=e.get('labels',{}).get('en',{}).get('value')
    for n in [title,en]:
     if n:ids[n]=q
   idsfile.write_text(json.dumps(ids,ensure_ascii=False),encoding='utf8');peoplefile.write_text(json.dumps(people,ensure_ascii=False),encoding='utf8');print('Named ruler identities',min(i+35,len(missing)),'/',len(missing),flush=True);time.sleep(3)
  idsfile.write_text(json.dumps(ids,ensure_ascii=False),encoding='utf8');peoplefile.write_text(json.dumps(people,ensure_ascii=False),encoding='utf8');return
 facts=json.loads((ROOT/'public/data/polity-facts.json').read_bytes());added=[];missing=[]
 for e in facts['entities'].values():e['fields']['ruler']=[r for r in e['fields'].get('ruler',[])if r.get('supplement')!=TAG]
 for c in candidates:
  q=ids.get(c['title']);country=c['country']
  if not q or not human(people.get(q,{})):missing.append(c['title']);continue
  if country not in facts['entities']:continue
  role='具名君主／统治者'
  if '总督'in c['label']:role='公司领地总督／行政首长，不是英国君主'
  elif '实际执政'in c['label']:role='实际执政者，与名义王室分列'
  elif '摄政'in c['label']:role='摄政／政治与抵抗领袖'
  row={'value':q,'label':c['label'],'from':c['from'],'to':c['to'],'at':None,'roleLabel':role,'citation':['https://en.wikipedia.org/wiki/'+c['source'],'https://www.wikidata.org/wiki/'+q],'dateSource':'reviewed named reign chronology','derived':True,'approximate':c['approximate'],'inference':'采用具名在位年表，交接年可并列。古代纪年与共治存在不同说法；没有把出生或去世年份直接当作执政任期。','supplement':TAG}
  facts['entities'][country]['fields'].setdefault('ruler',[]).append(row);facts['labels'][q]=row['label'];added.append({'country':country,**row})
 (ROOT/'public/data/polity-facts.json').write_text(json.dumps(facts,ensure_ascii=False,separators=(',',':')),encoding='utf8');(CACHE/'verified-people.json').write_text(json.dumps({r['value']:people[r['value']]for r in added},ensure_ascii=False),encoding='utf8')
 report={'reviewedAt':'2026-11-01','records':added,'unresolved':sorted(set(missing)),'summary':{'records':len(added),'people':len({r['value']for r in added}),'countries':len({r['country']for r in added})}}
 (ROOT/'public/data/coverage-reigns-review.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8');print(report['summary'],'unresolved',report['unresolved'],flush=True)
if __name__=='__main__':main()
