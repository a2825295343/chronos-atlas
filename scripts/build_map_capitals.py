"""Build the offline capital index from dated archive facts and Natural Earth cities."""
from pathlib import Path
from collections import defaultdict
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".local/python"))
from shapely.geometry import Point, shape

SOURCE = 'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-populated-places/'

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

cities = read('.local/ne-capital-places.geojson')['features']
facts = read('public/data/polity-facts.json')['entities']
curated = read('public/data/curated-facts.json')
by_id, by_name = {}, defaultdict(set)
for city in cities:
    p = city['properties']
    location = tuple(round(x, 5) for x in city['geometry']['coordinates'])
    identifier = p.get('WIKIDATAID')
    if identifier and identifier != '-99':
        by_id[identifier] = location
    for key in ('NAME','NAMEASCII','NAME_EN','NAME_ZH','NAME_ZHT'):
        if p.get(key):
            by_name[p[key]].add(location)

# Archaeological locations and historical names already reviewed in the atlas.
reviewed = {
    '长安':(108.94,34.34), '雒阳':(112.45,34.62), '洛阳':(112.45,34.62),
    '泰西封':(44.58,33.09), '华氏城':(85.14,25.61), '平安京':(135.77,35.01),
    '君士坦丁堡':(28.978,41.008), '埃迪尔内':(26.56,41.68),
    '萨迈拉':(43.87,34.20), '瑟于特':(30.18,40.02),
    '罗马':(12.496,41.903), '许昌':(113.82,34.02),
    '国内城':(126.19,41.13872), '恩吉鲁穆德':(134.63,7.49),

}
manual_names = {
    '应天府（南京）':'南京',
    '北京；南京保留留都地位':'北京',
    '埃迪尔内（阿德里安堡）':'埃迪尔内',
    '君士坦丁堡／伊斯坦布尔':'君士坦丁堡',
    '罗马；晚期皇帝驻地和行政中心有所变化':'罗马',
    '长安（朝廷迁驻）':'长安',
    '许县（朝廷所在地）':'许昌',
}

def position(identifier, label):
    if label in reviewed:
        return reviewed[label]
    matches = by_name[label]
    return by_id.get(identifier) or (next(iter(matches)) if len(matches)==1 else None)

coordinate_cache = ROOT / '.local/capital-coordinate-cache.json'
wikidata = read(coordinate_cache) if coordinate_cache.exists() else {}
if '--fetch-coordinates' in sys.argv:
    missing = sorted({row['value'] for entity in facts.values()
                      for row in entity['fields'].get('capital', [])
                      if isinstance(row['value'], str) and row['value'].startswith('Q')
                      and not position(row['value'], row['label']) and row['value'] not in wikidata})
    for offset in range(0, len(missing), 40):
        ids = missing[offset:offset + 40]
        query = urlencode(dict(action='wbgetentities', ids='|'.join(ids), props='claims', format='json', maxlag=5))
        request = Request(f'https://www.wikidata.org/w/api.php?{query}',
                          headers={'User-Agent': 'GuanlanHistoricalAtlas/1.0 (historical capital coordinate audit)'})
        with urlopen(request, timeout=25) as response:
            entities = json.load(response)['entities']
        for identifier in ids:
            claims = entities.get(identifier, {}).get('claims', {}).get('P625', [])
            values = [claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}) for claim in claims
                      if claim.get('rank') != 'deprecated']
            points = [[round(value['longitude'],5),round(value['latitude'],5)] for value in values
                      if value.get('globe','').endswith('/Q2') and 'longitude' in value and 'latitude' in value]
            if points and all(abs(p[0]-points[0][0])<0.1 and abs(p[1]-points[0][1])<0.1 for p in points):
                wikidata[identifier] = points[0]
            else:
                wikidata[identifier] = None
        coordinate_cache.write_text(json.dumps(wikidata, separators=(',', ':')), encoding='utf-8')
    print('Wikidata geographic coordinates:', sum(bool(point) for point in wikidata.values()), flush=True)

