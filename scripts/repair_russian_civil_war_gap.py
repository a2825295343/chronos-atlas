"""Restore the missing Soviet Russian component in the 1918/1919 atlas.

Only the Moscow-connected gap inside the existing 1917 Russian footprint is
reconstructed. Existing annual owners remain untouched. This is a sourced,
approximate annual representation, not a digitized daily civil-war front.
Run after chronology and dynastic refinements, before the global audit/build.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.local/python'))
from shapely import make_valid, union_all
from shapely.geometry import Point, shape, mapping
from prepare_political_presentation import label_path

TAG = 'soviet-russia-gap-1918-1919-v1'
NAME = 'Russian Socialist Federative Soviet Republic'
LABEL = '苏维埃俄国'
QID = 'Q2305208'  # Independent Soviet Russia, not the later USSR republic.
SOURCE = 'https://wwws.loc.gov/rr/geogmap/pdf/ruscw/ruscwmaps.html'
CONSTITUTION = 'https://history.state.gov/historicaldocuments/frus1918Russiav01/d579'


def read(path):
    return json.loads((ROOT / path).read_bytes())


def write(path, data):
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf8')


def polygon_parts(geometry):
    if geometry.geom_type == 'Polygon':
        return [geometry]
    return [part for child in getattr(geometry, 'geoms', []) for part in polygon_parts(child)]


def main():
    path = 'public/data/temporal/19.geojson'
    atlas = read(path)
    original = [f for f in atlas['features'] if f['properties'].get('chronologyPatch') != TAG]
    reference = next(f for f in original if f['properties']['NAME'] == 'Russian Republic'
                     and f['properties']['validFrom'] == 1917)
    footprint = make_valid(shape(reference['geometry']))
    review = []
    for year in (1918, 1919):
        active = [f for f in original if f['properties']['validFrom'] <= year <= f['properties']['validTo']]
        occupied = union_all([make_valid(shape(f['geometry'])) for f in active])
        missing = make_valid(footprint.difference(occupied))
        components = [g for g in polygon_parts(missing) if g.covers(Point(37.62, 55.75))]
        if len(components) != 1:
            raise ValueError(f'{year}: expected one missing Moscow-connected component')
        geometry = components[0]
        if not geometry.covers(Point(30.32, 59.93)) or geometry.area < 100:
            raise ValueError(f'{year}: Soviet Russian core is unexpectedly absent')
        if geometry.intersection(occupied).area > 1e-7:
            raise ValueError(f'{year}: reconstruction would overwrite another owner')
        properties = {
            'NAME': NAME, 'SUBJECTO': NAME, 'displayName': LABEL, 'qid': QID, 'entityId': QID,
            'validFrom': year, 'validTo': year,
            'sourceRecord': f'{TAG}:{year}', 'chronologyPatch': TAG,
            'source': 'Cliopatria历史轮廓 + 美国国会图书馆俄国内战史料核对',
            'sourceUrl': SOURCE, 'identitySource': f'https://www.wikidata.org/wiki/{QID}',
            'identityReviewed': True, 'temporalResolution': 'annual-gap-reconstruction',
            'yearConvention': '沿用源GIS的该年代表性分期；不是全年不变或年末精确战线。',
            'geometryMethod': '1917年俄国历史轮廓减去该年全部已有势力，选取连通莫斯科的缺失多边形；不使用现代俄罗斯国界或1920年苏联轮廓回填。',
            'accuracy': '莫斯科、彼得格勒及相连核心区域应属于苏维埃俄国，源图遗漏了这一势力。以相邻当年势力的既有边线补出缺口；1918与1919分别计算。内战中红白军、地方政权与外国干涉的控制线变化频繁，本补绘仍是概化推断，未逐点复原战线。',
            'labelPath': label_path(geometry, LABEL),
        }
        atlas['features'] = [*original, *[f for f in atlas['features'] if f['properties'].get('chronologyPatch') == TAG and f['properties']['validFrom'] != year]]
        atlas['features'].append({'type': 'Feature', 'properties': properties, 'geometry': mapping(geometry)})
        review.append({'year': year, 'bounds': list(geometry.bounds), 'squareDegrees': geometry.area,
                       'overlapWithExisting': geometry.intersection(occupied).area,
                       'sourceFootprintRecord': reference['properties']['sourceRecord']})
    write(path, atlas)
    index = read('public/data/temporal/index.json')
    all_rows = [f for c in index['centuries'] for f in read(f'public/data/temporal/{c}.geojson')['features']]
    index['counts']['polityRecords'] = len({f['properties']['sourceRecord'] for f in all_rows})
    index['changeYears'] = sorted(set(index['changeYears']) | {1918, 1919, 1920})
    index['russianCivilWarRevision'] = TAG
    write('public/data/temporal/index.json', index)
    for filename in ['src/localization/temporal.zh.json', 'src/localization/display-names.zh.json']:
        names = read(filename)
        names[NAME] = LABEL
        write(filename, names)
    curated = read('public/data/curated-facts.json')
    curated['identities'][NAME] = QID
    write('public/data/curated-facts.json', curated)
    # A small, explicitly dated archive accompanies the newly clickable owner.
    def fact(value, label, start, end, role=None, source=CONSTITUTION):
        row = {'value': value, 'label': label, 'from': start, 'to': end, 'at': None,
               'citation': [source], 'supplement': TAG}
        if role:
            row['roleLabel'] = role
        return row
    facts = read('public/data/polity-facts.json')
    fields = {
        'government': [fact('soviet-republic', '苏维埃共和国；全俄苏维埃代表大会、全俄中央执行委员会及人民委员会构成中央政权', 1918, 1919)],
        'capital': [fact('Q649', '莫斯科（1918年3月由彼得格勒迁入）', 1918, 1919,
                         source=f'https://www.wikidata.org/wiki/{QID}#P36')],
        'ideology': [fact('Q6186', '布尔什维克社会主义／共产主义', 1918, 1919)],
        'ruler': [fact('Q298384', '雅科夫·斯维尔德洛夫', 1917, 1919, '全俄中央执行委员会主席；1919年3月去世', 'https://www.wikidata.org/wiki/Q298384'),
                  fact('Q2723541', '米哈伊尔·弗拉基米尔斯基', 1919, 1919, '1919年3月代理全俄中央执行委员会主席', 'https://www.wikidata.org/wiki/Q2723541'),
                  fact('Q229828', '米哈伊尔·加里宁', 1919, 1938, '1919年3月起任全俄中央执行委员会主席；1922年后为加盟共和国职务', 'https://www.wikidata.org/wiki/Q229828')],
        'headOfGovernment': [fact('Q1394', '弗拉基米尔·列宁', 1917, 1924, '人民委员会主席／政府首脑；1922年后继续担任俄共和国政府职务', f'https://www.wikidata.org/wiki/{QID}#P6')],
    }
    facts['entities'][QID] = {'label': LABEL, 'en': NAME, 'description': '十月革命后建立的苏维埃俄国；本图补绘1918、1919年遗漏的西部核心区域，不表示其全部领土或现代俄罗斯国界。',
                              'fields': fields, 'rulerScopeNote': '列宁作为人民委员会主席另列于政府首脑。1919年元首职位发生交接，年度视图不表示三人全年同时任职。'}
    facts['labels'][QID] = LABEL
    write('public/data/polity-facts.json', facts)
    write('public/data/russian-civil-war-gap-review.json', {
        'revision': TAG, 'reviewedAt': '2026-10-31', 'sources': [SOURCE, CONSTITUTION],
        'method': '只补前俄国轮廓中与莫斯科相连的缺失区域；保留当年全部已有势力。', 'records': review,
        'limitations': ['补全缺失势力，不等于核定相邻所有内战势力的名称及控制线。',
                        '原始轮廓不统一对应年末，不能把1918、1919两幅轮廓理解为逐日战线。']})
    print('Restored Soviet Russian core:', [(r['year'], round(r['squareDegrees'], 3)) for r in review])


if __name__ == '__main__':
    main()
