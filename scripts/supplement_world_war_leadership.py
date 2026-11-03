"""Source-checked office terms for the World War years."""
from territory_repair_stage import read, write

TAG = 'world-war-officeholders-2026-11-03'
path = 'public/data/polity-facts.json'
data = read(path)
entities = data['entities']
for entity in entities.values():
    for field in ('ruler','headOfGovernment'):
        if field in entity['fields']:
            entity['fields'][field] = [row for row in entity['fields'][field] if row.get('supplement') != TAG]

def add(country, field, role, source, rows):
    records = entities[country]['fields'].setdefault(field, [])
    for person, label, start, end, *custom_role in rows:
        identifier = person if person.startswith('Q') else f'local:person-{person}'
        records[:] = [row for row in records if not (
            row.get('supplement') != TAG and row.get('value') == identifier and row.get('from') is not None
            and row['from'] <= end and (row.get('to') or 9999) >= start
        )]
        records.append(dict(value=identifier,label=label,from_=start,to=end,at=None,
                            roleLabel=custom_role[0] if custom_role else role,
                            citation=[source],supplement=TAG))
        records[-1]['from'] = records[-1].pop('from_')
        data['labels'][identifier] = label

ITALY = 'https://bpr.camera.it/bpr/allegati/show/23350_3505_t'
ITALY_CROWN = 'https://archivio.quirinale.it/aspr/soggetti-produttori/CPF-001-000596/uffici-del-capo-provvisorio-dello-stato'
MUSSOLINI = 'https://encyclopedia.ushmm.org/content/en/article/benito-mussolini-1'
add('Q172579','headOfGovernment','意大利王国部长会议主席',ITALY,[
    ('salandra','安东尼奥·萨兰德拉',1914,1916),
    ('boselli','保罗·博塞利',1916,1917),
    ('vittorio-orlando','维托里奥·埃马努埃莱·奥兰多',1917,1919),
    ('nitti','弗朗切斯科·萨韦里奥·尼蒂',1919,1920),
    ('giolitti','乔瓦尼·焦利蒂',1920,1921),
    ('Q313717','伊万诺埃·博诺米',1921,1922),
    ('facta','路易吉·法克塔',1922,1922),
    ('Q23559','贝尼托·墨索里尼',1922,1943,'政府首脑；1943年7月25日被解除职务'),
    ('badoglio','彼得罗·巴多格里奥',1943,1944,'政府首脑；1943年7月25日接任'),
    ('Q313717','伊万诺埃·博诺米',1944,1945),
    ('Q471315','费卢西奥·帕里',1945,1945),
    ('de-gasperi','阿尔契德·德加斯佩里',1945,1946),
])
add('Q172579','ruler','意大利王国元首',ITALY_CROWN,[
    ('Q150642','维托里奥·埃马努埃莱三世',1900,1946,'意大利国王；1944年起由王储代行王权'),
    ('Q187149','翁贝托二世',1944,1946,'1944年起代理王权；1946年5月继位'),
])
add('local:italian-social-republic','ruler','意大利社会共和国领导人',MUSSOLINI,[
    ('Q23559','贝尼托·墨索里尼',1943,1945,'1943年9月起领导德国支持的意大利社会共和国'),
])

FRANCE = 'https://www.elysee.fr/la-presidence/les-presidents-de-la-republique'
add('Q70802','ruler','法兰西第三共和国总统',FRANCE,[
    ('poincare','雷蒙·普恩加莱',1913,1920),('deschanel','保罗·德沙内尔',1920,1920),
    ('millerand','亚历山大·米勒兰',1920,1924),('doumergue','加斯东·杜梅格',1924,1931),
    ('doumer','保罗·杜美',1931,1932),('lebrun','阿尔贝·勒布伦',1932,1940),
])
add('Q152582','ruler','法国抵抗运动及其政府机构领导人','https://www.ordredelaliberation.fr/fr/la-france-libre',[
    ('Q2042','夏尔·戴高乐',1940,1942,'自由法国领导人'),
    ('Q2042','夏尔·戴高乐',1943,1944,'法国民族解放委员会主席；1943年初期与吉罗共同主持'),
    ('Q2042','夏尔·戴高乐',1944,1946,'法兰西共和国临时政府主席'),
])
add('Q69808','headOfGovernment','维希法国政府首脑','https://encyclopedia.ushmm.org/content/en/article/france',[
    ('pierre-laval','皮埃尔·赖伐尔',1942,1944),
])