archive = {}
has_dated = []
for identifier in sorted(facts.keys() | curated['polities'].keys()):
    records = []
    manual = [r for r in curated['polities'].get(identifier,{}).get('facts',[]) if r['field']=='capital']
    rows = facts.get(identifier,{}).get('fields',{}).get('capital',[])
    matching_points = defaultdict(set)
    for row in rows:
        if row.get('rank') == 'deprecated':
            continue
        point = position(row['value'],row['label']) or wikidata.get(row['value'])
        if point:
            matching_points[row['label']].add(tuple(point))
    for row in manual:
        label = manual_names.get(row['value'],row['value'])
        matches = matching_points[label]
        point = position(None,label) or (next(iter(matches)) if len(matches)==1 else None)
        records.append(['应天府' if row['value']=='应天府（南京）' else label,point,row.get('from'),row.get('to'),row.get('at'),True])
    dated = any(any(r.get(k) is not None for k in ('from','to','at')) for r in [*manual,*rows])
    if dated:
        has_dated.append(identifier)
    for row in rows:
        if row.get('rank')=='deprecated':
            continue
        label = row['label']
        point = position(row['value'],label) or wikidata.get(row['value'])
        records.append([label,point,row.get('from'),row.get('to'),row.get('at'),False])
    if records:
        archive[identifier]=records

# Source-backed phases supersede composite capital descriptions for the matching years.
def period(identifier, label, point, start, end, source, polity=None, federation=None):
    archive.setdefault(identifier, []).insert(0, [label, point, start, end, None, True, source, polity, federation])
    if identifier not in has_dated:
        has_dated.append(identifier)

# Administrative seats are split at documented moves, including temporary moves.
westminster = (-0.1276,51.4995)
winchester = (-1.308,51.061)
early_england = 'https://www.parliament.uk/about/living-heritage/building/palace/estatehistory/the-middle-ages/palace-normans/'
english_administration = 'https://www.parliament.uk/about/living-heritage/building/palace/westminsterhall/government-and-administration/centre-of-admin/'
for identifier in ('Q105313','Q179876'):
    period(identifier, '温切斯特', winchester, 871, 1065, early_england)
for identifier in ('Q179876','Q200485'):
    period(identifier, '伦敦·威斯敏斯特', westminster, 1066, 1198, early_england)
for identifier in ('Q179876','Q330362','Q161885','Q174193','Q145'):
    period(identifier, '伦敦', westminster, 1199, None, english_administration)

period('Q538677','伦敦·威斯敏斯特（英格兰行政中心）',westminster,1199,1216,english_administration)

paris = (2.35299,48.85809)
versailles = (2.1269,48.8049)
versailles_history = 'https://en.chateauversailles.fr/discover/history'
versailles_return = 'https://www.chateauversailles.fr/decouvrir/histoire/grandes-dates/retour-cour-versailles'
for label, point, first, last, source in (
    ('巴黎',paris,990,1417,'https://archives.paris.fr/offre-culturelle/expositions-virtuelles/un-palais-de-justice-pour-paris/aux-origines-du-palais-de-la-cite'),
    ('布尔日',(2.398,47.081),1418,1435,'https://www.culture.gouv.fr/content/download/123075/file/Bourges%20renaissance.pdf'),
    ('巴黎',paris,1436,1681,'https://rdf.archives-nationales.culture.gouv.fr/garance/entities/agent/051926/?lang=en'),
    ('凡尔赛',versailles,1682,1714,versailles_history),
    ('巴黎',paris,1715,1721,versailles_return),
    ('凡尔赛',versailles,1722,1788,versailles_return),
    ('巴黎',paris,1789,1792,versailles_history),
):
    period('Q70972',label,point,first,last,source)
for identifier, first, last in (
    ('Q58296',1792,1795),('Q219817',1795,1799),('Q877619',1799,1804),
    ('Q71084',1804,1815),('Q58326',1848,1852),('Q71092',1852,1870),
    ('Q70802',1870,1939),('Q69829',1946,1958),('Q142',1944,None),
):
    period(identifier,'巴黎',paris,first,last,versailles_history)
period('Q207162','巴黎',paris,1814,1847,'https://www.carnavalet.paris.fr/en/le-nouveau-parcours')
period('Q69829','巴黎',paris,1945,1945,'https://www.cheminsdememoire.gouv.fr/fr/revue/le-retour-la-republique')
period('Q69808','维希',(3.426,46.124),1940,1944,'https://www.cheminsdememoire.gouv.fr/en/node/436')

