"""Review dated identities, archival evidence and historical population observations."""
import copy
from territory_repair_stage import ROOT, read, write, clean, label_path
from shapely import union_all
from shapely.geometry import mapping, shape

BUYID = 'https://www.iranicaonline.org/articles/buyids/'
FLAGS = 'https://www.iranicaonline.org/articles/flags-i/'
ABBASID = 'https://www.ucl.ac.uk/museums-static/digitalegypt/chronology/islamic.html'
MONGOL = 'https://www.iranicaonline.org/articles/il-khanids-i-dynastic-history/'
HAITI = 'https://www.haiti-reference.info/pages/plan/politique/pouvoir-executif/presidents/'
HAITI_SPLIT = 'https://www.marines.mil/Portals/1/Publications/Dominican%20Republic%20and%20Haiti%20Study_2.pdf'
BULGARIA = 'https://archontology.org/nations/bulgaria/00_1908_1946_s.php'
HUNGARY_REVOLUTION = 'https://mnm.hu/en/en/exhibitions/history-hungary-part-ii/1848-49-revolution-and-war-independence'
HUNGARY_SURRENDER = 'https://oktober6.kormany.hu/tortenelmi-kronologia'
BAHRAIN = 'https://culture.gov.bh/en/eservices/BahrainHistoryTimeline/'
POLISH_SUCCESSION = 'https://mnk.pl/en/wystawy/stanislaw-leszczynski-i-august-ii-wettin/'
TAG = 'caliphates-successions-2026-11-03'


def relabel(feature, start, end, name, qid, label, source, note):
    row = copy.deepcopy(feature)
    properties = row['properties']
    properties.update(
        NAME=name, SUBJECTO=name, qid=qid, entityId=qid, displayName=label,
        validFrom=start, validTo=end, sourceUrl=source, accuracy=note,
        sourceName=properties.get('sourceName', properties['NAME']),
        sourceQid=properties.get('sourceQid', properties.get('qid')),
        sourceRecord=f"{properties['sourceRecord']}:{TAG}:{start}",
        identityCorrection=note,
    )
    return row


def combine(rows, template):
    geometry = clean(union_all([shape(row['geometry']) for row in rows]))
    template['geometry'] = mapping(geometry)
    template['properties']['labelPath'] = label_path(geometry, template['properties']['displayName'])
    return template


