"""Repair specific historical identities, reigns and overlapping Norway polygons."""
from territory_repair_stage import read, write, clean
from shapely.geometry import shape, mapping

TAG = 'western-and-southeast-asian-archive-review'
FACTS = 'public/data/polity-facts.json'
ROYAL = 'https://www.royal.uk/kings-and-queens-1066'
CNUT = 'https://www.royal.uk/canute-great-r-1016-1035'
FRANCE = 'https://www.assemblee-nationale.fr/13/presidence/histoire.asp'
GERMAN = 'https://germanhistorydocs.org/en/from-vormaerz-to-prussian-dominance-1815-1866/german-federal-act-june-8-1815'
SERBIA = 'https://www.britannica.com/place/Serbia/History'
data = read(FACTS)
entities = data['entities']


def add(q, name, a, b, source, role, kind=None):
    row = {'value':name,'label':name,'from':a,'to':b,'at':None,'citation':[source],
           'roleLabel':role,'supplement':TAG}
    if kind:
        row['kind'] = kind
    entities[q]['fields'].setdefault('ruler', []).append(row)


def chain(q, source, role, end, terms):
    rows = [(int(y),n) for y,n in (part.split(' ',1) for part in terms.split('|'))]
    for i,(start,name) in enumerate(rows):
        add(q,name,start,rows[i+1][0] if i+1<len(rows) else end,source,role)