moscow = (37.6173,55.7558)
petersburg = (30.33,59.94)
russian_capital = 'https://encspb.ru/object/2804019776?lc=en'
for identifier in ('Q186096','Q34266'):
    period(identifier,'圣彼得堡',petersburg,1712,1727,russian_capital)
period('Q34266','莫斯科',moscow,1728,1731,russian_capital)
period('Q34266','圣彼得堡',petersburg,1732,1913,russian_capital)
period('Q139319','彼得格勒',petersburg,1917,1917,russian_capital)
for identifier in ('Q2305208','Q236036','Q15180','Q159'):
    period(identifier,'莫斯科',moscow,1918,None,russian_capital)

brazil_capitals = 'https://www.senado.gov.br/noticias/especiais/brasilia50anos/not02.asp'
for identifier in ('Q217230','Q155'):
    period(identifier,'里约热内卢',(-43.1729,-22.9068),1822,1959,brazil_capitals)
period('Q155','巴西利亚',(-47.8828,-15.7942),1960,None,brazil_capitals)
period('Q713750','波恩',(7.0982,50.7374),1949,1990,
       'https://www.bundestag.de/en/parliament/history/history-197590')

period('Q467627', '坎大哈', (65.69495,31.61002), 1747, 1774,
       'https://www.iranicaonline.org/articles/kandahar-from-the-mongol-invasion-through-the-safavid-era/')
period('Q467627', '喀布尔', (69.18131,34.51864), 1775, 1823,
       'https://www.iranicaonline.org/articles/kabul-iii-history/')

byzantine_source = 'https://www.metmuseum.org/essays/byzantium-ca-330-1453'
archive['Q12544'] = []
period('Q12544', '君士坦丁堡', (28.978,41.008), 330, 1203, byzantine_source)
period('Q12544', '君士坦丁堡', (28.978,41.008), 1261, 1452, byzantine_source)
period('Q178897', '君士坦丁堡', (28.978,41.008), 1204, 1260, byzantine_source)
period('Q181254', '尼西亚', (29.72,40.43), 1204, 1260, byzantine_source)
ottoman_source = 'https://islamicart.museumwnf.org/exhibitions/ISL/the_ottomans/exhibition.php?theme=9'
# Galata is a city-centre landmark; use its position on coarse Bosporus outlines.
period('Q12560', '伊斯坦布尔', (28.97417,41.02556), 1453, 1922, ottoman_source)
period('Q34266', '彼得格勒', (30.33,59.94), 1914, 1917, 'https://encspb.ru/object/2804017592?lc=en')

safavid_source = 'https://www.metmuseum.org/zh/toah/ht/08/wai.html'
for identifier in ('Q161205','local:safavid-iran'):
    period(identifier, '大不里士', (46.2919,38.0800), 1501, 1554, safavid_source)
    period(identifier, '加兹温', (50.0049,36.2688), 1555, 1597, safavid_source)
    period(identifier, '伊斯法罕', (51.6746,32.6546), 1598, 1722, 'https://www.iranicaonline.org/articles/isfahan-vii-safavid-period/')

period('Q220594', '佩特拉', (35.4444,30.3286), -168, 105, 'https://whc.unesco.org/en/list/326/')
period('Q241790', '麦罗埃', (33.7483,16.9370), -200, 300, 'https://whc.unesco.org/en/list/1336/')
period('Q5724', '阿努拉德普勒', (80.3964,8.3500), -200, 992, 'https://whc.unesco.org/en/list/200/')
period('Q5406', '哈图沙', (34.6153,40.0197), -1600, -1200, 'https://whc.unesco.org/en/list/377/')
period('Q841364', '阿瑜陀耶', (100.5594,14.3472), 1351, 1767, 'https://whc.unesco.org/en/list/576/')

