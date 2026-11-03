"""Fill narrow historical coastal gaps worldwide using dated ownership."""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from territory_repair_stage import clean, read, write
from shapely.errors import GEOSException
from shapely.geometry import box, mapping, shape
from shapely.ops import clip_by_rect, unary_union
from shapely.strtree import STRtree

WIDTH = .12
STEP = 10
TAG = 'world-historical-coast'
SOURCE = 'https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/'


def polygons(g):
    if g.geom_type == 'Polygon':
        return [g] if not g.is_empty else []
    return [p for child in getattr(g, 'geoms', ()) for p in polygons(child)]


def clip(g, bounds):
    try:
        return clean(clip_by_rect(g, *bounds))
    except GEOSException:
        return clean(g.intersection(box(*bounds)))


def shoreline_tiles():
    parts = [p for f in read('public/data/ne_10m_land.geojson')['features']
             for p in polygons(shape(f['geometry']))]
    tree = STRtree(parts)
    tiles = []
    for west in range(-180,180,STEP):
        for south in range(-80,80,STEP):
            cell = box(west,south,west+STEP,south+STEP)
            bounds = cell.buffer(3*WIDTH).bounds
            local = clean(unary_union([clip(parts[i], bounds)
                                       for i in tree.query(box(*bounds))]))
            if local.is_empty or local.covers(cell):
                continue
            # Construct the shore before cutting at the tile edge.
            band = clean(local.boundary.buffer(WIDTH,quad_segs=3).intersection(local).intersection(cell))
            if not band.is_empty:
                tiles.append((bounds,band,polygons(local)))
    return tiles


def refine(century, tiles):
    path=f'public/data/temporal/{century}.geojson'
    data=read(path)
    rows=[f for f in data['features'] if f['properties']['validFrom'] < 2024
          and not f['properties'].get('controlArea')]
    if not any(not f['properties'].get('worldCoastalGeometry') for f in rows):
        return 0
    geoms=[clean(shape(f['geometry'])) for f in rows]
    tree=STRtree(geoms)
    repairs=defaultdict(list)
    for bounds,band,land in tiles:
        candidates=tree.query(box(*bounds),predicate='intersects')
        local=[]
        for i in candidates:
            g=clip(geoms[i], bounds)
            if not g.is_empty:
                local.append((i,g,g.buffer(WIDTH,quad_segs=3)))
        for i,g,reach in local:
            p=rows[i]['properties']
            if p.get('worldCoastalGeometry')==TAG or p.get('representationKind') in {
                    'archaeological-culture','human-presence'}:
                continue
            if g.covers(band) or not reach.intersects(band):
                continue
            # The claimant must already reach this land component. No bridge
            # across open water is inferred from proximity alone.
            attached=[part for part in land if g.intersection(part).area>.0001]
            if not attached:
                continue
            extra=clean(reach.intersection(band).intersection(unary_union(attached)).difference(g))
            if extra.area<.00003:
                continue
            competitors=[]
            for j,_,other_reach in local:
                rival=rows[j]['properties']
                if (rival['NAME']!=p['NAME'] and p['validFrom']<=rival['validTo']
                        and rival['validFrom']<=p['validTo'] and other_reach.intersects(extra)):
                    competitors.append(other_reach)
            patch=clean(extra.difference(unary_union(competitors))) if competitors else extra
            if patch.area>.00003:
                repairs[i].append(patch)
    for i,parts in repairs.items():
        f=rows[i]
        f['geometry']=mapping(clean(unary_union([geoms[i],*parts])))
        f['properties'].update(coastalReference=SOURCE,worldCoastalGeometry=TAG)
    if repairs:
        write(path,data)
    print(century,len(repairs),flush=True)
    return len(repairs)


def main():
    tiles=shoreline_tiles()
    print('coastal tiles',len(tiles),flush=True)
    centuries=[c for c in read('public/data/temporal/index.json')['centuries'] if -40<=c<=20]
    with ThreadPoolExecutor(max_workers=3) as pool:
        total=sum(pool.map(lambda c:refine(c,tiles),centuries))
    print('worldwide coastal repairs',total,flush=True)


if __name__=='__main__':
    main()
