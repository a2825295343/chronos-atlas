"""Exact human identities and bounded appointments across four continents.

Each roster is an explicit reign chronology. Never infer office from lifespan.
"""
import argparse,copy,hashlib,json,subprocess,urllib.parse
from territory_repair_stage import ROOT,read,write
from prepare_global_archive_review import human
from enrich_polities import simplify
TAG='world-rosters-2026-11-02';CACHE=ROOT/'.local/world-rosters';CACHE.mkdir(exist_ok=True)
ROWS=[]
def roster(q,page,role,text):
 for line in text.strip().splitlines():
  title,zh,a,b=line.strip().split('|');ROWS.append(dict(country=q,title=title,label=zh,start=int(a),end=int(b),source='https://en.wikipedia.org/wiki/'+page,role=role))

roster('Q179876','List_of_English_monarchs','英格兰国王；年内交接可并列', '''
Æthelstan|埃塞尔斯坦|927|939
Edmund I|埃德蒙一世|939|946
Eadred|埃德雷德|946|955
Eadwig|埃德威格|955|959
Edgar, King of England|埃德加|959|975
Edward the Martyr|殉教者爱德华|975|978
Æthelred the Unready|埃塞尔雷德二世|978|1013
Sweyn Forkbeard|斯温一世|1013|1014
Æthelred the Unready|埃塞尔雷德二世|1014|1016
Edmund Ironside|埃德蒙二世|1016|1016
Cnut|克努特|1016|1035
Harold Harefoot|哈罗德一世|1035|1040
Harthacnut|哈德克努特|1040|1042
Edward the Confessor|忏悔者爱德华|1042|1066
Harold Godwinson|哈罗德二世|1066|1066
William the Conqueror|威廉一世|1066|1087
William II of England|威廉二世|1087|1100
Henry I of England|亨利一世|1100|1135
Stephen, King of England|斯蒂芬|1135|1154
Henry II of England|亨利二世|1154|1189
Richard I of England|理查一世|1189|1199
John, King of England|约翰|1199|1216
Henry III of England|亨利三世|1216|1272
Edward I of England|爱德华一世|1272|1307
Edward II of England|爱德华二世|1307|1327
Edward III of England|爱德华三世|1327|1377
Richard II of England|理查二世|1377|1399
Henry IV of England|亨利四世|1399|1413
''')
roster('Q70972','List_of_French_monarchs','法兰西国王；早期常用法兰克人之王称号', '''
Hugh Capet|于格·卡佩|987|996
Robert II of France|罗贝尔二世|996|1031
Henry I of France|亨利一世|1031|1060
Philip I of France|腓力一世|1060|1108
Louis VI of France|路易六世|1108|1137
Louis VII of France|路易七世|1137|1180
Philip II of France|腓力二世|1180|1223
Louis VIII of France|路易八世|1223|1226
Louis IX of France|路易九世|1226|1270
Philip III of France|腓力三世|1270|1285
Philip IV of France|腓力四世|1285|1314
Louis X of France|路易十世|1314|1316
John I of France|约翰一世|1316|1316
Philip V of France|腓力五世|1316|1322
Charles IV of France|查理四世|1322|1328
''')
roster('Q45670','List_of_Portuguese_monarchs','葡萄牙君主；伊比利亚共主时期仍为独立王冠', '''
Afonso I of Portugal|阿方索一世|1139|1185
Sancho I of Portugal|桑乔一世|1185|1211
Afonso II of Portugal|阿方索二世|1211|1223
Sancho II of Portugal|桑乔二世|1223|1248
Afonso III of Portugal|阿方索三世|1248|1279
Denis of Portugal|迪尼斯一世|1279|1325
Afonso IV of Portugal|阿方索四世|1325|1357
Peter I of Portugal|佩德罗一世|1357|1367
Ferdinand I of Portugal|费尔南多一世|1367|1383
John I of Portugal|若昂一世|1385|1433
Edward, King of Portugal|杜阿尔特一世|1433|1438
Afonso V of Portugal|阿方索五世|1438|1481
John II of Portugal|若昂二世|1481|1495
John II of Portugal|若昂二世（前任短暂退位期间）|1477|1477
Manuel I of Portugal|曼努埃尔一世|1495|1521
John III of Portugal|若昂三世|1521|1557
Sebastian of Portugal|塞巴斯蒂昂一世|1557|1578
Henry, King of Portugal|恩里克一世|1578|1580
António, Prior of Crato|安东尼奥（争位者，控制范围有限）|1580|1580
Philip II of Spain|腓力一世（葡萄牙王号）|1580|1598
Philip III of Spain|腓力二世（葡萄牙王号）|1598|1621
Philip IV of Spain|腓力三世（葡萄牙王号）|1621|1640
John IV of Portugal|若昂四世|1640|1656
Afonso VI of Portugal|阿方索六世|1656|1683
Peter II of Portugal|佩德罗二世|1683|1706
John V of Portugal|若昂五世|1706|1750
Joseph I of Portugal|若泽一世|1750|1777
Maria I of Portugal|玛丽亚一世|1777|1816
Peter III of Portugal|佩德罗三世（配偶共治君主）|1777|1786
John VI of Portugal|若昂六世|1816|1826
Pedro I of Brazil|佩德罗四世（葡萄牙王号）|1826|1826
Maria II of Portugal|玛丽亚二世|1826|1828
Miguel I of Portugal|米格尔一世|1828|1834
Maria II of Portugal|玛丽亚二世|1834|1853
Ferdinand II of Portugal|费尔南多二世（配偶共治君主）|1837|1853
Pedro V of Portugal|佩德罗五世|1853|1861
Luís I of Portugal|路易斯一世|1861|1889
Carlos I of Portugal|卡洛斯一世|1889|1908
Manuel II of Portugal|曼努埃尔二世|1908|1910
''')
roster('Q1062422','Konbaung_dynasty','缅甸国王（贡榜王室）', '''
Alaungpaya|雍籍牙|1752|1760
Naungdawgyi|囊陀基|1760|1763
Hsinbyushin|辛骠信|1763|1776
Singu Min|新古王|1776|1782
Phaungkaza Maung Maung|孟孟|1782|1782
Bodawpaya|波道帕耶|1782|1819
Bagyidaw|巴基道|1819|1837
Tharrawaddy Min|沙耶瓦底王|1837|1846
Pagan Min|蒲甘王|1846|1853
Mindon Min|敏东王|1853|1878
Thibaw Min|锡袍王|1878|1885
''')
roster('Q878309','L%C3%BD_dynasty','大越皇帝（李氏）', '''
Lý Thái Tổ|李太祖李公蕴|1009|1028
Lý Thái Tông|李太宗李佛玛|1028|1054
Lý Thánh Tông|李圣宗李日尊|1054|1072
Lý Nhân Tông|李仁宗李乾德|1072|1127
Lý Thần Tông|李神宗李阳焕|1127|1138
Lý Anh Tông|李英宗李天祚|1138|1175
Lý Cao Tông|李高宗李龙翰|1175|1210
Lý Huệ Tông|李惠宗李旵|1210|1224
Lý Chiêu Hoàng|李昭皇李佛金|1224|1225
''')
roster('Q3111454','Tr%E1%BA%A7n_dynasty','大越皇帝（陈氏）；退位后上皇仍可能掌权', '''
Trần Thái Tông|陈太宗陈煚|1225|1258
Trần Thánh Tông|陈圣宗陈晃|1258|1278
Trần Nhân Tông|陈仁宗陈昑|1278|1293
Trần Anh Tông|陈英宗陈烇|1293|1314
Trần Minh Tông|陈明宗陈奣|1314|1329
Trần Hiến Tông|陈宪宗陈旺|1329|1341
Trần Dụ Tông|陈裕宗陈暭|1341|1369
Dương Nhật Lễ|杨日礼|1369|1370
Trần Nghệ Tông|陈艺宗陈暊|1370|1372
Trần Duệ Tông|陈睿宗陈曔|1372|1377
Trần Phế Đế|陈废帝陈晛|1377|1388
Trần Thuận Tông|陈顺宗陈颙|1388|1398
Trần Thiếu Đế|陈少帝陈𩖃|1398|1400
''')
roster('Q6500483','Nguy%E1%BB%85n_dynasty','越南／大南皇帝；1883年后法国保护下王权受限', '''
Gia Long|嘉隆帝阮福映|1802|1820
Minh Mạng|明命帝阮福晈|1820|1841
Thiệu Trị|绍治帝阮福暶|1841|1847
Tự Đức|嗣德帝阮福时|1847|1883
Dục Đức|育德帝阮福膺禛|1883|1883
Hiệp Hòa|协和帝阮福洪佚|1883|1883
Kiến Phúc|建福帝阮福膺登|1883|1884
Hàm Nghi|咸宜帝阮福膺𧰡|1884|1885
Đồng Khánh|同庆帝阮福膺禟|1885|1889
Thành Thái|成泰帝阮福宝嶙|1889|1907
Duy Tân|维新帝阮福晃|1907|1916
Khải Định|启定帝阮福宝嶹|1916|1925
Bảo Đại|保大帝阮福晪|1926|1945
''')
roster('Q722071','List_of_rulers_of_Asante','阿散蒂赫内；不是全部西非地区的统治者', '''
Osei Kofi Tutu I|奥塞·图图一世|1701|1717
Opoku Ware I|奥波库·瓦雷一世|1720|1750
Kusi Obodom|库西·奥博杜姆|1750|1764
Osei Kwadwo|奥塞·夸德沃|1764|1777
Osei Kwame Panyin|奥塞·夸梅|1777|1803
Opoku Fofie|奥波库·福菲|1803|1804
Osei Tutu Kwame|奥塞·邦苏|1804|1824
Osei Yaw Akoto|奥塞·亚乌·阿科托|1824|1834
Kwaku Dua I|夸库·杜阿一世|1834|1867
Kofi Karikari|科菲·卡里卡里|1867|1874
Mensa Bonsu|门萨·邦苏|1874|1883
Kwaku Dua II|夸库·杜阿二世|1884|1884
Prempeh I|普雷姆佩一世|1888|1896
''')
roster('Q207521','List_of_emperors_of_Ethiopia','埃塞俄比亚皇帝；不将地方诸王自动等同中央实控', '''
Fasilides|法西利德斯|1632|1667
Yohannes I|约翰内斯一世|1667|1682
Iyasu I|伊亚苏一世|1682|1706
Tekle Haymanot I|特克勒·海马诺特一世|1706|1708
Tewoflos|特沃夫洛斯|1708|1711
Yostos|约斯托斯|1711|1716
Dawit III|达维特三世|1716|1721
Bakaffa|巴卡法|1721|1730
Iyasu II|伊亚苏二世|1730|1755
Iyoas I|伊约阿斯一世|1755|1769
Tewodros II|特沃德罗斯二世|1855|1868
Tekle Giyorgis II|特克勒·吉约吉斯二世|1868|1871
Yohannes IV|约翰内斯四世|1872|1889
Menelik II|孟尼利克二世|1889|1913
Lij Iyasu|伊亚苏五世（未加冕的指定继承人及实际执政者）|1913|1916
Zewditu|佐迪图女皇|1916|1930
Haile Selassie|海尔·塞拉西一世|1930|1936
Haile Selassie|海尔·塞拉西一世（流亡）|1936|1941
Haile Selassie|海尔·塞拉西一世|1941|1974
''')
roster('Q1028','Alaouite_dynasty','摩洛哥苏丹（阿拉维王室）；内战时期控制分裂', '''
Al-Rashid of Morocco|拉希德|1666|1672
Ismail Ibn Sharif|穆莱·伊斯迈尔|1672|1727
Mohammed ben Abdallah|穆罕默德三世|1757|1790
Yazid of Morocco|耶齐德|1790|1792
Slimane of Morocco|苏莱曼|1792|1822
Abd al-Rahman of Morocco|阿卜杜拉赫曼|1822|1859
Mohammed IV of Morocco|穆罕默德四世|1859|1873
Hassan I of Morocco|哈桑一世|1873|1894
Abdelaziz of Morocco|阿卜杜勒-阿齐兹|1894|1908
Abd al-Hafid of Morocco|阿卜杜勒-哈菲兹|1908|1912
''')
roster('Q217230','Empire_of_Brazil','巴西皇帝', '''
Pedro I of Brazil|佩德罗一世|1822|1831
Pedro II of Brazil|佩德罗二世|1831|1889
''')
roster('Q155','List_of_presidents_of_Brazil','巴西共和国总统；不把军政交接视为君主继承', '''
Deodoro da Fonseca|德奥多罗·达·丰塞卡|1889|1891
Floriano Peixoto|弗洛里亚诺·佩肖托|1891|1894
Prudente de Morais|普鲁登特·德·莫赖斯|1894|1898
Campos Sales|坎波斯·萨莱斯|1898|1902
Rodrigues Alves|罗德里格斯·阿尔维斯|1902|1906
Afonso Pena|阿方索·佩纳|1906|1909
Nilo Peçanha|尼洛·佩萨尼亚|1909|1910
Hermes da Fonseca|埃尔梅斯·达·丰塞卡|1910|1914
Venceslau Brás|文塞斯劳·布拉斯|1914|1918
Delfim Moreira|德尔芬·莫雷拉|1918|1919
Epitácio Pessoa|埃皮塔西奥·佩索阿|1919|1922
Artur Bernardes|阿图尔·贝尔纳德斯|1922|1926
Washington Luís|华盛顿·路易斯|1926|1930
''')
roster('Q298','List_of_presidents_of_Chile','智利总统', '''
José Joaquín Prieto|何塞·华金·普列托|1831|1841
Manuel Bulnes|曼努埃尔·布尔内斯|1841|1851
Manuel Montt|曼努埃尔·蒙特|1851|1861
José Joaquín Pérez|何塞·华金·佩雷斯|1861|1871
Federico Errázuriz Zañartu|费德里科·埃拉苏里斯·萨尼亚尔图|1871|1876
Aníbal Pinto|阿尼瓦尔·平托|1876|1881
Domingo Santa María|多明戈·圣玛丽亚|1881|1886
José Manuel Balmaceda|何塞·曼努埃尔·巴尔马塞达|1886|1891
Jorge Montt|豪尔赫·蒙特|1891|1896
Federico Errázuriz Echaurren|费德里科·埃拉苏里斯·埃绍伦|1896|1901
Germán Riesco|赫尔曼·里斯科|1901|1906
Pedro Montt|佩德罗·蒙特|1906|1910
Ramón Barros Luco|拉蒙·巴罗斯·卢科|1910|1915
Juan Luis Sanfuentes|胡安·路易斯·圣富恩特斯|1915|1920
''')
roster('Q414','List_of_presidents_of_Argentina','阿根廷共和国总统', '''
Bartolomé Mitre|巴托洛梅·米特雷|1862|1868
Domingo Faustino Sarmiento|多明戈·福斯蒂诺·萨米恩托|1868|1874
Nicolás Avellaneda|尼古拉斯·阿韦利亚内达|1874|1880
Julio Argentino Roca|胡利奥·阿根蒂诺·罗卡|1880|1886
Miguel Juárez Celman|米格尔·胡亚雷斯·塞尔曼|1886|1890
Carlos Pellegrini|卡洛斯·佩莱格里尼|1890|1892
Luis Sáenz Peña|路易斯·萨恩斯·佩尼亚|1892|1895
José Evaristo Uriburu|何塞·埃瓦里斯托·乌里武鲁|1895|1898
Julio Argentino Roca|胡利奥·阿根蒂诺·罗卡|1898|1904
Manuel Quintana|曼努埃尔·金塔纳|1904|1906
José Figueroa Alcorta|何塞·菲格罗亚·阿尔科塔|1906|1910
Roque Sáenz Peña|罗克·萨恩斯·佩尼亚|1910|1914
Victorino de la Plaza|维克托里诺·德拉普拉萨|1914|1916
''')