# Dated capitals for additional states and regional courts.
iranian_capitals = 'https://www.iranicaonline.org/articles/capital-cities/'
for identifier, label, point, first, last, source in [
    ('Q7462','东京·汴京',(114.35,34.80),960,1126,'https://en.chinaculture.org/library/2008-02/15/content_33444.htm'),
    ('Q7462','临安',(120.168,30.225),1138,1275,'https://www.grandcanalmuseum.cn/TemporaryandSpecialExhibitions/1153.html'),
    ('local:china-liao-dynasty','皇都',(119.38,43.95),918,937,'https://www.blzq.gov.cn/zjzq/lswh/202002/t20200229_1915634.html'),
    ('local:china-liao-dynasty','上京临潢府',(119.38,43.95),938,1120,'https://www.lingyuan.gov.cn/html/LYSZF/202311/0169961068163943.html'),
    ('local:japanese-imperial-court','平安京',(135.75,35.02),794,1184,'https://whc.unesco.org/en/list/688/'),
    ('local:japanese-imperial-court','京都',(135.75,35.02),1185,1867,'https://whc.unesco.org/en/list/688/'),
    ('Q878309','升龙',(105.839,21.038),1010,1225,'https://whc.unesco.org/en/list/1328/'),
    ('Q10800789','东京（升龙）',(105.839,21.038),1428,1526,'https://whc.unesco.org/en/decisions/4001'),
    ('Q6500483','顺化',(107.58,16.468),1802,1945,'https://whc.unesco.org/en/list/678/'),
    ('Q201705','耶输陀罗补罗（吴哥）',(103.86,13.435),889,920,'https://whc.unesco.org/document/153994'),
    ('Q201705','贡开',(104.54,13.78),928,943,'https://whc.unesco.org/archive/2023/whc23-45com-inf8B1-en.pdf'),
    ('Q201705','耶输陀罗补罗（吴哥）',(103.86,13.435),944,1430,'https://whc.unesco.org/document/153994'),
    ('Q167639','毗奢耶那伽罗（亨比）',(76.46,15.335),1336,1564,'https://whc.unesco.org/document/135115'),
    ('Q1986139','泰西封',(44.58,33.09),-100,223,'https://www.iranicaonline.org/articles/ctesiphon/'),
    ('Q12844800','加兹尼',(68.42,33.55),977,1150,iranian_capitals),
    ('local:buyid-state','设拉子（法尔斯）',(52.54,29.61),934,1062,iranian_capitals),
    ('local:buyid-state','雷伊（吉巴勒）',(51.44,35.59),935,1028,iranian_capitals),
    ('local:buyid-state','巴格达（伊拉克）',(44.37,33.31),945,1054,iranian_capitals),
    ('local:qajar-iran','德黑兰',(51.39,35.69),1786,1925,iranian_capitals),
    ('Q139377','阿克苏姆',(38.72,14.13),100,600,'https://archeologie.culture.gouv.fr/en/kingdom-aksum'),
    ('local:kingdom-of-kongo','姆班扎刚果',(14.24,-6.27),1400,1800,'https://whc.unesco.org/en/list/1511/'),
    ('Q752662','突尼斯',(10.172,36.799),1229,1573,'https://whc.unesco.org/en/list/36'),
    ('Q230791','爱丁堡',(-3.20,55.95),1452,1707,'https://www.pkc.gov.uk/media/14401/City-Status-Bid-document/pdf/City_Status_Bid_document.pdf'),
]:
    period(identifier,label,point,first,last,source)

madrid_source = 'https://www.madrid.es/UnidadesDescentralizadas/EducacionyJuventud/ActividadesEducativasComplementarias/MadridUnLibroAbierto/BibliotecaDigital/Capitulos/ficheros/H14MadridDeLosAustriasIngles.pdf'
for label, point, first, last in [('马德里',(-3.704,40.417),1561,1600),('巴利亚多利德',(-4.728,41.652),1601,1605),('马德里',(-3.704,40.417),1606,1808)]:
    for identifier, polity in [('Q80702','Spanish Empire'),('Q29','Kingdom of Spain'),('Q377350','Iberian Union')]:
        period(identifier,label,point,first,last,madrid_source,polity)

india_source = 'https://ndmc.gov.in/ndmc/history.aspx'
period('local:company-india','加尔各答',(88.35,22.57),1772,1858,india_source)
period('Q129286','加尔各答',(88.35,22.57),1858,1911,india_source)
period('Q129286','德里',(77.23,28.66),1912,1930,india_source)
period('Q129286','新德里',(77.21,28.61),1931,1947,india_source)

# Older temporal shards link this polity to the foreign-relations article.
for label, point, first, last, _, _, source, *_ in archive['Q12544']:
    period('Q112039853',label,point,first,last,source,'Byzantine Empire')

