"""Sourced regional repairs after ALL earlier chronology/postwar pipelines.

Restore missing owners without interpolating a front or inventing a unified
ancient Ireland. Repeated runs start from the first stage input, not its output.
The first-stage backups must be migrated explicitly when upstream data changes.
"""
import copy
import hashlib
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.local/python'))
from shapely import make_valid, union_all
from shapely.geometry import shape, mapping, Polygon, box
from prepare_political_presentation import label_path

TAG = 'regional-gaps-britain-ireland-yemen-italy-v1'
SCOT = 'https://www.parliament.uk/about/living-heritage/evolutionofparliament/legislativescrutiny/act-of-union-1707/overview/union-of-the-crowns/'
COVENANT = 'https://www.nationalarchives.gov.uk/education/resources/civil-war-people/civil-war-person-scottish-covenanter/'
UNION = 'https://commonslibrary.parliament.uk/research-briefings/cbp-10649/'
IRELAND = 'https://libguides.ucd.ie/findingmaps/mapshistireland'
IRON = 'https://heritageireland.ie/articles/mesolithic-iron-age-8000bc-400ad/'
CROWN = 'https://www.legislation.gov.uk/aip/Hen8/33/1'
ADEN = 'https://www.nam.ac.uk/explore/aden-emergency'
FEDERATION = 'https://api.parliament.uk/historic-hansard/written-answers/1963/jul/02/federation'
INDEPENDENCE = 'https://digitallibrary.un.org/record/860183/files/1122896-EN.pdf'
YEMEN = 'https://2021-2025.state.gov/countries-areas/yemen/'
ITALY = 'https://nzhistory.govt.nz/war/the-italian-campaign/timeline'
RSI = 'https://encyclopedia.ushmm.org/content/en/article/italy'
OPERATIONS = 'https://www.ns-taeter-italien.org/en/glossary'
KINSALE = 'https://catalogue.nli.ie/Record/MS_UR_004415'
CORSICA = 'https://www.defense.gouv.fr/80-ans-liberation-corse-recit-trois-actes'


def read(path):
    return json.loads((ROOT / path).read_bytes())


def write(path, data):
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf8')


def polygons(g):
    if g.geom_type == 'Polygon':
        return [g]
    return [p for child in getattr(g, 'geoms', []) for p in polygons(child)]


def clean(g):
    if not g.is_valid:
        g = make_valid(g)
    if g.geom_type in ['Polygon', 'MultiPolygon']:
        return g
    return union_all(polygons(g))


def bounds_overlap(a, b):
    return a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1]


def key(f):
    p = f['properties']
    return (str(p['sourceRecord']), p['NAME'], p['validFrom'], p['validTo'])