UK = 'https://www.gov.uk/government/history/past-prime-ministers'
uk_terms = [
    ('asquith','赫伯特·亨利·阿斯奎斯',1908,1916),('lloyd-george','戴维·劳合·乔治',1916,1922),
    ('bonar-law','安德鲁·博纳·劳',1922,1923),('stanley-baldwin','斯坦利·鲍德温',1923,1924),
    ('ramsay-macdonald','拉姆齐·麦克唐纳',1924,1924),('stanley-baldwin','斯坦利·鲍德温',1924,1929),
    ('ramsay-macdonald','拉姆齐·麦克唐纳',1929,1935),('stanley-baldwin','斯坦利·鲍德温',1935,1937),
    ('Q10664','内维尔·张伯伦',1937,1940),('Q8016','温斯顿·丘吉尔',1940,1945),
    ('Q129006','克莱门特·艾德礼',1945,1951),
]
for identifier in ('Q145','Q174193'):
    add(identifier,'headOfGovernment','联合王国首相',UK,
        [term for term in uk_terms if identifier=='Q145' or term[2]<=1927])

AUS = 'https://www.naa.gov.au/explore-collection/australias-prime-ministers'
add('Q408','headOfGovernment','澳大利亚总理',AUS,[
    ('joseph-cook','约瑟夫·库克',1913,1914),('andrew-fisher','安德鲁·费希尔',1914,1915),
    ('Q152666','比利·休斯',1915,1923),('stanley-bruce','斯坦利·布鲁斯',1923,1929),
    ('james-scullin','詹姆斯·斯卡林',1929,1932),('joseph-lyons','约瑟夫·莱昂斯',1932,1939),
    ('earle-page','厄尔·佩奇',1939,1939),('Q214438','罗伯特·孟席斯',1939,1941),
    ('arthur-fadden','阿瑟·法登',1941,1941),('Q23375','约翰·柯廷',1941,1945),
    ('frank-forde','弗兰克·福德',1945,1945),('ben-chifley','本·奇夫利',1945,1949),
])
CAN = 'https://guide-ministries.canada.ca/en/canadian-ministries'
add('Q16','headOfGovernment','加拿大总理',CAN,[
    ('robert-borden','罗伯特·博登',1911,1920),('arthur-meighen','阿瑟·米恩',1920,1921),
    ('Q128633','威廉·莱昂·麦肯齐·金',1921,1926),('arthur-meighen','阿瑟·米恩',1926,1926),
    ('Q128633','威廉·莱昂·麦肯齐·金',1926,1930),('rb-bennett','理查德·贝德福德·贝内特',1930,1935),
    ('Q128633','威廉·莱昂·麦肯齐·金',1935,1948),
])
add('Q664','headOfGovernment','新西兰总理','https://nzhistory.govt.nz/page/biographies',[
    ('william-massey','威廉·梅西',1912,1925),('michael-savage','迈克尔·约瑟夫·萨维奇',1935,1940),
    ('Q1400226','彼得·弗雷泽',1940,1949),
])
# Shared monarchs are scoped to the three self-governing dominions.
for identifier in ('Q408','Q16','Q664'):
    add(identifier,'ruler','共主君主',UK,[
        ('Q269412','乔治五世',1910,1936),('Q590227','爱德华八世',1936,1936),
        ('Q280856','乔治六世',1936,1952),
    ])