# Distinguish seats of itinerant courts from formally fixed capitals.
castilian_court = 'https://uvadoc.uva.es/bitstream/10324/73679/1/Carlos%20Belloso_La%20Corte%20en%20Valladolid_texto_portadas_UEMC_2022_com.pdf'
period('Q217196','巴利亚多利德（王廷驻地之一）',(-4.724,41.652),1230,1516,castilian_court)
period('Q29','托莱多（王廷驻地）',(-4.024,39.858),1520,1560,'https://marpa.madrid/fondos/madrid-y-la-corte','Kingdom of Spain')
period('Q29','马德里',(-3.704,40.417),1809,None,'https://iuu.uva.es/wp-content/uploads/2023/07/Catedra_Guia-Palacio-Real.pdf','Kingdom of Spain')
republic_valencia = 'https://www.valencia.es/es/-/valencia-memoria.-edificio-de-l-ajuntament'
period('Q178038','马德里',(-3.704,40.417),1931,1935,republic_valencia)
period('Q178038','巴伦西亚',(-0.376,39.470),1936,1937,republic_valencia)
period('Q178038','巴塞罗那',(2.177,41.385),1938,1938,
       'https://pares.cultura.gob.es/ParesBusquedas20/catalogo/description/1577606')

vienna = (16.366,48.207)
hofburg = 'https://www.burghauptmannschaft.at/Themen/Hofburg-Wien/Geschichte-der-Hofburg-Wien.html'
period('local:austrian-hereditary-lands','维也纳',vienna,1278,1805,hofburg)
period('Q131964','维也纳',vienna,1804,1867,hofburg)
dual_monarchy = 'https://www.parlament.gv.at/verstehen/historisches/1848-1918/index.html'
period('Q28513','维也纳',vienna,1867,1918,dual_monarchy)
period('Q28513','布达佩斯（匈牙利政府所在地）',(19.049,47.507),1867,1918,dual_monarchy)
period('Q40','维也纳',vienna,1918,None,hofburg)

electors = 'https://www.berlin.de/en/history/8477039-8619314-the-electors-residence.en.html'
period('Q148499','哈弗尔河畔勃兰登堡（早期统治中心）',(12.553,52.416),1157,1485,
       'https://www.politische-bildung-brandenburg.de/themen/die-entstehung-der-mark')
period('Q148499','柏林—科隆城（施普雷河畔）',(13.403,52.517),1486,1618,electors)
period('Q157367','柏林—科隆城（选侯驻地）',(13.403,52.517),1618,1701,electors)

# Some 1360s map frames still omit Edirne; retain Bursa as a separately documented seat.
period('Q12560','布尔萨',(29.06,40.183),1326,1364,'https://bursa.ktb.gov.tr/TR-70230/tarihce.html')
period('Q12560','埃迪尔内',(26.556,41.678),1365,1452,'https://kulturportali.gov.tr/turkiye/Edirne/genelbilgiler')
period('Q12560','布尔萨（旧都）',(29.06,40.183),1365,1374,'https://bursa.ktb.gov.tr/TR-70230/tarihce.html')

# The duchy's seat and the kingdom's royal capital belonged to different phases.
prussia_archive = 'https://gsta.preussischer-kulturbesitz.de/recherche/thematischer-wegweiser/preussen-herzogtum-1525-1701.html'
berlin_history = 'https://www.berlin.de/en/history/8477225-8619314-the-royal-capital.en.html'
prussian_exile = 'https://www.w3ltfrieden.de/en/frieden/wie-kriege-endeten/frieden-von-tilsit'
period('Q153091','柯尼斯堡',(20.5093,54.7115),1525,1700,prussia_archive)
period('Q27306','柏林',(13.403,52.517),1701,1806,berlin_history)
period('Q27306','梅梅尔（临时王廷）',(21.134,55.709),1807,1807,prussian_exile)
period('Q27306','柯尼斯堡（临时王廷）',(20.5093,54.7115),1808,1808,
       'https://de.wikisource.org/wiki/ADB%3ALuise_%28K%C3%B6nigin_von_Preu%C3%9Fen%29')
period('Q27306','柏林',(13.403,52.517),1809,1814,berlin_history)
period('Q27306','柏林',(13.403,52.517),1815,1866,
       'https://germanhistorydocs.org/en/from-vormaerz-to-prussian-dominance-1815-1866/german-federal-act-june-8-1815',
       federation='German Confederation')
period('Q27306','柏林',(13.403,52.517),1867,1918,berlin_history)

