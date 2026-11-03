"""Repair a one-year Qing omission and separate source map symbols from territory.

Only reviewed colonial families in the Americas are processed. Original source
polygons and the pre-repair shards are preserved; islands are never size-filtered.
"""
import copy, hashlib, json, shutil
from collections import defaultdict
from territory_repair_stage import ROOT, read, write, clean
from prepare_political_presentation import label_path
from shapely import union_all
from shapely.geometry import shape, mapping, box, Point

TAG = 'qing-american-fragments-2026-11-01'
CLIO = 'https://github.com/Seshat-Global-History-Databank/cliopatria'
POSTS = 'https://open.canada.ca/data/en/dataset/96e248e8-f422-5d69-a085-cce12b04e11a'
NIAN = 'https://api.repository.cam.ac.uk/server/api/core/bitstreams/9a783ace-a7b3-46f0-bc60-324c1bbdeb67/content'
FAMILIES = {'British Colonial Empire', 'British Empire', 'New France', 'French Louisiana',
            'Spanish Empire', 'Portuguese Empire', 'Bourbon Kingdom of France', 'Kingdom of France'}
AMERICAS = box(-170, -56, -30, 80)


def parts(g):
    return list(g.geoms) if g.geom_type == 'MultiPolygon' else [g] if g.geom_type == 'Polygon' else []


