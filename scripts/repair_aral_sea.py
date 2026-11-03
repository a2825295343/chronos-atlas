"""Separate the Aral Sea's historical water and modern exposed lakebed."""
from territory_repair_stage import read, write, clean
from shapely.geometry import shape, box, Point, mapping
from shapely.ops import unary_union

SOURCE='https://eros.usgs.gov/earthshots/aral-sea-kazakhstan-and-uzbekistan'
path='public/data/temporal/19.geojson'
soviet=next(f for f in read(path)['features'] if (p:=f['properties'])['NAME']=='Union of Soviet Socialist Republics'
            and p['validFrom']<=1950<=p['validTo'])
region=box(57,42,63,48)
holes=region.difference(clean(shape(soviet['geometry'])))
old=next(g for g in getattr(holes,'geoms',[holes]) if g.covers(Point(60,45)))
source=read('public/data/world_2010.geojson')
lakes=read('public/data/ne_10m_lakes.geojson')
modern_water=unary_union([clean(shape(f['geometry'])).intersection(old) for f in lakes['features']
                         if shape(f['geometry']).intersects(old)])
write('public/data/aral-historical-water.geojson',{'type':'FeatureCollection','features':[
    {'type':'Feature','geometry':mapping(old),'properties':{'source':SOURCE,'name':'咸海','year':1950}}]})
for century in (19,20):
    path=f'public/data/temporal/{century}.geojson'
    d=read(path)
    for f in d['features']:
        p=f['properties']
        if p['NAME'] not in {'Kazakhstan','Uzbekistan','Republic of Uzbekistan'} or p['validTo']<1992:
            continue
        country=next(x for x in source['features'] if x['properties']['NAME']==p['NAME'].removeprefix('Republic of '))
        dry=clean(shape(country['geometry'])).intersection(old).difference(modern_water)
        f['geometry']=mapping(clean(shape(f['geometry'])).union(dry))
        p['geometryCorrection']='aral-sea-historical-shore'
    write(path,d)