danish_capital = 'https://um.dk/media/cwdbrn3o/uk-copenhagen.pdf'
period('Q756617','罗斯基勒（王室中心）',(12.080,55.642),1000,1442,danish_capital)
period('Q756617','哥本哈根',(12.578,55.682),1443,1814,danish_capital)

stockholm = (18.0716,59.3268)
period('Q34','斯德哥尔摩（王室据点）',stockholm,1252,1396,
       'https://www.royalpalaces.se/english/royal-palaces-and-sites/the-royal-palace/history.html')
for identifier in ('Q34','Q215443'):
    period(identifier,'斯德哥尔摩（王室驻地）',stockholm,1523,1633,
           'https://www.kungahuset.se/english/royal-palaces-and-residences')
for identifier in ('Q34','Q215443'):
    period(identifier,'斯德哥尔摩',stockholm,1634,None,
           'https://www.riksbank.se/globalassets/media/forskning/monetar-statistik/volym-3/riksbanken_iii_ch6.pdf')

oslo = (10.736,59.907)
oslo_history = 'https://www.oslo.kommune.no/get-file/762788/2350e49bc5bf25140454bf101e18adc3564aeedf3bed6524e7a5849975c5e006'
for label, point, first, last, source in [
    ('尼达罗斯（王室中心）',(10.396,63.427),997,1216,'https://visittrondheim.no/en/about/trondheim/the-history-of-trondheim/'),
    ('卑尔根（王室驻地）',(5.319,60.399),1217,1298,'https://www.forsvarshistoriskmuseum.no/bergenhus-festning/en'),
    ('奥斯陆（王室驻地）',oslo,1299,1396,'https://www.forsvarsbygg.no/en/festningene/akershus-fortress'),
    ('奥斯陆（挪威行政中心）',oslo,1397,1623,'https://www.forsvarshistoriskmuseum.no/historien-om-akershus-festning'),
    ('克里斯蒂安尼亚（挪威行政中心）',oslo,1624,1813,oslo_history),
    ('克里斯蒂安尼亚',oslo,1814,1896,oslo_history),
    ('克里斯蒂亚尼亚',oslo,1897,1924,oslo_history),
    ('奥斯陆',oslo,1925,None,oslo_history),
]:
    period('Q20',label,point,first,last,source)

polish_court = 'https://www.zamek-krolewski.pl/en/strona/1221-brief-history'
period('Q172107','克拉科夫',(19.935,50.054),1569,1595,polish_court)
period('Q172107','华沙（王廷与政府驻地）',(21.014,52.248),1596,1795,polish_court)

dublin = (-6.267,53.343)
dublin_castle = 'https://heritageireland.ie/places-to-visit/dublin-castle/'
period('local:lordship-of-ireland','都柏林',dublin,1204,1541,dublin_castle)
period('local:kingdom-of-ireland','都柏林',dublin,1542,1800,dublin_castle)
period('local:gaelic-irish-kingdoms','卡舍尔（芒斯特王室据点）',(-7.890,52.520),978,1100,
       'https://heritageireland.ie/places-to-visit/the-rock-of-cashel/')
period('local:gaelic-irish-lordships','邓甘嫩（蒂龙奥尼尔家族据点）',(-6.767,54.506),1318,1607,
       'https://www.qub.ac.uk/sites/communityarchaeology/PDFFileStore/Filetoupload%2C181157%2Cen.pdf')

period('Q1407718','基尔肯尼',(-7.249,52.650),1642,1649,
       'https://ourplan.kilkenny.ie/archive/sites/default/files/masterplan/Section%202.pdf')

mughal_moves = 'https://scalar.usc.edu/works/plastic-sheets-for-industrial-use/the-mughal-capital-under-akbar.1'
for label, point, first, last, source in [
    ('阿格拉',(78.02,27.18),1556,1570,mughal_moves),
    ('法泰赫普尔西格里',(77.66,27.09),1571,1584,'https://whc.unesco.org/en/list/255'),
    ('拉合尔',(74.31,31.59),1585,1597,mughal_moves),
    ('阿格拉',(78.02,27.18),1598,1647,mughal_moves),
    ('沙贾汗纳巴德（德里）',(77.24,28.655),1648,1657,'https://whc.unesco.org/archive/advisory_body_evaluation/231rev.pdf'),
]:
    period('Q33296',label,point,first,last,source)