ALIASES={'Osei Tutu Kwame':'Osei Bonsu'}

def fetch():
 pool=read('.local/world-rosters/verified-people.json')if(CACHE/'verified-people.json').exists()else{}
 for p in (ROOT/'.local').glob('*/verified*.json'):
  for q,e in json.loads(p.read_bytes()).items():
   if isinstance(e,dict)and human(e):pool.setdefault(q,e)
 def titles(e):return [e.get('labels',{}).get('en',{}).get('value'),e.get('sitelinks',{}).get('enwiki',{}).get('title')]
 have={s for e in pool.values()for s in titles(e)}
 if(CACHE/'resolved-titles.json').exists():have.update(t for t,q in read('.local/world-rosters/resolved-titles.json').items()if q in pool)
 names=sorted({ALIASES.get(r['title'],r['title'])for r in ROWS}-have)
 for i in range(0,len(names),25):
  params=urllib.parse.urlencode(dict(action='wbgetentities',format='json',sites='enwiki',titles='|'.join(names[i:i+25]),props='labels|claims|sitelinks',languages='zh-hans|zh|en',redirects='yes'));p=CACHE/(hashlib.sha1(params.encode()).hexdigest()+'.json')
  if not p.exists():subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','--max-time','45','--retry','1','https://www.wikidata.org/w/api.php?'+params,'--output',str(p)],check=True)
  pool.update({q:e for q,e in json.loads(p.read_bytes())['entities'].items()if human(e)})
  print('Resolved human batch',min(i+25,len(names)),'/',len(names),flush=True)
 have={s for e in pool.values()for s in titles(e)}
 unresolved=sorted({ALIASES.get(r['title'],r['title'])for r in ROWS}-have)
 resolved=read('.local/world-rosters/resolved-titles.json')if(CACHE/'resolved-titles.json').exists()else{}
 if unresolved:
  params=urllib.parse.urlencode(dict(action='query',format='json',titles='|'.join(unresolved),redirects=1,prop='pageprops',ppprop='wikibase_item'));p=CACHE/('redirects-'+hashlib.sha1(params.encode()).hexdigest()+'.json')
  if not p.exists():subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','--max-time','45','https://en.wikipedia.org/w/api.php?'+params,'--output',str(p)],check=True)
  d=json.loads(p.read_bytes())['query'];redirects={r['from']:r['to']for r in d.get('normalized',[])+d.get('redirects',[])};pages={r['title']:r.get('pageprops',{}).get('wikibase_item')for r in d['pages'].values()}
  for t in unresolved:
   n=t
   for _ in range(8):n=redirects.get(n,n)
   if pages.get(n):resolved[t]=pages[n]
  ids=sorted({resolved[t]for t in unresolved if t in resolved}-pool.keys())
  if ids:
   params=urllib.parse.urlencode(dict(action='wbgetentities',format='json',ids='|'.join(ids),props='labels|claims|sitelinks',languages='zh-hans|zh|en'));p=CACHE/('redirect-people-'+hashlib.sha1(params.encode()).hexdigest()+'.json')
   if not p.exists():subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','--max-time','45','https://www.wikidata.org/w/api.php?'+params,'--output',str(p)],check=True)
   pool.update({q:e for q,e in json.loads(p.read_bytes())['entities'].items()if human(e)})
 write('.local/world-rosters/resolved-titles.json',resolved)
 write('.local/world-rosters/verified-people.json',pool)