JAPAN = 'https://japan.kantei.go.jp/past_cabinet/index.html'
add('Q188712','headOfGovernment','日本内阁总理大臣',JAPAN,[
    ('yamamoto-gonnohyoe','山本权兵卫',1913,1914),('okuma-shigenobu','大隈重信',1914,1916),
    ('terauchi-masatake','寺内正毅',1916,1918),('hara-takashi','原敬',1918,1921),
    ('konoe-fumimaro','近卫文麿',1937,1939),('hiranuma-kiichiro','平沼骐一郎',1939,1939),
    ('abe-nobuyuki','阿部信行',1939,1940),('yonai-mitsumasa','米内光政',1940,1940),
    ('konoe-fumimaro','近卫文麿',1940,1941),('tojo-hideki','东条英机',1941,1944),
    ('Q315549','小矶国昭',1944,1945),('Q335198','铃木贯太郎',1945,1945),
    ('higashikuni','东久迩宫稔彦王',1945,1945),('shidehara-kijuro','币原喜重郎',1945,1946),
])

POLAND = 'https://t.prezydent.pl/kancelaria/archiwum/archiwum-bronislawa-komorowskiego/kancelaria/aktywnosc-ministrow/75-rocznica-objecia-urzedu-prezydenta-rp-na-uchodzstwie-przez-wladyslawa-raczkiewicza%2C21409'
add('Q207272','ruler','波兰第二共和国总统',POLAND,[
    ('ignacy-moscicki','伊格纳齐·莫希齐茨基',1926,1939),
    ('wladyslaw-raczkiewicz','瓦迪斯瓦夫·拉奇凯维奇',1939,1947,'波兰流亡政府总统；1939年9月30日接任'),
])
add('Q28','ruler','匈牙利王国摄政','https://encyclopedia.ushmm.org/content/en/article/the-holocaust-in-hungary',[
    ('miklos-horthy','米克洛什·霍尔蒂',1920,1944,'匈牙利王国摄政；1944年10月下台'),
    ('Q156473','费伦茨·萨拉希',1944,1945,'箭十字党政权领导人；1944年10月起'),
])

ROC = 'https://art.archives.gov.tw/tw/art/1620.html'
add('Q13426199','ruler','中华民国国民政府主席',ROC,[
    ('Q705872','林森',1931,1943),('Q16574','蒋介石',1943,1948),
])
add('Q13426199','ruler','中华民国大总统','https://ppg.ly.gov.tw/ppg/PublicationBulletinDetail/download/communique1/final/pdf/100/02/LCIDC01_1000201.pdf',[
    ('Q210329','袁世凯',1912,1916),('Q716136','黎元洪',1916,1917),
    ('Q700576','冯国璋',1917,1918,'代理大总统'),('Q702428','徐世昌',1918,1922),
])
add('Q175379','ruler','洪宪帝制的皇帝','https://ppg.ly.gov.tw/ppg/PublicationBulletinDetail/download/communique1/final/pdf/100/02/LCIDC01_1000201.pdf',[
    ('Q210329','袁世凯',1915,1916,'称帝并改元洪宪；1916年取消帝制'),
])

add('Q28513','ruler','奥地利皇帝兼匈牙利国王',
    'https://www.parlament.gv.at/verstehen/historisches/1848-1918/erster-weltkrieg-ende-monarchie',[
    ('franz-joseph-i','弗朗茨·约瑟夫一世',1867,1916),
    ('Q51068','卡尔一世（匈牙利国王卡洛伊四世）',1916,1918),
])
add('Q7318','headOfGovernment','德国总理',
    'https://encyclopedia.ushmm.org/content/en/article/law-on-the-head-of-state-of-the-german-reich-1',[
    ('Q352','阿道夫·希特勒',1933,1945),
])
add('Q17427','ruler','中共战时领导',
    'https://www.jms.gov.cn/jms/c100008/202303/c04_42.shtml',[
    ('zhang-wentian','张闻天',1935,1943,'在党内负总责'),
])
add('Q17427','ruler','中共战时领导',
    'https://www.mod.gov.cn/gfbw/qwfb/4888306.html',[
    ('Q5816','毛泽东',1943,1949,'1943年起任中央政治局主席；1945年当选中央委员会主席'),
])
# The source misidentifies twentieth-century Greece as the First Republic.
entities.setdefault('local:second-hellenic-republic', dict(label='希腊第二共和国', en='Second Hellenic Republic',
    description='1924—1935年的希腊共和政体。', fields={}))