def europe():
    chain('Q200485',ROYAL,'英格兰国王',1154,'1066 威廉一世|1087 威廉二世|1100 亨利一世|1135 斯蒂芬')
    entities['Q200485']['description']='1066年后由诺曼王室统治的英格兰王国。'
    add('Q3281269','克努特大帝',1018,1035,CNUT,'英格兰与丹麦国王；1028年起兼领挪威')
    add('Q3281269','哈德克努特',1035,1042,CNUT,'丹麦国王；1040年起兼领英格兰')
    add('Q3281269','哈罗德一世（飞毛腿）',1035,1040,CNUT,'英格兰摄政，1037年起为英格兰国王')
    burgundy='https://www.britannica.com/place/Burgundy-region-France/History'
    entities.setdefault('local:frankish-burgundy',{'label':'法兰克勃艮第王国','en':'Frankish Burgundy',
        'description':'勃艮第归入法兰克后形成的墨洛温王朝分国。国王可同时统治纽斯特里亚。','fields':{}})
    data['labels']['local:frankish-burgundy']='法兰克勃艮第王国'
    chain('local:frankish-burgundy',burgundy,'法兰克勃艮第的王室统治者',673,
          '561 贡特拉姆|592 希尔德贝尔特二世|595 提乌德里克二世|613 克洛泰尔二世|629 达戈贝尔特一世|639 克洛维二世|657 克洛泰尔三世')
    add('local:frankish-burgundy','巴蒂尔德',657,664,burgundy,'幼主克洛泰尔三世时期的摄政王太后')
    chain('Q13107370',SERBIA,'塞尔维亚大公',1882,'1815 米洛什·奥布雷诺维奇一世|1839 米兰·奥布雷诺维奇二世|1839 米哈伊洛·奥布雷诺维奇三世|1842 亚历山大·卡拉乔尔杰维奇|1858 米洛什·奥布雷诺维奇一世|1860 米哈伊洛·奥布雷诺维奇三世|1868 米兰·奥布雷诺维奇')
    add('Q13107370','卡拉乔尔杰',1804,1813,SERBIA,'第一次塞尔维亚起义领袖')
    chain('Q241748',SERBIA,'塞尔维亚国王',1918,'1882 米兰一世|1889 亚历山大一世|1903 彼得一世')
    for a,b in [(1815,1848),(1850,1866)]:
        add('Q151624','联邦议会（奥地利主持）',a,b,GERMAN,'成员国派遣代表组成，奥地利担任议会主席国','collective')
    add('Q151624','约翰大公',1848,1849,'https://www.bundestag.de/parlament/geschichte/parlamentarismus/1848','法兰克福国民议会选举的帝国摄政，任职于临时中央权力机构')
    entities['Q151624']['rulerScopeNote']='联邦议会由各邦代表组成。1848年起另有革命时期的临时中央权力机构，1850—1851年间恢复联邦议会。'
    rus='https://www.britannica.com/place/Russia/The-Muscovite-period'
    chain('Q186096',rus,'俄罗斯沙皇',1598,'1547 伊凡四世|1584 费奥多尔一世')
    chain('Q186096',rus,'俄罗斯沙皇（动乱时期）',1610,'1598 鲍里斯·戈杜诺夫|1605 费奥多尔二世|1605 伪德米特里一世|1606 瓦西里四世')
    chain('Q186096','https://www.britannica.com/topic/Romanov-dynasty','俄罗斯沙皇',1721,
          '1613 米哈伊尔·罗曼诺夫|1645 阿列克谢一世|1676 费奥多尔三世|1682 彼得一世')
    add('Q186096','伊凡五世',1682,1696,'https://www.britannica.com/biography/Peter-the-Great','与彼得一世共同在位')
    add('Q186096','索菲娅·阿列克谢耶芙娜',1682,1689,'https://www.britannica.com/biography/Peter-the-Great','摄政公主')
    add('Q58296','国民公会',1792,1795,FRANCE,'共和国的立法与最高政治权力机关','collective')
    add('Q58296','临时行政会议',1792,1794,'https://www2.assemblee-nationale.fr/15/evenements/2019/la-revolution-s-affiche/la-convention-septembre-1792-octobre-1795','由部长组成的集体行政机构','collective')
    add('Q58296','救国委员会',1793,1795,'https://www.britannica.com/topic/Committee-of-Public-Safety','国民公会设立的革命政府核心机构','collective')
    add('Q58296','马克西米连·罗伯斯庇尔',1793,1794,'https://www.britannica.com/biography/Maximilien-Robespierre','救国委员会成员')
    for q in ['Q58296','Q219817']:
        add(q,'五人督政府',1795,1799,'https://www.britannica.com/topic/Directory-French-history','依据共和三年宪法组成的集体行政机关','collective')
        add(q,'保罗·巴拉斯',1795,1799,'https://www.britannica.com/biography/Paul-Francois-Jean-Nicolas-vicomte-de-Barras','督政官')
        add(q,'拉扎尔·卡诺',1795,1797,'https://www.britannica.com/biography/Lazare-Carnot','督政官')
        add(q,'拿破仑·波拿巴',1799,1799,'https://www.assemblee-nationale.fr/dyn/histoire-et-patrimoine/consulat-et-premier-empire/consulat-centralisation-et-creation-du-corps-prefectoral','雾月政变后进入执政府，年底任第一执政')
    add('Q877619','拿破仑·波拿巴',1799,1804,'https://www.assemblee-nationale.fr/dyn/histoire-et-patrimoine/consulat-et-premier-empire/consulat-centralisation-et-creation-du-corps-prefectoral','第一执政')
    add('Q958291','亚历山德鲁·扬·库扎',1859,1866,'https://www.britannica.com/biography/Alexandru-Ioan-Cuza','摩尔达维亚与瓦拉几亚联合公国君主')
    add('Q958291','卡罗尔一世',1866,1881,'https://www.britannica.com/biography/Carol-I','联合公国／罗马尼亚大公')
    for q, name, a, b, url in [
        ('Q10957559','斯特凡三世',1457,1504,'https://www.britannica.com/biography/Stephen-Moldovan-ruler'),
        ('Q10957559','彼得·拉雷什',1527,1538,'https://www.britannica.com/place/Moldova/History'),
        ('Q10957559','彼得·拉雷什',1541,1546,'https://www.britannica.com/place/Moldova/History'),
        ('Q10957559','迪米特里耶·坎泰米尔',1710,1711,'https://www.britannica.com/biography/Dimitrie-Cantemir'),
        ('Q171393','米尔恰一世',1386,1418,'https://www.britannica.com/place/Romania/History'),
        ('Q171393','弗拉德三世',1456,1462,'https://www.britannica.com/biography/Vlad-the-Impaler'),
        ('Q171393','米哈伊勇士',1593,1601,'https://www.britannica.com/biography/Michael-prince-of-Walachia'),
        ('Q171393','康斯坦丁·布兰科韦亚努',1688,1714,'https://www.britannica.com/place/Romania/History')]:
        add(q,name,a,b,url,'公国君主')