def main():
    index = read('public/data/temporal/index.json')
    affected = [c for c in index['centuries'] if -5 <= c <= 17 or c == 19]
    backup = ROOT / '.local/regional-gap-review/original-shards'
    backup.mkdir(parents=True, exist_ok=True)
    originals = {}
    for century in affected:
        dest = ROOT / f'public/data/temporal/{century}.geojson'
        cached = backup / dest.name
        if not cached.exists():
            shutil.copyfile(dest, cached)
        for f in json.loads(cached.read_bytes())['features']:
            originals.setdefault(key(f), f)
    records = list(originals.values())
    geometry = {key(f): clean(shape(f['geometry'])) for f in records}
    admin = read('.local/ne_10m_admin_1_states_provinces.geojson')['features']

    def mask(predicate):
        return clean(union_all([shape(f['geometry']) for f in admin if predicate(f['properties'])]))

    scotland = mask(lambda p: p['admin'] == 'United Kingdom' and p.get('geonunit') == 'Scotland')
    england = mask(lambda p: p['admin'] == 'United Kingdom' and p.get('geonunit') in ['England', 'Wales'])
    ireland = mask(lambda p: p['admin'] == 'Ireland' or p.get('geonunit') == 'Northern Ireland')
    britain = union_all([scotland, england, ireland])
    italy = mask(lambda p: p['admin'] == 'Italy')
    corsica = mask(lambda p: p['admin'] == 'France' and p.get('region') == 'Corse')
    operations = mask(lambda p: p['admin'] == 'Italy' and p['iso_3166_2'] in ['IT-BZ', 'IT-TN', 'IT-BL', 'IT-UD', 'IT-GO', 'IT-TS', 'IT-PN'])
    # A deliberately schematic December 1944 front. It locates Florence,
    # Ravenna/Faenza on the Allied side and Bologna/Milan on the German side.
    # It is not a digitized tactical front, nor reused in any other year.
    south = clean(italy.intersection(Polygon([(-180, -90), (180, -90), (180, 44.58),
        (12.25, 44.58), (12, 44.40), (11.65, 44.36), (11.25, 44.15),
        (10.9, 44.05), (10.25, 44.10), (9.8, 44.0), (-180, 44.0)])))
    north = clean(italy.difference(south))
    # Use an actual pre-independence historical footprint, not modern unified
    # Yemen. The broken query selected a later tiny British island record and
    # discarded this mainland record because both had the same display key.
    south_refs = [f for f in records if f['properties']['NAME'] == 'United Kingdom Colony - Yemen'
                  and f['properties']['validFrom'] <= 1948 <= f['properties']['validTo']]
    south_reference = max(south_refs, key=lambda f: geometry[key(f)].area)
    south_yemen = clean(union_all([geometry[key(f)] for f in south_refs]))
    aden_city = mask(lambda p: p['admin'] == 'Yemen' and p['iso_3166_2'] == 'YE-AD').intersection(south_yemen)
    eastern = clean(union_all([mask(lambda p: p['admin'] == 'Yemen' and p['iso_3166_2'] in ['YE-HD', 'YE-MR']).intersection(south_yemen), south_yemen.intersection(box(53, 10, 56, 14))]))
    western = clean(south_yemen.difference(union_all([aden_city, eastern])))

    replaced = defaultdict(list)
    generated = []
    review = []
    labels = {}
    identities = {}

    def intervals(region, lo, hi, boundaries):
        relevant = [f for f in records if f['properties']['validFrom'] <= hi
                    and lo <= f['properties']['validTo'] and bounds_overlap(geometry[key(f)].bounds, region.bounds)
                    and geometry[key(f)].intersects(region)]
        stops = {lo, hi + 1, *[v for v in boundaries if lo < v <= hi]}
        for f in relevant:
            p = f['properties']
            stops.update([max(lo, p['validFrom']), min(hi + 1, p['validTo'] + 1)])
        stops = sorted(stops)
        return zip(stops, stops[1:])

    def work_at(year):
        active = {}
        for f in records:
            p = f['properties']
            if p['validFrom'] <= year <= p['validTo']:
                n = p['NAME']
                if n not in active or (p['validFrom'], -p['validTo']) > (active[n]['properties']['validFrom'], -active[n]['properties']['validTo']):
                    active[n] = f
        working = {n: [copy.deepcopy(f['properties']), geometry[key(f)]] for n, f in active.items()}
        # Mainland and island rows are simultaneous administrative fragments,
        # not successive borders. Resolve this known colliding key explicitly;
        # do not change the global latest-valid-period query rule.
        british_parts = [geometry[key(f)] for f in records if f['properties']['NAME'] == 'United Kingdom Colony - Yemen'
                         and f['properties']['validFrom'] <= year <= f['properties']['validTo']]
        if british_parts:
            working['United Kingdom Colony - Yemen'][1] = clean(union_all(british_parts))
        return working

    def process(region, lo, hi, boundaries, callback):
        for a, b in intervals(region, lo, hi, boundaries):
            working = work_at(a)
            dirty = set()
            audit = {'from': a, 'to': b - 1, 'region': callback.__name__, 'changes': []}

            def take(area, predicate):
                parts = []
                for n, (p, g) in list(working.items()):
                    if not predicate(n, p) or not bounds_overlap(g.bounds, area.bounds):
                        continue
                    piece = clean(g.intersection(area))
                    if piece.area < 1e-8:
                        continue
                    working[n][1] = clean(g.difference(area))
                    dirty.add(n)
                    parts.append(piece)
                return clean(union_all(parts))

            def unowned(area):
                claimed = [g.intersection(area) for p, g in working.values()
                           if not g.is_empty and bounds_overlap(g.bounds, area.bounds)]
                return clean(area.difference(union_all(claimed)))

            def put(n, label, qid, g, source, accuracy, **extra):
                g = clean(g)
                if g.is_empty or g.area < 1e-8:
                    return
                if n in working:
                    g = clean(union_all([working[n][1], g]))
                    p = working[n][0]
                else:
                    p = {'NAME': n, 'SUBJECTO': n, 'qid': qid, 'entityId': qid}
                p.update(NAME=n, SUBJECTO=n, qid=qid, entityId=qid, displayName=label,
                         sourceUrl=source, accuracy=accuracy)
                p.update(extra)
                if p.get('regionalCollection'):
                    p['representationNote'] = accuracy
                working[n] = [p, g]
                dirty.add(n)
                labels[n] = label
                identities[n] = qid

            callback(a, b - 1, working, dirty, take, unowned, put)
            for n in sorted(dirty):
                p, g = working[n]
                replaced[n].append((a, b - 1))
                if g.is_empty:
                    continue
                p = copy.deepcopy(p)
                p.setdefault('sourceUrl', {'british_isles': SCOT, 'south_arabia': ADEN, 'italian_campaign': ITALY}[callback.__name__])
                p.setdefault('accuracy', '保留原有效时期的其余轮廓，仅扣去本轮单独恢复的地区；不是重新测绘该政权全部领土。')
                p['upstreamSourceRecord'] = p.get('sourceRecord')
                p.update(validFrom=a, validTo=b - 1, chronologyPatch=TAG,
                         sourceRecord=TAG + ':' + hashlib.sha1(f'{n}|{a}|{b}'.encode()).hexdigest()[:16],
                         source='有史料的区域遗漏与身份修订', temporalResolution='reviewed-regional-period',
                         geometryMethod='历史GIS轮廓与地理遮罩的分期补绘；既有邻国不被自动吞并，内部界线和战线为明确标注的概化。',
                         labelPath=label_path(g, p.get('displayName', n)))
                generated.append({'type': 'Feature', 'properties': p, 'geometry': mapping(g)})
                audit['changes'].append({'name': n, 'squareDegrees': round(g.intersection(region).area, 8)})
            review.append(audit)
        print(callback.__name__, 'completed', flush=True)

    def british_isles(a, b, w, dirty, take, unowned, put):
        # Irish areas on a Scottish source outline do not constitute Scottish
        # sovereignty over Ulster. Return them to the regional reconstruction.
        if a <= 1641:
            removed = take(ireland, lambda n, p: n == 'Kingdom of Scotland')
            crown_pieces = take(ireland, lambda n, p: n in ['Kingdom of England', 'Norman England', 'Angevin Empire'])
            if a >= 1602:
                # The source retains the Spanish Kinsale enclave until 1608.
                # Its surrender in January 1602 is documented by the NLI.
                spanish = take(ireland, lambda n, p: n in ['Iberian Union', 'Spanish Empire'])
                crown_pieces = clean(union_all([crown_pieces, spanish]))
            if not crown_pieces.is_empty:
                if a < 1177:
                    n, label, q = 'Anglo-Norman Irish Lordships', '盎格鲁—诺曼爱尔兰领地', 'local:anglo-norman-ireland'
                elif a < 1541:
                    n, label, q = 'Lordship of Ireland', '爱尔兰领地', 'local:lordship-of-ireland'
                else:
                    n, label, q = 'Kingdom of Ireland', '爱尔兰王国', 'local:kingdom-of-ireland'
                put(n, label, q, crown_pieces, CROWN if a >= 1541 else IRELAND,
                    '仅将源GIS已有的英王／盎格鲁—诺曼控制部分按爱尔兰当地政体单列；王权头衔不代表已实际控制全岛。',
                    sovereignName='Kingdom of England', sovereignQid='Q179876', territoryType='member')
            gap = unowned(ireland)
            if a < 500:
                n, label, q = 'Irish Iron Age Polities', '爱尔兰铁器时代诸部族', 'local:irish-iron-age-polities'
                source, note = IRON, '铁器时代爱尔兰已有人群与地方政治组织；此轮只补岛上未记录的地域。不是统一国家、逐部族边界或一个共同统治者；起止为考古时代的概化分期。'
            elif a < 1169:
                n, label, q = 'Gaelic Irish Kingdoms', '盖尔爱尔兰诸国', 'local:gaelic-irish-kingdoms'
                source, note = IRELAND, '爱尔兰诸王国与地方王权的地域集合，不等于单一统一王国；保留已收录的达尔里阿达、北欧人城镇等范围。尚无可靠逐国矢量边界，不补造省界或共同国王。'
            elif a < 1603:
                n, label, q = 'Gaelic Irish Lordships', '盖尔爱尔兰诸领地', 'local:gaelic-irish-lordships'
                source, note = IRELAND, '盖尔地方诸领地的剩余地域集合，扣除当年已知英王领地、诺曼领地和独立伯国。不是统一国家；未将英王的全岛主权宣称当作实际控制。'
            else:
                n, label, q = 'Kingdom of Ireland', '爱尔兰王国', 'local:kingdom-of-ireland'
                source, note = IRELAND, '都铎征服结束后补全爱尔兰王国的岛上遗漏部分；保留当年其他已知控制区。地理遮罩用于补绘海岸，不等于恢复每年庄园和殖民垦殖边界。'
            extra = dict(regionalCollection=True, territoryType='regional') if a < 1603 else dict(sovereignName='Kingdom of England', sovereignQid='Q179876', territoryType='member')
            put(n, label, q, gap, source, note, **extra)
        if 1609 <= a <= 1706:
            # Crowns remain separate after 1603; the Commonwealth is the dated
            # exception. This also restores the 1640s missing Scottish outline.
            take(scotland, lambda n, p: n in ['Kingdom of England', 'Kingdom of Scotland', 'Commonwealth of England'])
            name, label, q = ('Commonwealth of England', '英格兰、苏格兰和爱尔兰共和国', 'Q330362') if 1652 <= a <= 1659 else ('Kingdom of Scotland', '苏格兰', 'Q230791')
            put(name, label, q, unowned(scotland), SCOT,
                '1603年为共主联合，苏格兰并未立即并入英格兰。1652—1659年按英联邦实际控制的概化阶段显示；1651年仍保留苏格兰王权抵抗的年度代表状态。1641年国内权力受盟约派及议会制约。1707年联合以后不再单列。')
        if 1640 <= a <= 1659:
            name, label, q = ('Kingdom of England', '英格兰', 'Q179876') if a < 1649 else ('Commonwealth of England', '英格兰共和国', 'Q330362')
            put(name, label, q, unowned(england), COVENANT,
                '补出不列颠岛北英格兰的遗漏。1640—1641年苏军曾占领纽卡斯尔及北部两郡，1641年伦敦条约后撤军；此层表示年度政体地域概览，不复原内战中每日变化的军队控制线。')
        if 1707 <= a <= 1708:
            piece = take(union_all([scotland, england]), lambda n, p: n in ['Kingdom of England', 'Kingdom of Scotland'])
            put('Kingdom of Great Britain', '大不列颠', 'Q161885', union_all([piece, unowned(union_all([scotland, england]))]), UNION,
                '1707年5月英格兰与苏格兰合并为大不列颠王国；按联合后的年度代表状态，不将1603年的共主联合提前视为国家合并。')
            irish_piece = take(ireland, lambda n, p: n == 'Kingdom of England')
            put('Kingdom of Ireland', '爱尔兰王国', 'local:kingdom-of-ireland', irish_piece, UNION,
                '1707年英苏合并时爱尔兰仍是另一个王国，并未一并成为大不列颠本土；地图仅按已有爱尔兰地域分列。',
                sovereignName='Kingdom of Great Britain', sovereignQid='Q161885', territoryType='member')

    def south_arabia(a, b, w, dirty, take, unowned, put):
        take(south_yemen, lambda n, p: n in ['United Kingdom Colony - Yemen', "People's Democratic Republic of Yemen"])
        if a < 1967:
            parent = dict(sovereignName='United Kingdom', sovereignQid='Q145', territoryType='protectorate')
            if a < 1963:
                put('Colony of Aden', '亚丁殖民地', 'local:aden-colony', unowned(aden_city), ADEN,
                    '亚丁直辖殖民地与周围保护地诸邦分列；用亚丁地理区定位，不能视为当年殖民地的精确市界。', **{**parent, 'territoryType': 'colony'})
                label = '西亚丁保护地诸邦' if a < 1959 else '西亚丁诸邦（部分组成联邦）'
                put('Western Aden Protectorate States', label, 'local:western-aden-states', unowned(western), FEDERATION,
                    '西亚丁保护地的地方苏丹国与酋长国集合；部分自1959年组成南方阿拉伯酋长国联邦，成员随后陆续加入。未以这个集合多边形宣称所有诸邦1959年同时加入，也未虚构一个共同苏丹。', regionalCollection=True, **parent)
                put('Eastern Aden Protectorate States', '东亚丁保护地诸邦', 'local:eastern-aden-states', unowned(eastern), ADEN,
                    '哈德拉毛、马赫拉等东部保护地诸邦；不是英属非洲，也不属于北也门。内部国界尚未逐邦数字化。', regionalCollection=True, **parent)
            else:
                put('Western South Arabian States', '南阿拉伯联邦及西部诸邦', 'local:western-south-arabian-states', unowned(union_all([aden_city, western])), FEDERATION,
                    '亚丁于1963年1月18日加入联邦。这里是联邦及仍在其外的西部保护邦的地域集合，不能把现代行政区界当成准确联邦成员界；地方制度不同，未指定一个共同君主。', regionalCollection=True, **parent)
                put('Eastern South Arabian Protectorate', '南阿拉伯东部保护地诸邦', 'local:eastern-south-arabian-states', unowned(eastern), ADEN,
                    '未加入联邦的哈德拉毛与马赫拉等保护邦，独立前继续与联邦分列。现代行政分区只用于地理定位，不等于精确保护邦界。', regionalCollection=True, **parent)
        else:
            put("People's Republic of Southern Yemen", '南也门人民共和国', 'Q199841', unowned(south_yemen), INDEPENDENCE,
                '1967年11月30日独立；1967年取独立后的年度状态，1970年才改称也门民主人民共和国。使用独立前历史GIS范围补缺，不把现代统一也门全境回填。')

    def italian_campaign(a, b, w, dirty, take, unowned, put):
        take(italy, lambda n, p: n in ['Nazi Germany', 'Kingdom of Italy'])
        put('Kingdom of Italy', '意大利王国', 'Q172579', unowned(south), ITALY,
            '1944年意大利王国与盟军解放／管理地区。按年末概化：罗马6月解放、佛罗伦萨8月解放、拉文纳及法恩扎12月解放；不是1944全年固定边界。与北部的分界为哥特防线战区的示意，未逐段复原战术战线。',
            yearConvention='1944年采用12月附近的概化代表状态。', regionalControlNote='王国政府与盟军军事管理并存，各地移交民政时间不同；不把盟军控制误写成无势力。', regionalControlSource=ITALY)
        put('Italian Social Republic', '意大利社会共和国（德占）', 'local:italian-social-republic', unowned(north.difference(operations)), RSI,
            '1943年9月至1945年由墨索里尼领导、依附德国军事占领的政权。1944年按年末北意大利概化控制范围；不把德军占领当成德国正式吞并。阿尔卑斯山前沿及亚得里亚滨海直接管理区另列。',
            controlArea=True, controller='Nazi Germany', controllerQid='Q7318', sovereignName='Kingdom of Italy', territoryType='occupation', controlId='de-italy-rsi-1944')
        put('Control area - de-italy-operations-1944', '意大利东北部（德国直接军事管理）', 'local:german-italian-operations', unowned(north.intersection(operations)), OPERATIONS,
            '德军阿尔卑斯山前沿与亚得里亚滨海作战区在今意大利境内的概化部分；使用省域定位，不等于意大利社会共和国完整管辖，也不包括源数据另列的境外部分。',
            controlArea=True, controller='Nazi Germany', controllerQid='Q7318', sovereignName='Kingdom of Italy', territoryType='occupation', controlId='de-italy-operations-1944')

        put('France', '法国', 'Q142', unowned(corsica), CORSICA,
            '科西嘉于1943年10月解放，1944年属于法国解放地区；不是无势力，也不是意大利领土。仅恢复被上游遗漏的科西嘉，不以此推断法国本土整年的实际控制范围。',
            yearConvention='1944年法国解放地区的年度地域参考。')

    process(britain, -500, 1708, [500, 1169, 1177, 1541, 1602, 1603, 1609, 1640, 1642, 1649, 1652, 1660, 1707], british_isles)
    process(south_yemen, 1948, 1969, [1953, 1959, 1963, 1967], south_arabia)
    process(union_all([italy, corsica]), 1944, 1944, [], italian_campaign)

    output = []
    for f in records:
        p = f['properties']
        intervals_to_remove = replaced.get(p['NAME'], [])
        if not intervals_to_remove:
            output.append(f)
            continue
        segments = [(p['validFrom'], p['validTo'])]
        for x, y in intervals_to_remove:
            next_segments = []
            for a, b in segments:
                if y < a or x > b:
                    next_segments.append((a, b))
                else:
                    if a < x: next_segments.append((a, x - 1))
                    if y < b: next_segments.append((y + 1, b))
            segments = next_segments
        for a, b in segments:
            row = copy.deepcopy(f)
            row['properties'].update(validFrom=a, validTo=b)
            output.append(row)
    output += generated
    for century in affected:
        rows = [f for f in output if f['properties']['validFrom'] < (century + 1) * 100 and f['properties']['validTo'] >= century * 100]
        write(f'public/data/temporal/{century}.geojson', {'type': 'FeatureCollection', 'features': rows})
    for filename in ['src/localization/display-names.zh.json', 'src/localization/temporal.zh.json']:
        names = read(filename)
        names.update(labels)
        write(filename, names)
    curated = read('public/data/curated-facts.json')
    curated['identities'].update(identities)
    for r in curated['relations'][:]:
        if r.get('supplement') == TAG: curated['relations'].remove(r)
    for start, end in [(1603, 1648), (1660, 1706)]:
        curated['relations'].append({'id': f'{TAG}:crowns:{start}', 'kind': 'personalUnion', 'members': ['Kingdom of England', 'Kingdom of Scotland'], 'from': start, 'to': end,
            'title': '英格兰—苏格兰共主联合', 'detail': '共奉一位君主，保持各自王国及议会；不是1603年国家合并。内战期间实际权力发生分裂。', 'source': SCOT, 'supplement': TAG})
    english_rulers = curated['polities'].get('Q179876', {}).get('rulers', [])
    for q, a, b in [('local:lordship-of-ireland', 1177, 1540), ('local:kingdom-of-ireland', 1541, 1641)]:
        curated['polities'][q] = {'label': '爱尔兰领地' if a == 1177 else '爱尔兰王国', 'source': CROWN,
            'rulersSource': 'https://www.royal.uk/kings-and-queens-1066',
            'rulers': [[max(a, x), min(b, y), label] for x, y, label in english_rulers if x <= b and a <= y],
            'summary': '爱尔兰当地的王权政体；与英格兰共奉君主，实际控制范围与全岛主权宣称分开理解。'}
    curated['polities']['local:kingdom-of-ireland']['rulers'].append([1702, 1714, '安妮女王'])
    for start, end in [(1541, 1641)]:
        curated['relations'].append({'id': f'{TAG}:irish-crown:{start}', 'kind': 'personalUnion',
            'members': ['Kingdom of England', 'Kingdom of Ireland'], 'from': start, 'to': end,
            'title': '英格兰—爱尔兰共主王权', 'detail': '共奉英王为爱尔兰国王；爱尔兰有其独立王国头衔与行政机构，但并非平等或完全自主的联合。', 'source': CROWN, 'supplement': TAG})
    write('public/data/curated-facts.json', curated)
    facts = read('public/data/polity-facts.json')
    def fact(value, label, a, b, source, **extra):
        return dict(value=value, label=label, **{'from': a, 'to': b}, at=None, citation=[source], supplement=TAG, **extra)
    definitions = {
        'local:irish-iron-age-polities': ('爱尔兰铁器时代诸部族', -500, 499, IRON, '地方部族政治组织；不是统一国家，未将传说世系当作可靠任期'),
        'local:gaelic-irish-kingdoms': ('盖尔爱尔兰诸国', 500, 1168, IRELAND, '多个地方王国与王权集团；无可套用于全境的同一国王'),
        'local:gaelic-irish-lordships': ('盖尔爱尔兰诸领地', 1169, 1602, IRELAND, '多个盖尔地方领地；高王头衔与英王主权宣称不等于实际统一'),
        'local:western-aden-states': ('西亚丁保护地诸邦', 1948, 1962, FEDERATION, '多个苏丹国、酋长国与1959年起逐步组建的联邦；不是共同君主制国家'),
        'local:eastern-aden-states': ('东亚丁保护地诸邦', 1948, 1962, ADEN, '多个当地苏丹国与保护邦；保护关系不等同英国国王直接担任当地苏丹'),
        'local:western-south-arabian-states': ('南阿拉伯联邦及西部诸邦', 1963, 1966, FEDERATION, '联邦政府、成员邦及尚未加入的地方保护邦；未将地域集合当成单一苏丹国'),
        'local:eastern-south-arabian-states': ('南阿拉伯东部保护地诸邦', 1963, 1966, ADEN, '仍在联邦以外的东部保护邦；各有当地统治机构'),
    }
    for q, (label, a, b, source, government) in definitions.items():
        e = facts['entities'].setdefault(q, {'label': label, 'en': next(n for n, v in identities.items() if v == q), 'description': government, 'fields': {}})
        e['fields']['government'] = [fact('regional-polities', government, a, b, source)]
        if q.startswith('local:irish') or q.startswith('local:gaelic'):
            e['fields']['ruler'] = [fact('local:multiple-local-authorities', '各地部族首领／国王／领主（此区域不适用单一共同统治者）', a, b, source, kind='collective', roleLabel='地域集合，非统一中央政府')]
        facts['labels'][q] = label
    for q, label, name, a, b in [
        ('local:aden-colony', '亚丁殖民地', 'Colony of Aden', 1948, 1962),
        ('local:anglo-norman-ireland', '盎格鲁—诺曼爱尔兰领地', 'Anglo-Norman Irish Lordships', 1169, 1176),
        ('local:lordship-of-ireland', '爱尔兰领地', 'Lordship of Ireland', 1177, 1540),
        ('local:kingdom-of-ireland', '爱尔兰王国', 'Kingdom of Ireland', 1541, 1641),
    ]:
        facts['entities'].setdefault(q, {'label': label, 'en': name, 'description': '分期地域与上层王权／管理关系已在地图说明；不据现代国家身份回填。', 'fields': {}})
        facts['entities'][q]['fields']['capital'] = [fact('local:administrative-centre', '亚丁' if 'aden' in q else '都柏林', a, b, ADEN if 'aden' in q else IRELAND)]
        facts['labels'][q] = label
    facts['entities']['local:italian-social-republic'] = {'label': '意大利社会共和国', 'en': 'Italian Social Republic', 'description': '德国军事占领下的北意大利法西斯政权；不是意大利王国或德国正式吞并领土。', 'fields': {
        'ruler': [fact('Q23559', '贝尼托·墨索里尼', 1943, 1945, RSI, roleLabel='意大利社会共和国领导人；依附德国军事占领')],
        'government': [fact('fascist-republic', '法西斯一党专政；依附德国的占领政权', 1943, 1945, RSI)],
        'capital': [fact('de-facto-seat', '萨洛及加尔达湖周边政府驻地；罗马为名义首都', 1943, 1945, RSI)]}}
    facts['entities']['local:german-italian-operations'] = {'label': '意大利东北部德国军事管理区', 'en': 'German operational zones in Italy', 'description': '德军直接管理的作战区，非独立国家；仅表示当前意大利地理遮罩内的部分。', 'fields': {}}
    write('public/data/polity-facts.json', facts)
    # Recompute the index from all actually packaged shards, including stages
    # outside this patch. Never restore the old upstream record count.
    all_rows = [f for c in index['centuries'] for f in read(f'public/data/temporal/{c}.geojson')['features']]
    index['counts']['polityRecords'] = len({f['properties']['sourceRecord'] for f in all_rows})
    index['changeYears'] = sorted(set(index['changeYears']) | {y for f in generated for y in [f['properties']['validFrom'], f['properties']['validTo'] + 1]})
    index['regionalGapRevision'] = TAG
    write('public/data/temporal/index.json', index)
    write('public/data/regional-gap-review.json', {'revision': TAG, 'reviewedAt': '2026-10-31', 'records': review,
        'sources': [SCOT, COVENANT, UNION, IRELAND, IRON, CROWN, KINSALE, ADEN, FEDERATION, INDEPENDENCE, ITALY, RSI, OPERATIONS, CORSICA],
        'limitations': ['早期爱尔兰的区域集合不等于统一国家；尚未核定的逐王国疆界和传说世系未补造。',
            '亚丁内部管理区以现代地理区辅助定位，不等于联邦各成员逐年精确边界；联邦外诸邦不冒称均已入盟。',
            '1944年意大利取年末概化的哥特防线战区，非逐日或战术级战线。']})
    print('Regional repair:', len(generated), 'generated period records;', len(affected), 'shards;', len(labels), 'labels', flush=True)


if __name__ == '__main__':
    main()