def main():
    backup = ROOT / '.local' / TAG / 'original-shards'
    backup.mkdir(parents=True, exist_ok=True)
    rows = {}
    for century in [17, 18, 19]:
        saved = backup / f'{century}.geojson'
        if not saved.exists():
            shutil.copyfile(ROOT / f'public/data/temporal/{century}.geojson', saved)
        for f in json.loads(saved.read_bytes())['features']:
            p = f['properties']
            rows.setdefault((str(p['sourceRecord']), p['NAME'], p['validFrom'], p['validTo']), f)
    rows = list(rows.values())
    def at(name, year):
        candidates = [f for f in rows if f['properties']['NAME'] == name
                      and f['properties']['validFrom'] <= year <= f['properties']['validTo']]
        return max(candidates, key=lambda f: (f['properties']['validFrom'], -f['properties']['validTo']))

    qing = at('Qing Dynasty', 1856)
    # Shared adjacent-year territory is stronger evidence than a modern China mask.
    prior = shape(at('Qing Dynasty', 1855)['geometry'])
    following = shape(at('Qing Dynasty', 1857)['geometry'])
    region = box(108, 31, 122, 42)
    occupied = union_all([shape(f['geometry']).intersection(region) for f in rows
                         if f['properties']['validFrom'] <= 1856 <= f['properties']['validTo']])
    restored = clean(prior.intersection(following).intersection(region).difference(occupied))
    qing['geometry'] = mapping(clean(union_all([shape(qing['geometry']), restored])))
    qing['properties'].update(
        chronologyPatch=TAG, sourceUrl=NIAN, geometrySources=[CLIO, NIAN],
        accuracy='1856年华北遗漏以1855、1857年清朝轮廓共同覆盖的陆地区补回，并扣除已有其他控制方。'
                 '此为年度行政归属概览，捻军活动、团练和清军控制交错，不表示清军逐处持续实控；不将袭扰范围当作固定国界。',
        geometryMethod='相邻两年共同轮廓限定的一年缺项修复；保留太平天国和其他现存控制方。')
    qing['properties']['labelPath'] = label_path(qing['geometry'], '清朝')

    raw = read('.local/cliopatria.geojson')['features']
    admin = read('.local/presentation/admin0.geojson')['features']
    # Largest land masses exclude Caribbean islands, Vancouver Island, etc.
    mainland = clean(union_all([max(parts(shape(f['geometry'])), key=lambda p: p.area)
                               for f in admin if f['properties']['NAME_EN'] in
                               ['Canada', 'United States of America', 'Mexico']]))
    groups = defaultdict(list)
    for f in rows:
        p = f['properties']; sid = p['sourceRecord']
        if isinstance(sid, int) and p['validFrom'] <= 1899 and p['validTo'] >= 1700 and sid < len(raw):
            if raw[sid]['properties']['Name'] in FAMILIES:
                groups[sid].append(f)
    sites = []; audit = []; deleted = set()
    for group_index, (sid, group) in enumerate(groups.items()):
        if group_index % 25 == 0:
            print('Reviewing colonial source group', group_index, '/', len(groups), flush=True)
        geometries = {id(f): shape(f['geometry']) for f in group}
        def american_union():
            return clean(union_all([part for g in geometries.values() for part in parts(g)
                                   if AMERICAS.intersects(part)]))
        before_union = american_union()
        source = raw[sid]; original = clean(shape(source['geometry'])); symbols = []
        for component in parts(original):
            if not box(-150, 30, -50, 75).covers(component) or component.interiors:
                continue
            w, s, e, n = component.bounds
            # Repeated small angular symbols digitized in the upstream basemap.
            # A source shape alone cannot establish a fort name or legal boundary.
            if (len(component.exterior.coords) <= 18 and .025 < component.area < .22
                    and .15 < n-s < .65 and .15 < e-w < 1.2
                    and component.area / component.minimum_rotated_rectangle.area > .6
                    and mainland.covers(component)
                    and mainland.boundary.distance(component.representative_point()) > .02):
                symbols.append(component)
        cuts = union_all(symbols)
        converted = 0; attached = 0
        if symbols:
            for component in symbols:
                point = component.representative_point()
                owner = max(group, key=lambda f: geometries[id(f)].intersection(component).area)
                p = owner['properties']; area = geometries[id(owner)].intersection(component).area
                if area < component.area * .1:
                    continue
                props = {
                    'id': f'{TAG}:{sid}:{converted}', 'label': '殖民据点参考',
                    'operator': p.get('sovereignName', source['properties']['Name']),
                    'ownerName': p['NAME'], 'ownerLabel': p.get('displayName', p['NAME']),
                    'validFrom': p['validFrom'], 'validTo': p['validTo'],
                    'sourceRecord': sid, 'sourceUrl': CLIO, 'contextSource': POSTS,
                    'accuracy': '将上游反复出现的规则小块改为据点参考符号。位置取原小块内部点，'
                                '具体站名和逐年运营情况尚待核定；这不是该形状大小的独立领土，也不证明周边原住民土地归其直接控制。',
                    'inferred': True, 'representationKind': 'source-symbol-reference'}
                sites.append({'type': 'Feature', 'properties': props, 'geometry': mapping(point)})
                converted += 1
            for f in group:
                geometries[id(f)] = clean(geometries[id(f)].difference(cuts))

        # Modern-mask colonial naming left narrow bits outside its coastline.
        # Reattach only small American residuals to the SAME upstream colonial
        # record and contemporary partition. No area or island is discarded.
        for f in group:
            p = f['properties']
            if p['NAME'] != source['properties']['Name']:
                continue
            retained = []
            candidates = [r for r in group if r is not f and r['properties'].get('sourcePolity') == p['NAME']
                          and r['properties']['validFrom'] == p['validFrom']
                          and r['properties']['validTo'] == p['validTo']]
            targets = {id(r): geometries[id(r)] for r in candidates}
            additions = defaultdict(list)
            for component in parts(geometries[id(f)]):
                if not AMERICAS.covers(component) or component.area >= .25:
                    retained.append(component)
                    continue
                w, s, e, n = component.bounds
                nearby = [(component.distance(targets[id(r)]), r) for r in candidates
                          if not targets[id(r)].is_empty and
                          targets[id(r)].bounds[0] < e+.045 and targets[id(r)].bounds[2] > w-.045 and
                          targets[id(r)].bounds[1] < n+.045 and targets[id(r)].bounds[3] > s-.045]
                distance, target = min(nearby, key=lambda x: x[0]) if nearby else (999, None)
                if AMERICAS.covers(component) and component.area < .25 and distance < .045:
                    additions[id(target)].append(component); attached += 1
                else:
                    retained.append(component)
            geometries[id(f)] = clean(union_all(retained))
            for r in candidates:
                if additions[id(r)]:
                    geometries[id(r)] = clean(union_all([targets[id(r)], *additions[id(r)]]))
        for f in group:
            g = geometries[id(f)]
            if g.is_empty:
                deleted.add(id(f)); continue
            if converted or attached:
                f['geometry'] = mapping(g)
                p = f['properties']; p['cartographyRevision'] = TAG
                path = p.get('labelPath')
                if path and not g.covers(Point(path['coordinates'][len(path['coordinates'])//2])):
                    p['labelPath'] = None
        if converted or attached:
            after_union = american_union()
            expected = clean(before_union.difference(cuts))
            residual_error = after_union.symmetric_difference(expected).area
            if residual_error > .000001:
                raise ValueError(f'Unexplained colonial area loss or gain: {sid} {residual_error}')
            audit.append({'record': sid, 'sourceName': source['properties']['Name'],
                          'from': source['properties']['FromYear'], 'to': source['properties']['ToYear'],
                          'symbolsConverted': converted, 'partitionResidualsReattached': attached,
                          'unexplainedAreaChange': residual_error})
    output = [f for f in rows if id(f) not in deleted]
    for c in [17, 18, 19]:
        write(f'public/data/temporal/{c}.geojson', {'type': 'FeatureCollection', 'features': [f for f in output
              if f['properties']['validFrom'] < (c+1)*100 and f['properties']['validTo'] >= c*100]})
    write('public/data/colonial-reference-sites.geojson', {'type': 'FeatureCollection', 'features': sites})
    index = read('public/data/temporal/index.json')
    allrows = [f for c in index['centuries'] for f in read(f'public/data/temporal/{c}.geojson')['features']]
    index['counts']['polityRecords'] = len({f['properties']['sourceRecord'] for f in allrows})
    index['cartographicSymbolRevision'] = TAG
    write('public/data/temporal/index.json', index)
    write('public/data/qing-american-fragments-review.json', {
        'revision': TAG, 'qingRestoredSquareDegrees': restored.area,
        'records': audit, 'sitePeriods': len(sites),
        'partitionResidualsReattached': sum(r['partitionResidualsReattached'] for r in audit),
        'sources': [CLIO, POSTS, NIAN],
        'limitations': ['据点识别为形状与地域辅助推断，未虚构具体站名或精确营业年代。',
                        '未按面积全局删除飞地、岛屿或原住民领地。',
                        '灰色仍表示缺少可关联轮廓，不等于无人居住或无政治组织。']})
    print('Qing restored:', round(restored.area, 3), 'site periods:', len(sites),
          'residuals reattached:', sum(r['partitionResidualsReattached'] for r in audit), flush=True)


if __name__ == '__main__':
    main()
