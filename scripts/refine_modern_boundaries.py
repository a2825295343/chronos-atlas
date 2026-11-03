"""Build the modern political frame from a common admin-0 topology.

Reference geometries are accepted only for confidently matched map entities.
Unmatched territorial records retain precedence over the reference.
"""
from collections import defaultdict
from territory_repair_stage import clean, read, write
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely.strtree import STRtree

PATH = 'public/data/temporal/20.geojson'
SOURCE = 'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/'
TAG = 'natural-earth-modern-admin0'
IDS = {
    'Republic of China':'Q865', 'Republic of Korea':'Q884',
    'Republic of the Congo':'Q971',
}
ALIASES = {'Azerbaijan', 'Kuwait'}


def main():
    data = read(PATH)
    reference = defaultdict(list)
    for feature in read('.local/presentation/admin0.geojson')['features']:
        reference[feature['properties'].get('WIKIDATAID')].append(clean(shape(feature['geometry'])))
    rows = [f for f in data['features'] if f['properties']['validFrom'] == 2024
            and not f['properties'].get('controlArea')]
    original = [clean(shape(f['geometry'])) for f in rows]
    candidates = {}
    for i, (f, old) in enumerate(zip(rows, original)):
        p = f['properties']
        refs = reference[IDS.get(p['NAME'], p.get('qid'))]
        if p['NAME'] in ALIASES or len(refs) != 1 or old.is_empty:
            continue
        ref = refs[0]
        # The atlas shows these separately named administrative areas as
        # parts of the same national polygon in the modern view.
        if p['NAME'] == "People's Republic of China":
            ref = unary_union([ref, *reference['Q8646'], *reference['Q14773']])
        intersection = old.intersection(ref).area
        # Avoid replacing e.g. a metropolitan outline with a differently
        # scoped sovereign outline or an incompatible disputed region.
        if intersection >= .88 * max(old.area, ref.area):
            candidates[i] = ref

    # An ambiguous match never consumes an existing independently mapped area.
    protected = [g for i, (f, g) in enumerate(zip(rows, original))
                 if i not in candidates and f['properties']['NAME'] not in ALIASES]
    protection = STRtree(protected)
    for i, ref in candidates.items():
        f = rows[i]
        p = f['properties']
        overlaps = [protected[j] for j in protection.query(ref, predicate='intersects')
                    if ref.intersection(protected[j]).area > 1e-10]
        refined = clean(ref.difference(unary_union(overlaps))) if overlaps else ref
        if refined.is_empty:
            continue
        f['geometry'] = mapping(refined)
        p.pop('labelPath', None)
        p.update(coastalReference=SOURCE, boundaryGeometry=TAG)

    # The shared land layer can contain tiny islands absent from admin-0.
    # Attach only whole unclaimed island components close to one country.
    geoms = [clean(shape(f['geometry'])) for f in rows]
    tree = STRtree(geoms)
    extra = defaultdict(list)
    for f in read('public/data/ne_10m_land.geojson')['features']:
        geometry = shape(f['geometry'])
        for island in getattr(geometry, 'geoms', [geometry]):
            if not 1e-7 < island.area < .03:
                continue
            near = tree.query(island.buffer(.045), predicate='intersects')
            if len(near) != 1 or near[0] not in candidates:
                continue
            i = near[0]
            missing = clean(island.difference(geoms[i]))
            if missing.area > 1e-8:
                extra[i].append(missing)
    for i, islands in extra.items():
        rows[i]['geometry'] = mapping(clean(unary_union([geoms[i], *islands])))
    write(PATH, data)
    print(f'{len(candidates)} matched states; {sum(map(len, extra.values()))} nearshore island pieces restored')


if __name__ == '__main__':
    main()