def mediterranean_and_asia():
    naples='https://www.treccani.it/enciclopedia/regno-di-napoli/'
    chain('Q173065',naples,'那不勒斯国王',1442,'1282 查理一世|1285 查理二世|1309 罗贝托|1343 然娜一世|1382 查理三世|1386 拉迪斯劳|1414 然娜二世|1435 勒内')
    chain('Q173065',naples,'那不勒斯国王',1501,'1442 阿方索一世|1458 费兰特一世|1494 阿方索二世|1495 费兰迪诺|1496 腓特烈')
    chain('Q173065',naples,'那不勒斯国王',1806,'1734 卡洛七世|1759 费迪南多四世')
    for q in ['Q173065','Q48779892']:
        chain(q,naples,'拿破仑时期的那不勒斯国王',1815,'1806 约瑟夫·波拿巴|1808 若阿尚·缪拉')
    add('Q173065','费迪南多四世',1815,1816,naples,'复位的那不勒斯国王')
    aragon='https://www.britannica.com/place/Aragon-region-Spain'
    chain('Q204920',aragon,'阿拉贡国王',1516,'1412 费尔南多一世|1416 阿方索五世|1458 胡安二世|1479 费尔南多二世')
    chain('Q148540','https://www.britannica.com/topic/Medici-family','美第奇家族实际执政者',1494,
          '1464 皮耶罗·德·美第奇|1469 洛伦佐·德·美第奇|1492 皮耶罗二世·德·美第奇')
    add('Q148540','吉罗拉莫·萨沃纳罗拉',1494,1498,'https://www.britannica.com/biography/Girolamo-Savonarola','共和改革的政治与宗教领袖')
    savoy='https://www.britannica.com/topic/House-of-Savoy'
    for q in ['Q1232887','Q426025']:
        chain(q,savoy,'萨伏伊公爵',1497,'1465 阿梅代奥九世|1472 菲利贝托一世|1482 卡洛一世|1490 卡洛·乔万尼·阿梅代奥|1496 菲利波二世')
        chain(q,savoy,'萨伏伊公爵',1630,'1553 埃马努埃莱·菲利贝托|1580 卡洛·埃马努埃莱一世')
    genoa='https://www.lombardiabeniculturali.it/istituzioni/cronologie/cariche/2/'
    add('Q174306','西蒙尼·博卡内格拉',1339,1344,genoa,'热那亚首任总督')
    add('Q174306','西蒙尼·博卡内格拉',1356,1363,genoa,'再任总督')
    add('Q174306','托马索·迪·坎波弗雷戈索',1437,1442,genoa,'热那亚总督')
    add('Q174306','安德烈亚·多里亚',1528,1560,'https://www.britannica.com/biography/Andrea-Doria','共和国政治主导者与海军统帅')
    chain('Q185682','https://en.wikipedia.org/wiki/List_of_governors-general_of_French_Indochina','法属印度支那总督',1945,
          '1887 欧内斯特·孔斯坦|1888 艾蒂安·里绍|1889 皮埃尔·皮基|1891 让-马里·德拉内桑|1894 莱昂·鲁梭|1897 保罗·杜美|1902 保罗·博|1908 安东尼·克洛布科夫斯基|1910 阿尔贝·萨罗|1914 若斯特·范·沃伦霍芬|1915 欧内斯特·鲁姆|1917 阿尔贝·萨罗|1919 莫里斯·隆|1923 马夏尔·梅兰|1925 亚历山大·瓦雷纳|1928 皮埃尔·帕斯基耶|1934 欧仁·勒内·罗班|1936 朱尔·布雷维耶|1939 乔治·卡特鲁|1940 让·德句')
    entities['Q185682']['rulerScopeNote']='总督任期采用年度显示，交接年可见多人。部分短期代理总督仍待补录。'
    vietnam='https://www.britannica.com/place/Vietnam/The-Nguyen-dynasty'
    chain('Q6500483',vietnam,'阮朝皇帝',1883,'1802 嘉隆帝（阮福映）|1820 明命帝|1841 绍治帝|1847 嗣德帝')
    add('Q6500483','保大帝',1926,1945,vietnam,'阮朝皇帝')
    add('Q841364','纳黎萱',1590,1605,'https://www.britannica.com/biography/Naresuan','阿瑜陀耶国王')
    add('Q841364','那莱',1656,1688,'https://www.britannica.com/biography/Narai','阿瑜陀耶国王')
    khmer='https://www.britannica.com/place/Cambodia/The-Khmer-state-Angkor'
    for q in ('Q201705','Q4919413'):
        add(q,'苏利耶跋摩二世',1113,1150,khmer,'高棉国王，任期末年约数')
        add(q,'阇耶跋摩七世',1181,1218,khmer,'高棉国王，任期末年约数')
    moldavia='https://lexikon.katolikus.hu/M/Moldva.html'
    add('Q10957559','亚历山德鲁一世（善人）',1400,1432,moldavia,'摩尔达维亚公国君主')
    add('Q10957559','斯特凡二世',1442,1447,moldavia,'摩尔达维亚公国君主，争位时期')
    add('Q10957559','佩特鲁·阿龙',1455,1457,moldavia,'摩尔达维亚公国君主，第三次在位')
    chain('Q10957559',moldavia,'摩尔达维亚公国君主',1527,'1504 博格丹三世|1517 斯特凡四世')
    add('Q10957559','亚历山德鲁·勒普什内亚努',1552,1561,moldavia,'摩尔达维亚公国君主')
    add('Q10957559','亚历山德鲁·勒普什内亚努',1564,1568,moldavia,'摩尔达维亚公国君主，再度在位')
    wallachia='https://en.wikipedia.org/wiki/List_of_princes_of_Wallachia'
    add('Q171393','弗拉德二世',1443,1447,wallachia,'瓦拉几亚公国君主，再度在位')
    add('Q171393','拉杜四世',1495,1508,wallachia,'瓦拉几亚公国君主')
    add('Q171393','尼亚戈埃·巴萨拉布',1512,1521,wallachia,'瓦拉几亚公国君主')
    add('Q204920','卡洛斯一世',1516,1556,'https://www.britannica.com/biography/Charles-V-Holy-Roman-emperor','阿拉贡国王，亦为神圣罗马帝国皇帝查理五世')
    add('Q204920','卡洛斯二世',1665,1700,'https://www.britannica.com/biography/Charles-II-king-of-Spain','西班牙君主，兼领阿拉贡')



    aceh='https://maa.bandaacehkota.go.id/profil/sejarah-aceh/'
    add('Q1061057','伊斯坎达尔·穆达',1607,1636,aceh,'亚齐苏丹')
    add('Q1061057','伊斯坎达尔·塔尼',1636,1641,aceh,'亚齐苏丹')
    add('Q402145','阿贡苏丹',1613,1645,'https://www.persee.fr/doc/arch_0044-8613_1998_num_56_1_3503','马打兰苏丹')
    add('Q424','安东',1848,1860,'https://library.ncdd.gov.kh/detail/11814/download','柬埔寨国王')
    add('Q424','诺罗敦',1860,1904,'https://cdn.angkordatabase.asia/libs/docs/Briggs-SketchCambodian-History-1947.pdf','柬埔寨国王，1864年加冕')