def apply():
 pool=read('.local/world-rosters/verified-people.json');by={}
 for q,e in pool.items():
  if not human(e):continue
  for t in [e.get('labels',{}).get('en',{}).get('value'),e.get('sitelinks',{}).get('enwiki',{}).get('title')]:
   if t:by[t]=q
 for t,q in read('.local/world-rosters/resolved-titles.json').items():
  if human(pool.get(q,{})):by[t]=q
 missing=sorted({r['title']for r in ROWS if r['title']not in by and ALIASES.get(r['title'])not in by})
 if missing:raise ValueError('Resolve exact human biographies first: '+repr(missing))
 facts=read('public/data/polity-facts.json');review=[];duplicates=0
 for q in {r['country']for r in ROWS}:
  if q not in facts['entities']:raise ValueError('Missing polity archive '+q)
  e=facts['entities'][q];e['fields']['ruler']=[x for x in e['fields'].get('ruler',[])if x.get('supplement')!=TAG]
 for r in ROWS:
  q=by.get(r['title'])or by[ALIASES[r['title']]];e=pool[q]
  for prop,wrong in [('P569',lambda y:y>r['end']),('P570',lambda y:y<r['start'])]:
   ys=[int(s['value']['time'][:5])for c in e.get('claims',{}).get(prop,[])if(s:=simplify(c))and isinstance(s['value'],dict)and'time'in s['value']]
   if ys and all(wrong(y)for y in ys):raise ValueError('Lifespan incompatible with appointment '+repr(r))
  dst=facts['entities'][r['country']]['fields']['ruler']
  if any(x.get('value')==q and x.get('from')==r['start']and x.get('to')==r['end']for x in dst):duplicates+=1;continue
  role=r['role']
  if r['title']=='Haile Selassie'and r['start']==1936:role='流亡皇帝及其主权主张；意大利占领期，不表示当时直接控制本土'
  row=dict(value=q,label=r['label'],roleLabel=role,at=None,rank='preferred',supplement=TAG,citation=[r['source'],'https://www.wikidata.org/wiki/'+q],**{'from':r['start'],'to':r['end']})
  if r['title']=='Osei Kofi Tutu I':row.update(approximate=True,inference='在位终年常作约1717年，未冒充精确到日的纪年。')
  dst.append(row);facts['labels'][q]=r['label'];review.append(dict(country=r['country'],**row))
 for q in {r['country']for r in ROWS}:facts['entities'][q]['rulerScopeNote']='按具名在位年表补录；交接年可有先后任职、争位或共治，不表示全部人物同时控制全境。没有自动补齐所有摄政和地方实权人物。'
 write('public/data/polity-facts.json',facts)
 used={r['value']for r in review};wanted={by.get(r['title'])or by[ALIASES[r['title']]]for r in ROWS};write('.local/world-rosters/verified-people.json',{q:e for q,e in pool.items()if q in wanted})
 write('public/data/world-rosters-review.json',dict(reviewedAt='2026-11-02',tag=TAG,appointments=review,summary=dict(added=len(review),existingExactDuplicatesSkipped=duplicates,polities=len({r['country']for r in review}),people=len(used)),limitations=['本轮为明确列出的国家与时期，不是全球完整君主名录。','葡萄牙1383—1385年摄政危机、摩洛哥1727—1757年诸次内战等未以延长前任来伪造连续执政。','越南陈朝上皇、葡萄牙摄政及巴西摄政时期须与正式君主区分。']))
 print('Appointments added',len(review),'exact duplicates skipped',duplicates,'people',len(used),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['fetch','apply']);a=p.parse_args();globals()[a.stage]()
