"""Repair narrow shoreline gaps where one dated outline reaches the coast."""
from territory_repair_stage import clean, read, write
from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

TAG = 'historical-mainland-coast-alignment'
SOURCE = 'https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/'
# Eastern Mediterranean and Black Sea. Work windows can be applied independently
# to other regions with the same period and competing-ownership safeguards.
WINDOW = box(17.5, 34, 42, 47)
WIDTH = .14


def main():
    source = read('public/data/ne_10m_land.geojson')['features']
    land = clean(unary_union([shape(f['geometry']).intersection(WINDOW.buffer(.5)) for f in source]))
    components = list(getattr(land, 'geoms', [land]))
    mainland = [g for g in components if g.area >= .15]
    coast = clean(land.boundary.buffer(WIDTH).intersection(land).intersection(WINDOW))
    parts = list(getattr(coast, 'geoms', [coast]))
    coast_index = STRtree(parts)
    record_count = 0
    for century in read('public/data/temporal/index.json')['centuries']:
        if century < -40 or century > 20:
            continue
        path = f'public/data/temporal/{century}.geojson'
        shard = read(path)
        rows = [f for f in shard['features'] if f['properties']['validFrom'] < 2024
                and not f['properties'].get('controlArea')
                and shape(f['geometry']).intersects(WINDOW)]
        geoms = [clean(shape(f['geometry']).intersection(WINDOW.buffer(.5))) for f in rows]
        tree = STRtree(geoms)
        repairs = {}
        for i, (f, g) in enumerate(zip(rows, geoms)):
            p = f['properties']
            if g.is_empty or p.get('historicalCoastGeometry') == TAG or p.get('representationKind') in {
                    'archaeological-culture', 'human-presence'}:
                continue
            band = g.buffer(WIDTH)
            # Require the same landmass, so proximity alone cannot annex an island.
            attached = unary_union([m for m in mainland if g.intersection(m).area > .0002])
            possible = clean(unary_union([parts[j].intersection(band) for j in
                coast_index.query(band, predicate='intersects')]).intersection(attached).difference(g))
            if possible.is_empty:
                continue
            competitors = [geoms[j].buffer(WIDTH) for j in
                           tree.query(possible.buffer(WIDTH), predicate='intersects')
                           if rows[j]['properties']['NAME'] != p['NAME']
                           and rows[j]['properties']['validFrom'] <= p['validTo']
                           and p['validFrom'] <= rows[j]['properties']['validTo']]
            patch = clean(possible.difference(unary_union(competitors)))
            if patch.area > .00004:
                repairs[i] = patch
        for i, patch in repairs.items():
            f = rows[i]
            f['geometry'] = mapping(clean(clean(shape(f['geometry'])).union(patch)))
            f['properties'].update(coastalReference=SOURCE, historicalCoastGeometry=TAG)
        if repairs:
            write(path, shard)
            record_count += len(repairs)
            print(century, len(repairs), flush=True)
    print(f'{record_count} dated mainland shoreline repairs', flush=True)


if __name__ == '__main__':
    main()