greek_royal = 'https://www.ime.gr/projects/cooperations/f_policy36_45/en/text/131.html'
add('Q209065','ruler','希腊国王',
    'https://foundation.parliament.gr/sites/default/files/2020-06/Introduction%20to%20the%20Constitutional%20History%20of%20Modern%20of%20Greece.pdf',[
    ('constantine-i-greece','康斯坦丁一世',1913,1917),
    ('alexander-greece','亚历山大一世',1917,1920),
    ('constantine-i-greece','康斯坦丁一世',1920,1922),
    ('Q152935','乔治二世',1922,1924),
    ('Q152935','乔治二世',1935,1947,'1935年复位；1941年流亡，1946年回国'),
])
add('Q209065','ruler','希腊摄政',
    'https://www.elia.org.gr/userfiles/pdf_archieve/1945%201-345%20Dekembriana%2C%20Athens%2C%20Damaskinos%2C%20EAM-ELAS%2C%20Sophoulis%2C%20Truce%2C%20%20319-85-112110%20%28Naval%29.pdf',[
    ('damaskinos','达马斯基诺斯大主教',1944,1946),
])
add('Q209065','headOfGovernment','希腊首相',greek_royal,[
    ('ioannis-metaxas','扬尼斯·梅塔克萨斯',1936,1941),
])
add('Q209065','headOfGovernment','希腊流亡政府首相',
    'https://www.elia.org.gr/userfiles/pdf_archieve/1944%2010-144%20Greek%20Government%2C%20Public%20Health%2C%20Press%2C%20Geography%2C%20Collaborators%2C%20Italian%20Troops%2C%20German%20Troops%2C%20Civil%20Administration%2C%20%5B52%20pgs%5D%20226-CID-41174%20%28OSS%29.pdf',[
    ('emmanouil-tsouderos','埃马努伊尔·楚泽罗斯',1941,1944),
])
add('local:second-hellenic-republic','ruler','希腊共和国总统','https://helios.eie.gr/helios/handle/10442/8763',[
    ('pavlos-kountouriotis','帕夫洛斯·孔杜里奥蒂斯',1924,1926),
    ('theodoros-pangalos','塞奥多罗斯·潘加洛斯',1926,1926),
    ('pavlos-kountouriotis','帕夫洛斯·孔杜里奥蒂斯',1926,1929),
])
add('local:second-hellenic-republic','ruler','希腊共和国总统','https://www.elisme.gr/en/i-y/',[
    ('alexandros-zaimis','亚历山德罗斯·扎伊米斯',1929,1935),
])

YUG = 'https://www.archontology.org/nations/yugoslavia/00_1918_41_s.php'
add('Q83286','ruler','南斯拉夫王国元首',YUG,[
    ('peter-i-serbia','彼得一世',1918,1921,'塞尔维亚人、克罗地亚人和斯洛文尼亚人王国国王'),
    ('alexander-i-yugoslavia','亚历山大一世',1921,1934,'1929年国名改为南斯拉夫王国'),
    ('peter-ii-yugoslavia','彼得二世',1934,1945,'南斯拉夫国王；1941年流亡，1945年君主制废除'),
])
add('Q83286','ruler','南斯拉夫摄政委员会首席摄政','https://royalfamily.org/hrh-prince-paul-of-yugoslavia-regent-3/',[
    ('prince-paul-yugoslavia','保罗亲王',1934,1941),
])
add('Q155198','ruler','南斯拉夫游击队领导人','https://royalfamily.org/wp-content/uploads/2023/03/Press-Kit-2023-ENGLISH-1.pdf',[
    ('Q9161','约瑟普·布罗兹·铁托',1941,1945),
])
add('Q83286','headOfGovernment','南斯拉夫联邦政府首脑','https://www.britannica.com/biography/Josip-Broz-Tito',[
    ('Q9161','约瑟普·布罗兹·铁托',1945,1953),
])

