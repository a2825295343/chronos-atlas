"""Dated local seats, independent of the archive identity of a colonial power.

Run before build_map_capitals.py. Names in parentheses identify regional seats
and council centres within composite map records, rather than national capitals.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = 'american-and-asian-seats-2026-11-05'


def read(name):
    return json.loads((ROOT / 'public/data' / name).read_text(encoding='utf-8'))


def write(name, data):
    (ROOT / 'public/data' / name).write_text(
        json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


polities = {}
translations = {
    'Maimbung': '迈姆邦', 'Jolo': '霍洛', 'Buansa': '布安萨',
    'Nallur': '纳卢尔', 'Old City of Taiz': '塔伊兹老城',
}


def seat(names, label, point, start, end, source):
    for name in names.split('|'):
        polities.setdefault(name, []).append(
            [label, point, start, end, None, True, source, name])


# Indigenous states with documented political centres. Broad cultural or
# geographical coverage records do not receive a fabricated single capital.
seat('Tenochtitlan|Aztec Triple Alliance', '特诺奇提特兰', [-99.132, 19.435], 1325, 1521,
     'https://www.loc.gov/exhibits/exploring-the-early-americas/urban-landscapes.html')
seat('Texcoco', '特斯科科', [-98.883, 19.511], 1200, 1521,
     'https://www.britannica.com/place/Texcoco')
seat('Michoacán', '钦聪灿', [-101.5789, 19.6283], 1450, 1530,
     'https://lugares.inah.gob.mx/en/node/4481')
seat('Cuzco|Inca Empire', '库斯科', [-71.978, -13.517], 1200, 1533,
     'https://whc.unesco.org/en/list/273/')
seat('Inca Empire', '比尔卡班巴（新印加王廷）', [-73.2075, -12.9022], 1539, 1572,
     'https://intiyana.org/pdf/catalogoespiritupampa.pdf')
seat('Chimor|Chimu Empire', '昌昌', [-79.074, -8.110], 1000, 1470,
     'https://whc.unesco.org/en/list/366/')
seat('Itza Mayans', '诺赫佩滕（伊察王廷）', [-89.892, 16.930], 1450, 1697,
     'https://mcd.gob.gt/tayasal/')
seat('Later Mayan City-States|Maya City States', '玛雅潘（区域政治中心）', [-89.460, 20.629], 1200, 1449,
     'https://www.nature.com/articles/s41467-022-31522-x')
seat('Toltec', '图拉', [-99.341, 20.065], 900, 1150,
     'https://lugares.inah.gob.mx/es/zonas-arqueologicas/tula')
seat('Cahokia Polity', '卡霍基亚（酋邦中心）', [-90.062, 38.660], 1050, 1350,
     'https://whc.unesco.org/en/list/198/')

# French, Dutch and Swedish colonies, with their own dates and local names.
quebec = 'https://www.clo-ocol.gc.ca/en/french-explorer-samuel-champlain-founds-quebec-city'
seat('New France|France Colony - Canada', '魁北克', [-71.207, 46.813], 1608, 1759, quebec)
seat('New Netherland', '新阿姆斯特丹', [-74.0124, 40.7037], 1625, 1664,
     'https://www.nps.gov/elis/learn/historyculture/places_colonial_early_american.htm')
seat('New Netherland', '新奥兰治（荷兰复占）', [-74.0124, 40.7037], 1673, 1674,
     'https://www.nps.gov/elis/learn/historyculture/places_colonial_early_american.htm')
seat('New Sweden', '克里斯蒂娜堡', [-75.5385, 39.7371], 1638, 1655,
     'https://www.nps.gov/frst/learn/historyculture/fort-christina.htm')
seat('France Colony - United States of America', '莫比尔（路易斯安那首府）', [-88.044, 30.695], 1702, 1719,
     'https://www.britannica.com/place/Louisiana-state/History')
seat('France Colony - United States of America', '比洛克西（路易斯安那首府）', [-88.885, 30.396], 1720, 1721,
     'https://www.britannica.com/place/Louisiana-state/History')
seat('France Colony - United States of America', '新奥尔良（路易斯安那首府）', [-90.064, 29.958], 1722, 1762,
     'https://www.britannica.com/place/New-Orleans-Louisiana/History')
seat('French Colony of Guiana|France Colony - French Guiana', '卡宴', [-52.335, 4.938], 1664, 1946,
     'https://www.britannica.com/place/Cayenne-French-Guiana')
seat('France Colony - Haiti', '法兰西角（殖民行政中心）', [-72.199, 19.759], 1711, 1769,
     'https://www.britannica.com/place/Cap-Haitien')
seat('France Colony - Haiti', '太子港', [-72.338, 18.543], 1770, 1803,
     'https://www.britannica.com/place/Port-au-Prince')

# A map record covering the British Atlantic colonies has several provincial
# seats. Never identify one of them as the capital of all thirteen colonies.
british_america = 'United Kingdom Colony - United States of America|English Colonial Empire'
jamestown = 'https://www.nps.gov/jame/learn/historyculture/a-short-history-of-jamestown.htm'
seat(british_america, '詹姆斯敦（弗吉尼亚首府）', [-76.778, 37.209], 1607, 1698, jamestown)
seat(british_america, '威廉斯堡（弗吉尼亚首府）', [-76.702, 37.271], 1699, 1775, jamestown)
seat(british_america, '波士顿（马萨诸塞首府）', [-71.058, 42.360], 1630, 1775,
     'https://www.britannica.com/place/Boston/History')
seat(british_america, '纽约（纽约殖民地首府）', [-74.0124, 40.7037], 1664, 1775,
     'https://www.nps.gov/elis/learn/historyculture/places_colonial_early_american.htm')
seat(british_america, '费城（宾夕法尼亚首府）', [-75.150, 39.949], 1682, 1775,
     'https://www.nps.gov/inde/learn/historyculture/places.htm')
seat('United Kingdom Colony - Canada', '魁北克（加拿大行政中心）', [-71.207, 46.813], 1763, 1840,
     'https://www.thecanadianencyclopedia.ca/en/article/quebec-act')
seat('United Kingdom Colony - Canada', '金斯敦（联合加拿大首府）', [-76.486, 44.231], 1841, 1843,
     'https://www.thecanadianencyclopedia.ca/en/article/province-of-canada-1841-67')
seat('United Kingdom Colony - Canada', '蒙特利尔（联合加拿大首府）', [-73.554, 45.508], 1844, 1849,
     'https://www.thecanadianencyclopedia.ca/en/article/province-of-canada-1841-67')
for city, point, first, last in [
    ('多伦多', [-79.383, 43.653], 1850, 1851),
    ('魁北克', [-71.207, 46.813], 1852, 1855),
    ('多伦多', [-79.383, 43.653], 1856, 1859),
    ('魁北克', [-71.207, 46.813], 1860, 1865),
    ('渥太华', [-75.699, 45.424], 1866, 1931),
]:
    seat('United Kingdom Colony - Canada', city, point, first, last,
         'https://www.pc.gc.ca/apps/dfhd/page_nhs_eng.aspx?id=1637')
seat('United Kingdom Colony - Canada', '安纳波利斯罗亚尔（新斯科舍首府）', [-65.518, 44.743], 1710, 1748,
     'https://www.thecanadianencyclopedia.ca/en/article/annapolis-royal')
seat('United Kingdom Colony - Canada', '哈利法克斯（新斯科舍首府）', [-63.573, 44.648], 1749, 1867,
     'https://www.thecanadianencyclopedia.ca/en/article/halifax')
for name, label, point, first, last, source in [
    ('Jamaica', '西班牙镇', [-76.956, 17.991], 1655, 1871, 'https://www.britannica.com/place/Spanish-Town'),
    ('Jamaica', '金斯敦', [-76.793, 17.968], 1872, 1962, 'https://www.britannica.com/place/Kingston-Jamaica'),
    ('Barbados', '布里奇敦', [-59.614, 13.097], 1628, 1966, 'https://whc.unesco.org/en/list/1376/'),
    ('Belize', '伯利兹城', [-88.188, 17.495], 1786, 1969, 'https://www.belizecitycouncil.org/uploads/principles/28359-Belize-City-Council-Municipal-Paper-Prospectus-2020.pdf'),
    ('Belize', '贝尔莫潘', [-88.767, 17.251], 1970, 1981, 'https://digitallibrary.un.org/record/5077'),
    ('Guyana', '斯塔布鲁克', [-58.164, 6.813], 1796, 1811, 'https://www.britannica.com/place/Georgetown-Guyana'),
    ('Guyana', '乔治敦', [-58.164, 6.813], 1812, 1966, 'https://www.britannica.com/place/Georgetown-Guyana'),
    ('Trinidad and Tobago', '西班牙港', [-61.518, 10.653], 1797, 1962, 'https://www.britannica.com/place/Port-of-Spain'),
    ('Grenada', '圣乔治', [-61.752, 12.053], 1763, 1974, 'https://www.britannica.com/place/Saint-Georges-Grenada'),
    ('Dominica', '罗索', [-61.388, 15.299], 1763, 1978, 'https://www.britannica.com/place/Roseau'),
    ('Saint Lucia', '卡斯特里', [-60.990, 14.010], 1814, 1979, 'https://www.britannica.com/place/Castries'),
]:
    seat('United Kingdom Colony - ' + name, label, point, first, last, source)

# Spanish regional seats. Modern-country splits in the base GIS do not make
# each slice an independent viceroyalty, so label its administrative function.
viceroys = 'https://www.cultura.gob.es/en/cultura/archivos/difusion/mc-difusion/bicentenarios/contexto-historico/imperio-espanol/organizacion/virreinatos.html'
seat('Spain Colony - Mexico', '墨西哥城（新西班牙首府）', [-99.132, 19.435], 1535, 1821, viceroys)
seat('Spain Colony - Peru', '利马（秘鲁总督区首府）', [-77.031, -12.046], 1542, 1821,
     'https://whc.unesco.org/en/list/500/')
audiences = 'https://www.cultura.gob.es/cultura/areas/archivos/mc/archivos/agi/consultas/profesionales/encomiendas.html'
for name, label, point, first, last in [
    ('Bolivia', '拉普拉塔（查尔卡斯审问院驻地）', [-65.261, -19.048], 1561, 1825),
    ('Ecuador', '基多（审问院驻地）', [-78.512, -0.220], 1563, 1822),
    ('Colombia', '圣菲波哥大（行政中心）', [-74.076, 4.598], 1550, 1819),
    ('Argentina', '布宜诺斯艾利斯（行政中心）', [-58.373, -34.608], 1580, 1810),
    ('Chile', '圣地亚哥（行政中心）', [-70.651, -33.438], 1541, 1818),
    ('Paraguay', '亚松森（行政中心）', [-57.635, -25.282], 1537, 1811),
    ('Panama', '巴拿马城（行政中心）', [-79.535, 8.952], 1673, 1821),
    ('Venezuela', '加拉加斯（行政中心）', [-66.914, 10.506], 1577, 1811),
    ('Uruguay', '蒙得维的亚（行政中心）', [-56.211, -34.906], 1726, 1814),
]:
    seat('Spain Colony - ' + name, label, point, first, last, audiences)
seat('Spain Colony - Guatemala', '圣地亚哥危地马拉（总督府驻地）', [-90.734, 14.557], 1543, 1775,
     'https://blogs.worldbank.org/en/latinamerica/history-disasters-and-resilience-story-antigua-guatemala')
seat('Spain Colony - Guatemala', '新危地马拉城（总督府驻地）', [-90.513, 14.642], 1776, 1821,
     'https://blogs.worldbank.org/en/latinamerica/history-disasters-and-resilience-story-antigua-guatemala')
for name, label, point, first, last, source in [
    ('Cuba', '哈瓦那', [-82.350, 23.139], 1607, 1898, 'https://whc.unesco.org/en/list/204/'),
    ('Puerto Rico', '圣胡安', [-66.117, 18.466], 1521, 1898, 'https://whc.unesco.org/en/list/266/'),
    ('Dominican Republic', '圣多明各', [-69.883, 18.474], 1498, 1795, 'https://whc.unesco.org/en/list/526/'),
    ('United States of America', '圣奥古斯丁（佛罗里达首府）', [-81.313, 29.894], 1565, 1763, 'https://www.nps.gov/casa/learn/historyculture/index.htm'),
    ('United States of America', '圣奥古斯丁（佛罗里达首府）', [-81.313, 29.894], 1784, 1821, 'https://www.nps.gov/casa/learn/historyculture/index.htm'),
    ('United States of America', '圣菲（新墨西哥首府）', [-105.938, 35.687], 1610, 1821, 'https://www.nps.gov/places/palace-of-the-governors.htm'),
]:
    seat('Spain Colony - ' + name, label, point, first, last, source)
salvador = 'https://www.cms.ba.gov.br/memorial'
seat('Portugal Colony - Brazil|Portuguese Empire', '萨尔瓦多（巴西总督府驻地）', [-38.512, -12.973], 1549, 1762, salvador)
seat('Portugal Colony - Brazil|Portuguese Empire', '里约热内卢（巴西行政中心）', [-43.173, -22.907], 1763, 1822, salvador)
seat('Portugal Colony - Uruguay', '萨克拉门托殖民地', [-57.850, -34.472], 1680, 1777,
     'https://whc.unesco.org/en/list/747/')
seat('Netherlands Colony - Suriname', '帕拉马里博', [-55.150, 5.826], 1667, 1975,
     'https://whc.unesco.org/en/list/940/')
seat('Netherlands Antilles', '威廉斯塔德', [-68.933, 12.109], 1634, 2010,
     'https://whc.unesco.org/en/list/819/')

# Named phases also resolve records whose historical and modern archive QIDs
# differ. Capital moves follow administrative seats, not modern geometry.
oudong = 'https://whc.unesco.org/en/tentativelists/6459/'
seat('Kingdom of Cambodia|Khmer Empire|Cambodia', '乌栋', [104.7425, 11.8239], 1618, 1865, oudong)
seat('Kingdom of Cambodia|Khmer Empire|Cambodia', '金边', [104.928, 11.556], 1866, 2026, oudong)
pakistan = 'Pakistan|Dominion of Pakistan|Islamic Republic of Pakistan'
pakistan_history = 'https://click.gos.pk/history'
seat(pakistan, '卡拉奇', [67.010, 24.860], 1947, 1958, pakistan_history)
seat(pakistan, '拉瓦尔品第（临时首都）', [73.0479, 33.6007], 1959, 1966,
     'https://rda.gop.pk/rawalpindi/')
seat(pakistan, '伊斯兰堡', [73.095, 33.730], 1967, 2026,
     'https://www.cda.gov.pk/storage/app/public/public_notices/9NcEV4Crt4o4tgm2ysgQLhPQgcpJvCvKqrrhiTOZ.pdf')
laos_history = 'https://whc.unesco.org/archive/advisory_body_evaluation/479.pdf'
seat('Lan Xang', '琅勃拉邦', [102.135, 19.892], 1353, 1559, laos_history)
seat('Lan Xang', '万象', [102.613, 17.966], 1560, 1707, laos_history)
seat('Kingdom of Luang Prabang|Kingdom of Luang Phrabang', '琅勃拉邦', [102.135, 19.892], 1707, 1946, laos_history)
seat('Kingdom of Vientiane|Vientiane', '万象', [102.613, 17.966], 1707, 1828, laos_history)
seat('Kingdom of Laos|Laos|Lao People’s Democratic Republic|Lao People\'s Democratic Republic',
     '万象（行政首都）', [102.613, 17.966], 1946, 1975, 'https://whc.unesco.org/document/153552')
seat('Kingdom of Laos|Laos', '琅勃拉邦（王室驻地）', [102.135, 19.892], 1946, 1975,
     'https://events.development.asia/system/files/materials/2023/12/202312-luang-prabang-smart-and-integrated-urban-strategy_0.pdf')
seat('Laos|Communist Laos|Lao People’s Democratic Republic|Lao People\'s Democratic Republic',
     '万象', [102.613, 17.966], 1976, 2026, 'https://whc.unesco.org/document/153552')
write('reviewed-capital-seats.json', {
    'reviewedAt': '2026-11-05',
    'notes': [
        '现代国家切片式殖民地记录按当地行政中心标记；括号说明其实际职能。',
        '原住民地域或文化集合未必具有统一首都，仅为有出处的政权和会址添加标记。',
        '巴基斯坦迁都分阶段完成，采用1959年临时首都、1967年政府迁驻新城的年度划分。',
    ], 'polities': polities, 'translations': translations,
})

# Translate all Sulu capital rows, including unscoped gazetteer records.
index = read('map-capitals.json')
for rows in index['archive'].values():
    for row in rows:
        row[0] = translations.get(row[0], row[0])
index['named'] = polities
write('map-capitals.json', index)

facts = read('polity-facts.json')
entity = facts['entities']['Q4919413']
entity['label'] = '柬埔寨王国'
entity['description'] = '后吴哥时期的柬埔寨王国，王廷先后位于金边、洛韦和乌栋，受暹罗与越南势力竞争影响。'
for field in ['ruler', 'government', 'religion', 'capital', 'language']:
    entity['fields'][field] = [r for r in entity['fields'].get(field, []) if r.get('supplement') != TAG]


def fact(field, label, first, last, source, **extra):
    entity['fields'][field].append(dict(
        value=label, label=label, at=None, citation=[source], supplement=TAG,
        **{'from': first, 'to': last}, **extra))


monarchs = 'https://fr.wikipedia.org/wiki/Monarchie_cambodgienne'
for label, first, last in [
    ('吉哲塔四世', 1700, 1702), ('托摩列阇三世', 1702, 1703),
    ('吉哲塔四世', 1703, 1706), ('托摩列阇三世', 1706, 1710),
    ('安恩', 1710, 1722), ('萨达二世', 1722, 1729), ('安恩', 1729, 1730),
    ('萨达二世', 1730, 1736), ('托摩列阇三世', 1736, 1747),
    ('托摩列阇四世', 1747, 1747), ('安东（Ang Tong）', 1747, 1749),
    ('萨达二世', 1749, 1749), ('吉哲塔五世', 1749, 1755),
    ('安东（Ang Tong）', 1755, 1758), ('乌迭二世', 1758, 1775),
    ('安嫩二世', 1775, 1779), ('安英', 1779, 1796),
    ('波克（摄政）', 1796, 1806), ('安赞二世', 1806, 1834),
    ('安眉女王', 1834, 1841), ('安东（Ang Duong）', 1848, 1860),
    ('诺罗敦', 1860, 1863),
]:
    fact('ruler', label, first, last, monarchs, roleLabel='柬埔寨国王／摄政',
         approximate=True, inference='后吴哥王表纪年有异说，1736/1738等交接年不完全一致；采用所引王表。')
fact('capital', '乌栋', 1618, 1865, oudong)
chandler = 'https://angkordatabase.asia/libs/docs/d.chandler-a-history-of-cambodia.pdf'
fact('government', '世袭君主制', 1618, 1863, chandler)
fact('religion', '上座部佛教', 1659, 1863,
     'https://lib.ncdd.gov.kh/storage/app/public/library_backend/CAT_21463_1/2005-Buddhism-en.pdf')
fact('language', '高棉语', 1618, 1863, chandler)
entity['rulerScopeNote'] = '按后吴哥时期王表补入，部分即位年有异说。年内更替可能显示多位，不能视为同时共治。'
for e in facts['entities'].values():
    for row in e.get('fields', {}).get('capital', []):
        row['label'] = translations.get(row.get('label'), row.get('label'))
write('polity-facts.json', facts)

flags = read('flags.json')
for row in flags['entities'].get('Q627449', []):
    if row['file'] == 'Black flag.svg':
        row.update({
            'from': 1709, 'to': 1738, 'role': '汉达基黑旗（传统归属）',
            'representative': True,
            'periodNote': '纯黑为传统归属于汉达基政权的旗式。具体纹样及各时期使用情况证据有限，作为代表性黑旗展示。',
            'periodSource': 'https://en.wikipedia.org/wiki/Flag_of_Afghanistan',
            'reviewedAt': '2026-11-05',
        })
write('flags.json', flags)
print('Reviewed named capital records:', sum(map(len, polities.values())))
