"""Merge Azerbaijan's supplemental coverage into the existing dated state."""
from territory_repair_stage import read, write, clean
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

for century in (19, 20):
    path = f'public/data/temporal/{century}.geojson'
    shard = read(path)
    aliases = [f for f in shard['features'] if f['properties']['NAME'] == 'Azerbaijan'
               and f['properties'].get('qid') == 'Q227']
    for f in shard['features']:
        p = f['properties']
        if p['NAME'] != 'Republic of Azerbaijan' or p.get('qid') != 'Q227':
            continue
        patches = [clean(shape(a['geometry'])) for a in aliases
                   if a['properties']['validFrom'] <= p['validTo']
                   and p['validFrom'] <= a['properties']['validTo']]
        if not patches:
            continue
        assert all(g.equals(patches[0]) for g in patches)
        f['geometry'] = mapping(unary_union([clean(shape(f['geometry'])), patches[0]]))
    write(path, shard)
