"""Restore dated Aegean coverage and independent Nauru."""
from territory_repair_stage import clean, read, write
from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union

LAND = 'https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/'
NAURU = 'https://www.un.org/dppa/decolonization/history/former-trust-and-nsgts'
AEGEAN = 'https://www.naxos.gr/byzantine-period/?lang=en'
RECORD = 'nauru-independence-1968-admin0'
NAME = 'Nauru'


def aegean():
    window = box(22.3, 34.7, 28.6, 41.05)
    islands = []
    for f in read('public/data/ne_10m_land.geojson')['features']:
        g = shape(f['geometry'])
        islands.extend(p for p in getattr(g, 'geoms', [g]) if p.area > 1e-6 and window.covers(p))
    path = 'public/data/temporal/11.geojson'
    d = read(path)
    rows = d['features']
    for f in rows:
        p = f['properties']
        if p['NAME'] != 'Byzantine Empire' or not (1100 <= p['validFrom'] <= p['validTo'] <= 1203):
            continue
        rivals = [clean(shape(other['geometry']).intersection(window)) for other in rows
                  if other['properties']['NAME'] != p['NAME']
                  and other['properties']['validFrom'] <= p['validTo']
                  and p['validFrom'] <= other['properties']['validTo']
                  and shape(other['geometry']).intersects(window)]
        occupied = unary_union(rivals)
        g = clean(shape(f['geometry']))
        patches = [island for island in islands if not g.covers(island)
                   and island.intersection(occupied).area < 1e-9]
        if patches:
            f['geometry'] = mapping(clean(unary_union([g, *patches])))
            p.update(coastalReference=LAND, historicalIslandGeometry='aegean-byzantine-core',
                     aegeanCoverageSource=AEGEAN,
                     representationNote='爱琴海核心岛屿按12世纪拜占庭统治期补绘，保留同期源图已注明的其他势力。')
    write(path,d)


def nauru():
    base = next(f for f in read('.local/presentation/admin0.geojson')['features']
                if f['properties'].get('WIKIDATAID') == 'Q697')
    f = {'type':'Feature','geometry':base['geometry'],'properties':{
        'NAME':NAME,'SUBJECTO':NAME,'qid':'Q697','entityId':'Q697','displayName':'瑙鲁',
        'validFrom':1968,'validTo':2024,'sourceRecord':RECORD,'sourceUrl':NAURU,
        'coastalReference':'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/',
        'representationNote':'1968年独立。地图采用自然地球地理底图的岛屿轮廓。'}}
    existed = False
    for century in (19,20):
        path=f'public/data/temporal/{century}.geojson'
        d=read(path)
        if any(x['properties'].get('sourceRecord')==RECORD for x in d['features']):
            existed=True
        else:
            d['features'].append(f)
            write(path,d)
    for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
        d=read(path)
        d[NAME]='瑙鲁'
        write(path,d)
    path='public/data/polity-facts.json'
    d=read(path)
    d['labels']['Q697']='瑙鲁'
    d['entities'].setdefault('Q697',{'label':'瑙鲁','en':'Nauru','description':'太平洋岛国，1968年独立。','fields':{}})
    write(path,d)
    if not existed:
        path='public/data/temporal/index.json'
        d=read(path)
        d['counts']['polityRecords']+=1
        d['changeYears']=sorted(set(d['changeYears'])|{1968})
        write(path,d)
        path='public/data/chronology-audit.json'
        d=read(path)
        d['summary']['sourceRecords']+=1
        write(path,d)
    path='public/data/chronology-audit.json'
    d=read(path)
    if not any(row['record']==RECORD for row in d['longIntervals']):
        for key,amount in [('storedShardRows',2),('uniqueDatedRows',1),('polityIdentities',1),('intervalsAtLeast25Years',1)]:
            d['summary'][key]+=amount
        d['regions']['大洋洲']+=1
        for row in d['annualQueryCoverage']:
            if 1968<=row['year']<=2024:
                row['territorialRecords']+=1
        d['longIntervals'].append({'name':NAME,'from':1968,'to':2024,'record':RECORD,'years':57,
                                   'method':'documented-independence','accuracy':'独立日期有出处，岛岸为现代地理参考。'})
        write(path,d)


if __name__=='__main__':
    aegean()
    nauru()