def repair_north_sea():
    from shapely.ops import unary_union
    path='public/data/temporal/10.geojson'
    shard=read(path)
    names={'Kingdom of Norway','North Sea Empire'}
    rows=[f for f in shard['features'] if f['properties']['NAME'] in names]
    if any(f['properties'].get('geometryCorrection')==TAG for f in rows):
        return
    norway=unary_union([clean(shape(f['geometry'])) for f in rows
        if f['properties']['NAME']=='Kingdom of Norway' and f['properties']['validFrom']<=1035<=f['properties']['validTo']])
    empire=unary_union([clean(shape(f['geometry'])) for f in rows
        if f['properties']['NAME']=='North Sea Empire' and 1028<=f['properties']['validFrom']<=1035])
    output=[]
    for f in shard['features']:
        p=f['properties']
        name=p['NAME']
        if name not in names or p['validFrom']>1039 or p['validTo']<1028:
            output.append(f)
            continue
        for a,b in [(p['validFrom'],min(1027,p['validTo'])),
                    (max(1028,p['validFrom']),min(1035,p['validTo'])),
                    (max(1036,p['validFrom']),p['validTo'])]:
            if a>b:
                continue
            props={**p,'validFrom':a,'validTo':b}
            geometry=f['geometry']
            if (name=='Kingdom of Norway' and 1028<=a<=1035) or (name=='North Sea Empire' and a>=1036):
                g=clean(shape(geometry)).difference(empire if name=='Kingdom of Norway' else norway)
                if g.is_empty:
                    continue
                geometry=mapping(clean(g))
                props.pop('labelPath',None)
                props.update(geometryCorrection=TAG,sourceUrl=CNUT)
                if name=='Kingdom of Norway':
                    props['suppressPolityLabel']=True
            output.append({**f,'geometry':geometry,'properties':props})
    shard['features']=output
    write(path,shard)


def update_temporal_index():
    index_path='public/data/temporal/index.json'
    index=read(index_path)
    index['changeYears']=sorted(set(index['changeYears'])|{1028,1036})
    index['counts']['polityRecords']=len({
        f['properties']['sourceRecord']
        for century in index['centuries']
        for f in read(f'public/data/temporal/{century}.geojson')['features']
    })
    write(index_path,index)


if __name__=='__main__':
    for e in entities.values():
        e['fields']['ruler']=[r for r in e['fields'].get('ruler',[]) if r.get('supplement')!=TAG]
    europe()
    mediterranean_and_asia()
    repair_north_sea()
    update_temporal_index()
    write(FACTS,data)
    print(sum(r.get('supplement')==TAG for e in entities.values() for r in e['fields']['ruler']))