def revise_shards():
    for century in [9, 10, 12, 17, 18, 19, 20]:
        path = f'public/data/temporal/{century}.geojson'
        data = read(path)
        output, buyids = [], []
        late_abbasid = None
        haiti = {}
        hungarian_revolt = None
        polish_factions = {}
        for row in data['features']:
            p = row['properties']
            name, start, end = p['NAME'], p['validFrom'], p['validTo']
            if name == 'Pro-Swedish Poland':
                polish_factions[start,end] = row
            elif name in {'Buyid Dynasty', 'Abbasid Caliphate/Buyid Dynasty'}:
                buyids.append(row)
            elif name == 'Kingdom of Bahrain' and end <= 2001:
                # The contemporaneous State of Bahrain record covers these islands.
                continue
            elif name == 'Hungarian Nationalists' and start == 1849 and end == 1852:
                hungarian_revolt = row
                note = '1849年匈牙利革命政府的控制范围示意。主要革命军于同年8月投降，残余抵抗于秋季结束。'
                output.append(combine([row], relabel(row, 1849, 1849, name, 'local:hungarian-revolution', '匈牙利革命政府', HUNGARY_REVOLUTION, note)))
            elif name == 'Principality of Bulgaria' and end >= 1908:
                if start < 1908:
                    before = copy.deepcopy(row)
                    before['properties']['validTo'] = 1907
                    output.append(before)
                successor = relabel(row, max(start, 1908), end, 'Kingdom of Bulgaria', 'Q147909', '保加利亚王国', BULGARIA, '1908年宣布独立并改称王国，沿用原时期轮廓。')
                for key in ['sovereignName', 'sovereignQid', 'territoryType']:
                    successor['properties'].pop(key, None)
                output.append(successor)
            elif name == 'Abbasid Caliphate' and end == 1259:
                late_abbasid = row
                output.append(relabel(row, start, 1258, name, 'Q12536', '阿拔斯哈里发国', MONGOL, '1258年巴格达陷落，年度档案保留年内末代哈里发。'))
            elif name == 'Empire of Haiti' and end > 1806:
                periods = [
                    (1804, 1806, name, 'Q2006756', '海地第一帝国'),
                    (1807, 1819, 'Divided Haiti', 'local:haiti-divided', '海地南北政权'),
                    (1820, 1848, 'Republic of Haiti', 'Q790', '海地共和国'),
                    (1849, 1858, 'Second Empire of Haiti', 'local:haiti-second-empire', '海地第二帝国'),
                    (1859, 1915, 'Republic of Haiti', 'Q790', '海地共和国'),
                ]
                for first, last, target, qid, label in periods:
                    lo, hi = max(start, first), min(end, last)
                    if lo > hi or lo >= (century + 1) * 100 or hi < century * 100:
                        continue
                    note = '原轮廓为南北政权的合计分布。北方克里斯托夫于1811年称王，南方维持共和政府。' if target == 'Divided Haiti' else '按海地政府更替切换档案身份，沿用来源轮廓。'
                    updated = relabel(row, lo, hi, target, qid, label, HAITI_SPLIT if target == 'Divided Haiti' else HAITI, note)
                    if target == 'Divided Haiti':
                        updated['properties'].update(regionalCollection=True, representationNote=note)
                    haiti.setdefault((lo, hi, target), []).append(updated)
            else:
                output.append(row)

        for (start,end), faction in polish_factions.items():
            index, commonwealth = next(
                (i,row) for i,row in enumerate(output)
                if row['properties']['NAME'] == 'Polish-Lithuanian Commonwealth'
                and row['properties']['validFrom'] == start and row['properties']['validTo'] == end
            )
            note = '大北方战争期间，共和国内出现由瑞典支持的斯坦尼斯瓦夫一世与奥古斯特二世的王位争夺。1709年波尔塔瓦战役后，奥古斯特二世复位。'
            combined = relabel(commonwealth,start,end,'Polish-Lithuanian Commonwealth','Q172107',
                               '波兰立陶宛联邦',POLISH_SUCCESSION,note)
            combined['properties']['representationNote'] = note
            output[index] = combine([commonwealth,faction],combined)
        if hungarian_revolt:
            austria = next(row for row in output if row['properties']['NAME'] == 'Austrian Empire'
                           and row['properties']['validFrom'] == 1849 and row['properties']['validTo'] == 1852)
            restored = relabel(austria, 1850, 1852, 'Austrian Empire', 'Q131964', '奥地利帝国',
                               HUNGARY_SURRENDER, '1849年匈牙利革命被镇压。1850年起合并原来被错误延长的革命政府轮廓。')
            austria['properties']['validTo'] = 1849
            output.append(combine([austria, hungarian_revolt], restored))
        for rows in haiti.values():
            output.append(combine(rows, rows[0]) if len(rows) > 1 else rows[0])
        if buyids:
            stops = sorted({year for row in buyids for year in (row['properties']['validFrom'], row['properties']['validTo'] + 1)})
            for lo, end in zip(stops, stops[1:]):
                group = [row for row in buyids if row['properties']['validFrom'] <= lo <= row['properties']['validTo']]
                if group and lo < (century + 1) * 100 and end > century * 100:
                    # Preserve already reviewed records on repeat runs.
                    if len(group) == 1 and group[0]['properties']['qid'] == 'local:buyid-state':
                        output.append(group[0])
                        continue
                    reviewed = relabel(group[0], lo, end - 1, 'Buyid Dynasty', 'local:buyid-state', '布韦希王朝', BUYID, '合并原图中的布韦希控制范围。巴格达的阿拔斯哈里发与布韦希埃米尔分别记载。')
                    output.append(combine(group, reviewed))
        if late_abbasid:
            for i, row in enumerate(output):
                p = row['properties']
                if p['NAME'] == 'Mongol Empire' and p['validFrom'] <= 1259 <= p['validTo']:
                    early = copy.deepcopy(row)
                    early['properties']['validTo'] = 1258
                    output[i] = early
                    successor = relabel(row, 1259, 1259, 'Mongol Empire', p['qid'], p['displayName'], MONGOL, '巴格达于1258年被旭烈兀攻占。1259年沿用蒙军控制的年度代表范围。')
                    output.append(combine([row, late_abbasid], successor))
                    break
        data['features'] = [
            row for row in output
            if row['properties']['validFrom'] < (century + 1) * 100
            and row['properties']['validTo'] >= century * 100
        ]
        write(path, data)


