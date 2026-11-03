"""Reconcile Luxembourg's shared borders and restore Baikonur's sovereign fill."""
from territory_repair_stage import clean, read, write
from shapely.geometry import Polygon, box, mapping, shape
from shapely.ops import unary_union

PATH='public/data/temporal/20.geojson'
SOURCE='https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/'
LEASE='https://old.adilet.zan.kz/rus/docs/U950002195_'
NEIGHBORS={'Q32','Q31','Q142','Q183'}


def main():
    d=read(PATH)
    references={f['properties']['WIKIDATAID']:clean(shape(f['geometry']))
                for f in read('.local/presentation/admin0.geojson')['features']
                if f['properties'].get('WIKIDATAID') in NEIGHBORS|{'Q165413'}}
    modern={f['properties'].get('qid'):f for f in d['features']
            if f['properties']['validFrom']==2024 and f['properties'].get('qid') in NEIGHBORS}
    original=shape(modern['Q32']['geometry'])
    neighborhood=box(*original.union(references['Q32']).bounds).buffer(.02)
    for q,f in modern.items():
        old=clean(shape(f['geometry']))
        g=clean(old.difference(neighborhood).union(references[q].intersection(neighborhood)))
        f['geometry']=mapping(g)
        f['properties'].update(coastalReference=SOURCE,boundaryGeometry='natural-earth-modern-admin0')
        if q=='Q32':
            f['properties'].pop('labelPath',None)

    for f in d['features']:
        p=f['properties']
        if p['NAME']!='Kazakhstan':
            continue
        territory=clean(shape(f['geometry']))
        leased=references['Q165413']
        holes=[Polygon(ring) for part in getattr(territory,'geoms',[territory]) for ring in part.interiors]
        exact_holes=[hole for hole in holes if hole.symmetric_difference(leased).area < 1e-8]
        if exact_holes:
            f['geometry']=mapping(clean(territory.union(unary_union(exact_holes))))
        if exact_holes or p.get('baikonurLeaseSource'):
            p.update(baikonurLeaseSource=LEASE,
                     representationNote='拜科努尔位于哈萨克斯坦境内，相关设施由俄罗斯租用和管理，租借期延至2050年。地图底色按哈萨克斯坦主权显示。')
    write(PATH,d)


if __name__=='__main__':
    main()

