"""Restore historical islands supported by each dated outline and the coast layer."""
from collections import defaultdict
from territory_repair_stage import clean, read, write
from shapely.geometry import mapping, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

SOURCE = 'https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/'
TAG = 'historical-island-coast-alignment'


def refine(shard, islands, first, last):
    rows = [f for f in shard['features'] if f['properties']['validFrom'] <= last
            and first <= f['properties']['validTo'] and not f['properties'].get('controlArea')]
    geoms = [clean(shape(f['geometry'])) for f in rows]
    spatial = STRtree(geoms)
    additions = defaultdict(list)
    for island in islands:
        hits = []
        for i in spatial.query(island, predicate='intersects'):
            overlap = island.intersection(geoms[i]).area
            if overlap > 1e-10:
                hits.append((i, overlap))
        for i, overlap in hits:
            p = rows[i]['properties']
            if (p.get('historicalIslandGeometry') == TAG
                    or not .70 <= overlap / island.area < .999
                    or p.get('representationKind') in {'archaeological-culture', 'human-presence'}):
                continue
            if any(rows[j]['properties']['NAME'] != p['NAME']
                   and max(first, p['validFrom'], rows[j]['properties']['validFrom'])
                   <= min(last, p['validTo'], rows[j]['properties']['validTo'])
                   for j, _ in hits):
                continue
            additions[i].append(island)
    for i, parts in additions.items():
        f = rows[i]
        f['geometry'] = mapping(clean(unary_union([geoms[i], *parts])))
        f['properties'].update(coastalReference=SOURCE, historicalIslandGeometry=TAG)
    return len(additions), sum(map(len, additions.values()))


def main():
    islands = []
    for f in read('public/data/ne_10m_land.geojson')['features']:
        geometry = shape(f['geometry'])
        islands.extend(clean(p) for p in getattr(geometry, 'geoms', [geometry])
                       if .00012 <= p.area <= .15)
    records = patches = shards = 0
    for century in read('public/data/temporal/index.json')['centuries']:
        first, last = max(-4000, century * 100), min(2023, century * 100 + 99)
        if first > last:
            continue
        path = f'public/data/temporal/{century}.geojson'
        shard = read(path)
        n, m = refine(shard, islands, first, last)
        if n:
            write(path, shard)
            records += n
            patches += m
            shards += 1
            print(century, n, m, flush=True)
    print(f'{records} records, {patches} island repairs, {shards} shards', flush=True)


if __name__ == '__main__':
    main()