def revise_archives():
    facts = read('public/data/polity-facts.json')
    entities = facts['entities']
    entities.setdefault('local:buyid-state', dict(label='布韦希王朝', en='Buyid Dynasty', description='以法尔斯、吉巴勒和伊拉克为主要支系的埃米尔政权。', fields={}))
    entities.setdefault('local:haiti-divided', dict(label='海地南北政权', en='Divided Haiti', description='海地北方与南方政权并立时期。', fields={}))
    entities.setdefault('local:haiti-second-empire', dict(label='海地第二帝国', en='Second Empire of Haiti', description='福斯坦一世统治时期。', fields={}))
    entities.setdefault('Q147909', dict(label='保加利亚王国', en='Kingdom of Bulgaria', description='1908年至1946年的保加利亚君主国。', fields={}))
    for entity in entities.values():
        for field in ['ruler', 'imperialSovereign']:
            if field in entity['fields']:
                entity['fields'][field] = [row for row in entity['fields'][field] if row.get('supplement') != TAG]
    entities['Q12536']['fields']['ruler'] = []
    entities.setdefault('local:hungarian-revolution', dict(label='匈牙利革命政府', en='Hungarian Revolutionary Government',
        description='1849年宣布独立的匈牙利革命政府。', fields={}))

    def terms(country, source, role, rows, field='ruler'):
        for slug, label, start, end in rows:
            person = slug if slug.startswith('Q') else f'local:person-{slug}'
            row = {'value':person, 'label':label, 'from':start, 'to':end, 'at':None,
                   'roleLabel':role, 'citation':[source], 'supplement':TAG}
            entities[country]['fields'].setdefault(field, []).append(row)
            facts['labels'][person] = label

    if facts['labels'].get('Q16912') == '拉约什·科苏特':
        facts['labels'].pop('Q16912')
    terms('local:hungarian-revolution', HUNGARY_REVOLUTION, '摄政总统', [
        ('Q157040','科苏特·拉约什',1849,1849),
    ])
    sheikhdom = entities['local:bahrain-sheikhdom']['fields']
    for field in ('ruler', 'headOfGovernment'):
        if field in sheikhdom:
            sheikhdom[field] = [row for row in sheikhdom[field] if (row.get('from') or 0) < 1971]
    terms('local:bahrain-sheikhdom', BAHRAIN, '巴林统治者', [
        ('isa-bin-ali','伊萨·本·阿里·阿勒哈利法',1869,1932),
        ('hamad-bin-isa-1872','哈马德·本·伊萨·阿勒哈利法',1932,1942),
    ])
    terms('Q398', BAHRAIN, '巴林埃米尔', [
        ('Q309650','伊萨·本·萨勒曼·阿勒哈利法',1971,1999),
    ])

    names = [
        ('saffah','萨法赫',750), ('mansur','曼苏尔',754), ('mahdi','马赫迪',775),
        ('hadi','哈迪',785), ('harun','哈伦·拉希德',786), ('amin','阿明',809),
        ('mamun','马蒙',813), ('mutasim','穆阿台绥姆',833), ('wathiq','瓦西格',842),
        ('mutawakkil','穆塔瓦基勒',847), ('muntasir','蒙塔西尔',861),
        ('mustain','穆斯塔因',862), ('mutazz','穆塔兹',866), ('muhtadi','穆赫塔迪',869),
        ('mutamid','穆塔米德',870), ('mutadid','穆塔迪德',892), ('muktafi','穆克塔菲',902),
        ('muqtadir','穆格台迪尔',908), ('qahir','卡希尔',932), ('radi','拉迪',934),
        ('muttaqi','穆塔基',940), ('mustakfi','穆斯塔克菲',944), ('muti','穆提',946),
        ('tai','塔伊',974), ('qadir','卡迪尔',991), ('qaim','卡伊姆',1031),
        ('muqtadi','穆格塔迪',1075), ('mustazhir','穆斯塔齐尔',1094),
        ('mustarshid','穆斯塔尔希德',1118), ('rashid','拉希德',1135),
        ('muqtafi','穆格塔菲',1136), ('mustanjid','穆斯坦吉德',1160),
        ('mustadi','穆斯塔迪',1170), ('nasir','纳西尔',1180), ('zahir','扎希尔',1225),
        ('mustansir','穆斯坦西尔',1226), ('mustasim','穆斯塔辛',1242),
    ]
    terms('Q12536', ABBASID, '阿拔斯哈里发', [
        ('abbasid-'+slug, label, start, names[i+1][2] if i+1 < len(names) else 1258)
        for i,(slug,label,start) in enumerate(names)
    ])
    # Retain the already identified founder portrait.
    entities['Q12536']['fields']['ruler'][0]['value'] = 'Q252087'
    terms('local:buyid-state', BUYID, '伊拉克支系埃米尔', [
        ('muizz','穆伊兹·道莱',945,967), ('bakhtiyar','伊兹·道莱·巴赫蒂亚尔',967,978),
        ('adud','阿杜德·道莱',978,983), ('samsam','萨姆萨姆·道莱',983,987),
        ('sharaf','沙拉夫·道莱',987,989), ('baha','巴哈·道莱',989,1012),
        ('sultan','苏丹·道莱',1012,1021), ('musharrif','穆沙里夫·道莱',1021,1025),
        ('jalal','贾拉勒·道莱',1027,1044), ('abu-kalijar','阿布·卡利贾尔',1044,1048),
        ('malik-rahim','马利克·拉希姆',1048,1055),
    ])
    terms('local:buyid-state', BUYID, '法尔斯支系埃米尔', [
        ('imad','伊马德·道莱',934,949), ('adud','阿杜德·道莱',949,983),
        ('sharaf','沙拉夫·道莱',983,989), ('samsam','萨姆萨姆·道莱',989,998),
        ('baha','巴哈·道莱',998,1012), ('sultan','苏丹·道莱',1012,1024),
        ('abu-kalijar','阿布·卡利贾尔',1024,1048),
    ])
    terms('local:buyid-state', BUYID, '吉巴勒支系埃米尔', [
        ('rukn','鲁克恩·道莱',935,976), ('fakhr','法赫尔·道莱',976,980),
        ('muayyad','穆艾叶德·道莱',980,983), ('fakhr','法赫尔·道莱',983,997),
        ('majd','马吉德·道莱',997,1029),
    ])
    for row in entities['Q12536']['fields']['ruler']:
        start, end = max(945, row['from']), min(1055, row['to'])
        if start <= end:
            entities['local:buyid-state']['fields'].setdefault('imperialSovereign', []).append({
                **row, 'from':start, 'to':end, 'roleLabel':'巴格达阿拔斯哈里发，权力受布韦希埃米尔制约',
            })
    terms('Q147909', BULGARIA, '保加利亚沙皇', [
        ('ferdinand-bulgaria','斐迪南一世',1908,1918),
        ('boris-iii','鲍里斯三世',1918,1943),
        ('simeon-ii','西美昂二世（摄政时期）',1943,1946),
    ])
    terms('local:haiti-divided', HAITI_SPLIT, '北方统治者，1811年称王', [('christophe','亨利·克里斯托夫',1807,1819)])
    terms('local:haiti-divided', HAITI_SPLIT, '南方共和国总统', [
        ('petion','亚历山大·佩蒂翁',1807,1818), ('boyer','让-皮埃尔·布瓦耶',1818,1819),
    ])
    terms('local:haiti-second-empire', HAITI, '海地皇帝', [('soulouque','福斯坦一世',1849,1859)])
    terms('Q790', HAITI, '海地共和国总统', [
        ('boyer','让-皮埃尔·布瓦耶',1820,1843), ('herard','夏尔·里维埃尔-埃拉尔',1843,1844),
        ('guerrier','菲利普·盖里耶',1844,1845), ('pierrot','让-路易·皮埃罗',1845,1846),
        ('riche','让-巴蒂斯特·里谢',1846,1847), ('soulouque','福斯坦·苏卢克',1847,1849),
        ('geffrard','法布尔·热弗拉尔',1859,1867), ('salnave','西尔万·萨尔纳夫',1867,1869),
        ('saget','尼萨日·萨热',1870,1874), ('domingue','米歇尔·多明格',1874,1876),
        ('canal','布瓦龙-卡纳尔',1876,1879), ('salomon','利修斯·萨洛蒙',1879,1888),
        ('legitime','弗朗索瓦·莱吉蒂姆',1888,1889), ('hyppolite','弗洛维尔·伊波利特',1889,1896),
        ('simon-sam','蒂雷齐亚·西蒙·萨姆',1896,1902), ('nord-alexis','皮埃尔·诺尔·阿莱克西',1902,1908),
        ('antoine-simon','安托万·西蒙',1908,1911),
    ])
    write('public/data/polity-facts.json', facts)
    flags = read('public/data/flags.json')
    for flag in flags['entities']['Q12536']:
        if flag['file'] == 'Black flag.svg':
            flag.update({'from':750, 'to':1258, 'role':'阿拔斯黑旗 · 史料示意',
                         'representative':True, 'periodSource':FLAGS,
                         'periodNote':'黑色是阿拔斯的王朝标志。图像以纯黑示意其传统旗色。马蒙曾短期改用绿色，后恢复黑色。'})
    write('public/data/flags.json', flags)
    curated = read('public/data/curated-facts.json')
    curated['identities'].update({'Buyid Dynasty':'local:buyid-state', 'Republic of Haiti':'Q790',
                                  'Hungarian Nationalists':'local:hungarian-revolution',
                                  'Divided Haiti':'local:haiti-divided', 'Second Empire of Haiti':'local:haiti-second-empire'})
    write('public/data/curated-facts.json', curated)
    for path in ['src/localization/display-names.zh.json', 'src/localization/temporal.zh.json']:
        names = read(path)
        names.update({'Buyid Dynasty':'布韦希王朝', 'Republic of Haiti':'海地共和国',
                      'Hungarian Nationalists':'匈牙利革命政府', 'Pro-Swedish Poland':'波兰亲瑞典派',
                      'Divided Haiti':'海地南北政权', 'Second Empire of Haiti':'海地第二帝国'})
        write(path, names)


def main():
    revise_shards()
    revise_archives()
    index = read('public/data/temporal/index.json')
    records = set()
    for century in index['centuries']:
        for row in read(f'public/data/temporal/{century}.geojson')['features']:
            records.add(row['properties']['sourceRecord'])
    index['counts']['polityRecords'] = len(records)
    index['changeYears'] = sorted(set(index['changeYears']) | {1807, 1820, 1849, 1859, 1259, 1850, 1908, 2002})
    write('public/data/temporal/index.json', index)


if __name__ == '__main__':
    main()