period('Q146871','德拉伊耶',(46.57,24.73),1744,1818,'https://whc.unesco.org/en/list/1329')

konbaung = 'https://www.jcic-heritage.jp/wp-content/uploads/2022/12/2012Report_Myanmar_eg.pdf'
for label, point, first, last in [
    ('阿马拉布拉',(96.06,21.90),1783,1820),
    ('阿瓦',(95.98,21.84),1821,1841),
    ('阿马拉布拉',(96.06,21.90),1842,1858),
    ('曼德勒',(96.10,21.99),1859,1885),
]:
    period('Q1062422',label,point,first,last,konbaung)

# South African government lists separate administrative, legislative and judicial seats.
south_africa_roles = {'比勒陀利亚':'行政首都','开普敦':'立法首都','布隆方丹':'司法首都'}
archive['Q258'] += [
    [f'{label}（{south_africa_roles[label]}）', point, 2024, None, None, True]
    for label, point, *_ in archive['Q258']
    if label in south_africa_roles and point
]

# Dated seats of the maritime republics and the Baltic orders.
period('Q4948', '威尼斯', (12.3403,45.4337), 1200,1797,
       'https://whc.unesco.org/en/list/394/')
period('Q174306', '热那亚', (8.933,44.410), 1339,1797,
       'https://www.lombardiabeniculturali.it/istituzioni/cronologie/cariche/2/')
period('Q48189', '马林堡', (19.028,54.040), 1309,1456,
       'https://whc.unesco.org/en/list/847/')
period('Q48189', '柯尼斯堡', (20.510,54.710), 1457,1525,
       'https://teutonicorder.org/hochmeisters')
period('Q1064825', '里加（大主教驻地）', (24.105,56.949), 1435,1561,
       'https://lnvm.gov.lv/rigas-pils/rigas-pils-vesture/')
period('Q1064825', '文登（骑士团团长驻地）', (25.271,57.313), 1481,1561,
       'https://visit.cesis.lv/en/place/cesis-old-town/')
period('Q1136188', '马拉喀什', (-7.989,31.625), 1524,1603,
       'https://csuohio.elsevierpure.com/en/publications/sharifian-rule-in-morocco-sixteenth-to-eighteenth-centuries/')

papal_rome = 'https://www.britannica.com/place/Papal-States'
period('Q170174','罗马',(12.496,41.903),756,1308,papal_rome)
period('Q170174','罗马（教皇国行政中心）',(12.496,41.903),1309,1376,papal_rome)
period('Q170174','阿维尼翁（教廷驻地）',(4.805,43.951),1309,1376,
       'https://whc.unesco.org/en/list/228/')
period('Q170174','罗马',(12.496,41.903),1377,1870,papal_rome)
period('Q13107370','贝尔格莱德',(20.458,44.817),1841,1882,'https://www.britannica.com/place/Belgrade')
period('Q241748','贝尔格莱德',(20.458,44.817),1882,1918,'https://www.britannica.com/place/Belgrade')
modern = {}
shard = read('public/data/temporal/20.geojson')['features']
admin_centers = [f for f in cities if f['properties'].get('ADM0CAP')==1]
for feature in shard:
    p=feature['properties']
    if not p['validFrom']<=2024<=p['validTo'] or p.get('controlArea'):
        continue
    polity=shape(feature['geometry'])
    candidates=[f for f in admin_centers if polity.covers(Point(f['geometry']['coordinates']))]
    named=[f for f in candidates if f['properties']['ADM0NAME'] in (p['NAME'],p.get('wikipedia'))]
    if len(named)==1 or (not named and len(candidates)==1):
        city=(named or candidates)[0]
        label=city['properties'].get('NAME_ZH') or city['properties']['NAME']
        modern[p['NAME']]=[label,[round(x,5) for x in city['geometry']['coordinates']]]

supplement = read('public/data/reviewed-capital-seats.json')
for rows in archive.values():
    for row in rows:
        row[0] = supplement['translations'].get(row[0], row[0])

(ROOT/'public/data/map-capitals.json').write_text(json.dumps({
    'source':SOURCE,'archive':archive,'modern':modern,'hasDated':has_dated,
    'named':supplement['polities']
},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('Archived polities:',len(archive),'located records:',sum(bool(r[1]) for rows in archive.values() for r in rows),'modern map matches:',len(modern))