ALB = 'https://ambasadat.gov.al/usa/en/presidenti-i-republikes/'
add('Q222','ruler','阿尔巴尼亚国家元首',ALB,[
    ('fan-noli','凡·诺利',1924,1924,'临时政府首脑，兼行元首职责'),
    ('zog','艾哈迈德·佐古',1925,1928,'共和国总统'),
    ('zog','佐古一世',1928,1939,'阿尔巴尼亚国王'),
    ('Q150642','维托里奥·埃马努埃莱三世',1939,1943,'意大利占领后兼任阿尔巴尼亚国王'),
])
add('Q222','ruler','德占时期四人最高摄政委员会',
    'https://ambasadat.gov.al/poland/historiku-i-parlamentarizmit-shqiptar/',[
    ('albanian-regency-council','阿尔巴尼亚最高摄政委员会',1943,1944),
])
entities['Q222']['fields']['ruler'][-1]['kind'] = 'collective'
for identifier in ('Q222','Q467864'):
    add(identifier,'headOfGovernment','阿尔巴尼亚政府首脑','https://ambasadat.gov.al/council-of-europe/en/kryetari-i-keshillit-te-ministrave/',[
        ('Q53783','恩维尔·霍查',1944,1954),
    ])
add('Q467864','ruler','阿尔巴尼亚人民议会主席团主席',ALB,[
    ('Q560630','奥默尔·尼沙尼',1946,1953),
])
# The pre-1946 source incorrectly attaches the later chairmanship to the 1944 frame.
entities['Q222']['fields']['ruler'] = [
    row for row in entities['Q222']['fields']['ruler']
    if not (row.get('value')=='Q560630' and row.get('from')==1944)
]

add('local:qajar-iran','ruler','伊朗国王',
    'https://www.iranicaonline.org/articles/ahmad-shah-qajar-1909-1925-the-seventh-and-last-ruler-of-the-qajar-dynasty/',[
    ('ahmad-shah-qajar','艾哈迈德沙·卡扎尔',1909,1925),
])
add('Q207991','ruler','伊朗国王','https://www.iranicaonline.org/articles/iran-ii2-islamic-period-page-6/',[
    ('reza-shah','礼萨·沙阿·巴列维',1925,1941),
    ('Q128245','穆罕默德·礼萨·巴列维',1941,1979),
])
add('Q207991','headOfGovernment','伊朗首相','https://etheses.dur.ac.uk/1225/1/1225.pdf',[
    ('mohammad-ali-foroughi','穆罕默德·阿里·福鲁吉',1941,1942),
    ('ali-soheili','阿里·苏海利',1942,1942),
    ('ahmad-qavam','艾哈迈德·卡瓦姆',1942,1943),
    ('ali-soheili','阿里·苏海利',1943,1944),
])

EST = 'https://www.archontology.org/nations/estonia/00_1920_37_s.php'
add('Q191','ruler','爱沙尼亚国务长老',EST,[
    ('jaan-tonisson','扬·特尼松',1919,1920,'总理，国务长老制度实施前'),
    ('Q299114','康斯坦丁·佩茨',1921,1922),('juhan-kukk','尤汉·库克',1922,1923),
    ('Q299114','康斯坦丁·佩茨',1923,1924),('friedrich-akel','弗里德里希·阿克尔',1924,1924),
    ('juri-jaakson','于里·亚克松',1924,1925),('jaan-teemant','扬·泰曼特',1925,1927),
    ('jaan-tonisson','扬·特尼松',1927,1928),('august-rei','奥古斯特·雷伊',1928,1929),
    ('otto-strandman','奥托·斯特兰德曼',1929,1931),('Q299114','康斯坦丁·佩茨',1931,1932),
    ('jaan-teemant','扬·泰曼特',1932,1932),('karl-einbund','卡尔·艾因本德',1932,1932),
    ('Q299114','康斯坦丁·佩茨',1932,1933),('jaan-tonisson','扬·特尼松',1933,1933),
    ('Q299114','康斯坦丁·佩茨',1933,1937,'国务长老；1934年起代理元首'),
])
add('Q191','ruler','爱沙尼亚国家元首','https://www.tlulib.ee/en/exhibition/estonian-heads-of-state-1918-2016/',[
    ('Q299114','康斯坦丁·佩茨',1937,1938,'摄政时期的国家元首'),
    ('Q299114','康斯坦丁·佩茨',1938,1940,'爱沙尼亚总统'),
])
add('Q211','ruler','拉脱维亚共和国总统','https://www.president.lv/en/history-presidency',[
    ('janis-cakste','亚尼斯·恰克斯特',1920,1922,'立宪会议主席，行使元首职能'),
    ('janis-cakste','亚尼斯·恰克斯特',1922,1927),
    ('gustavs-zemgals','古斯塔夫斯·泽姆加尔斯',1927,1930),
    ('alberts-kviesis','阿尔贝茨·克维耶西斯',1930,1936),
    ('karlis-ulmanis','卡尔利斯·乌尔马尼斯',1936,1940),
])
add('Q37','ruler','立陶宛共和国总统','https://istorineprezidentura.lt/en/k/presidents/',[
    ('antanas-smetona','安塔纳斯·斯梅托纳',1919,1920),
    ('aleksandras-stulginskis','亚历山德拉斯·斯图尔金斯基斯',1920,1926,'1920年起行使总统职权；1922年正式当选'),
    ('kazys-grinius','卡济斯·格里纽斯',1926,1926),
    ('antanas-smetona','安塔纳斯·斯梅托纳',1926,1940),
])

