"""Align contemporary coastlines to Natural Earth without redrawing inland borders."""
from territory_repair_stage import read, write, clean
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

PATH = 'public/data/temporal/20.geojson'
SOURCE = 'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/'
TAG = 'natural-earth-modern-coast'


def main():
    data = read(PATH)
    rows = [f for f in data['features'] if f['properties']['validFrom'] == 2024
            and not f['properties'].get('controlArea')]
    territory = [clean(shape(f['geometry'])) for f in rows]
    owners = STRtree(territory)
    admin = {}
    for f in read('.local/presentation/admin0.geojson')['features']:
        qid = f['properties'].get('WIKIDATAID')
        admin.setdefault(qid, []).append(clean(shape(f['geometry'])))
    coasts = [part for f in read('public/data/ne_10m_land.geojson')['features']
              for part in getattr(shape(f['geometry']), 'geoms', [shape(f['geometry'])])]
    coast_index = STRtree(coasts)
    added = removed = count = 0
    for i, (f, original) in enumerate(zip(rows, territory)):
        p = f['properties']
        refs = admin.get(p.get('qid'), [])
        if len(refs) != 1 or original.is_empty or p.get('coastalGeometry') == TAG:
            continue
        # Restrict the operation to the same coast used by the map, in a
        # narrow corridor around already documented territory.
        near = original.buffer(.16)
        parts = [coasts[j] for j in coast_index.query(near, predicate='intersects')]
        if not parts:
            continue
        window = box(*near.bounds).buffer(.24)
        land = unary_union([part.intersection(window) for part in parts])
        coastal = land.boundary.buffer(.11)
        extra = refs[0].intersection(near).intersection(coastal).intersection(land).difference(original)
        if not extra.is_empty:
            claimed = unary_union([territory[j] for j in owners.query(extra, predicate='intersects') if j != i])
            extra = extra.difference(claimed)
        offshore = original.intersection(coastal).difference(land)
        result = clean(original.difference(offshore).union(extra))
        if result.is_empty or (extra.area + offshore.area) < 1e-7:
            continue
        f['geometry'] = mapping(result)
        p.update(coastalReference=SOURCE, coastalGeometry=TAG)
        added += extra.area
        removed += offshore.area
        count += 1
    write(PATH, data)
    print(f'{count} coastlines refined; {added:.4f} square degrees restored, {removed:.4f} offshore removed')


if __name__ == '__main__':
    main()
