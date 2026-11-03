"""Fill the documented Japanese transition and the missing antimeridian half of Chukotka."""
from territory_repair_stage import read, write, clean
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union

def rows(shard, year, name):
    return [f for f in shard['features'] if (p:=f['properties'])['NAME']==name and p['validFrom']<=year<=p['validTo']]

def set_geometry(f, g):
    f['geometry']=mapping(clean(g))
    f['properties'].pop('labelPath',None)

def main():
    path='public/data/temporal/16.geojson'
    data=read(path)
    reference=shape(rows(data,1602,'Tokugawa Government')[0]['geometry'])
    for f in rows(data,1600,'Tokugawa Government')+rows(data,1601,'Tokugawa Government'):
        set_geometry(f,shape(f['geometry']).union(reference))
        f['properties'].update(
            representationNote='关原之战后形成的德川主导格局。补绘日本本州、四国及九州的缺失区域，以1602年底图为轮廓参考；各大名仍保有领国。1600年采用年末视图。',
            sourceUrl='https://www.britannica.com/event/Battle-of-Sekigahara')
    write(path,data)
    modern=read('public/data/world_2010.geojson')
    reference=unary_union([clean(shape(f['geometry'])) for f in modern['features'] if f['properties']['NAME']=='Russia'])
    tip=reference.intersection(box(-180,63,-168,72))
    for century in (19,20):
        path=f'public/data/temporal/{century}.geojson'
        data=read(path)
        for f in data['features']:
            p=f['properties']
            if p['NAME'] in {'Union of Soviet Socialist Republics','Russian Federation','Russia'} and p['validFrom']>=1922:
                g=clean(shape(f['geometry']))
                if not g.covers(tip):
                    set_geometry(f,g.union(tip))
        write(path,data)

if __name__=='__main__':
    main()