SPAIN = 'https://www.congreso.es/es/web/guest/cem/iirepesp'
add('Q178038','ruler','西班牙第二共和国总统',SPAIN,[
    ('niceto-alcala-zamora','尼塞托·阿尔卡拉-萨莫拉',1931,1936),
    ('manuel-azana','曼努埃尔·阿萨尼亚',1936,1939),
])
add('Q178038','headOfGovernment','西班牙共和国部长会议主席',SPAIN,[
    ('jose-giral','何塞·希拉尔',1936,1936),('largo-caballero','弗朗西斯科·拉尔戈·卡瓦列罗',1936,1937),
    ('juan-negrin','胡安·内格林',1937,1939),
])
add('Q2742116','ruler','西班牙国民派领导人','https://www.boe.es/gazeta/dias/1936/09/30/pdfs/BJD-1936-32.pdf',[
    ('miguel-cabanellas','米格尔·卡瓦内利亚斯',1936,1936,'1936年7—9月国防委员会主席'),
    ('Q29179','弗朗西斯科·佛朗哥',1936,1939,'1936年秋接任国民派最高领导'),
])

IRE = 'https://www.gov.ie/en/department-of-the-taoiseach/publications/former-taoisigh/'
add('Q31747','headOfGovernment','爱尔兰自由邦行政委员会主席',IRE,[
    ('wt-cosgrave','威廉·托马斯·科斯格雷夫',1922,1932),
    ('Q173347','埃蒙·德·瓦莱拉',1932,1937),
])
add('Q31747','ruler','爱尔兰自由邦总督（王室代表）','https://www.dib.ie/biography/healy-timothy-michael-a3903',[
    ('tim-healy','蒂莫西·希利',1922,1928),
])
add('Q31747','ruler','爱尔兰自由邦总督（王室代表）','https://www.dib.ie/index.php/biography/mcneill-james-a5751',[
    ('james-mcneill','詹姆斯·麦克尼尔',1928,1932),
])
add('Q31747','ruler','爱尔兰自由邦总督（王室代表）','https://www.dib.ie/biography/o-buachalla-ua-buachalla-domhnall-donaldaniel-richard-buckley-a6284',[
    ('domhnall-ua-buachalla','多纳尔·乌阿·布阿哈拉',1932,1936),
])
add('Q27','headOfGovernment','爱尔兰总理',IRE,[
    ('Q173347','埃蒙·德·瓦莱拉',1937,1948),
])
for country, field, obsolete in [
    ('Q27','headOfGovernment','local:person-eamon-de-valera'),
    ('Q222','headOfGovernment','local:person-enver-hoxha'),
    ('Q467864','headOfGovernment','local:person-enver-hoxha'),
]:
    entities[country]['fields'][field] = [row for row in entities[country]['fields'][field] if row['value']!=obsolete]
write(path,data)
print('Dated appointments:',sum(row.get('supplement')==TAG for entity in entities.values() for rows in entity['fields'].values() for row in rows))
