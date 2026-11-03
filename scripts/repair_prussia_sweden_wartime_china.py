"""Correct annual archive and territory records for the reported map issues."""
from territory_repair_stage import clean, read, write
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

TAG = 'prussia-sweden-china-review'
SWEDEN = 'https://www.kungahuset.se/english/the-monarchy-of-sweden'
YANAN = 'https://digicoll.lib.berkeley.edu/record/58534/files/CRM_36.pdf'
XINJIANG = 'https://www.mh.sinica.edu.tw/MHDocument/PublicationDetail/PublicationDetail_750.pdf'


def swedish_rulers():
    path = 'public/data/polity-facts.json'
    data = read(path)
    terms = [
        ('古斯塔夫二世·阿道夫',1611,1632), ('克里斯蒂娜',1632,1654),
        ('卡尔十世·古斯塔夫',1654,1660), ('卡尔十一世',1660,1697),
        ('卡尔十二世',1697,1718), ('乌尔丽卡·埃莱奥诺拉',1718,1720),
        ('弗雷德里克一世',1720,1751), ('阿道夫·弗雷德里克',1751,1771),
        ('古斯塔夫三世',1771,1792), ('古斯塔夫四世·阿道夫',1792,1809),
    ]
    for q in ('Q215443','Q34'):
        rows = data['entities'][q]['fields'].setdefault('ruler',[])
        rows[:] = [r for r in rows if r.get('supplement') != TAG]
        rows.extend({'value':name,'label':name,'from':start,'to':end,'at':None,
                     'roleLabel':'瑞典君主','citation':[SWEDEN],'supplement':TAG}
                    for name,start,end in terms)
    write(path,data)


def wartime_china():
    path = 'public/data/temporal/19.geojson'
    shard = read(path)
    for year in range(1938,1946):
        frame = {p['NAME']:f for f in shard['features'] if
                 (p:=f['properties'])['validFrom'] == p['validTo'] == year}
        base = frame['Communist Party of China']
        if base['properties'].get('geometryCorrection') == TAG:
            continue
        geometry = shape(base['geometry'])
        parts = list(geometry.geoms)
        west = unary_union([clean(g) for g in parts if g.bounds[2] < 100])
        border_region = unary_union([clean(g) for g in parts if g.bounds[2] >= 100])
        assert not west.is_empty and not border_region.is_empty
        base['geometry'] = mapping(border_region)
        base['properties'].pop('labelPath',None)
        base['properties'].update(displayName='中共抗日根据地',mapLabel='中共抗日根据地',
            geometryCorrection=TAG,sourceUrl=YANAN,
            representationNote='图中保留以延安为中心的陕甘宁边区示意。根据地实际范围随战局变化，现有轮廓为概化。')
        roc = frame['Republic of China']
        soviet = frame['Union of Soviet Socialist Republics']
        ili = frame.get('East Turkestan Republic')
        restored = west.difference(clean(shape(ili['geometry']))) if ili else west
        soviet['geometry'] = mapping(clean(shape(soviet['geometry'])).difference(west))
        roc['geometry'] = mapping(clean(shape(roc['geometry'])).union(restored).difference(border_region))
        roc['properties'].update(geometryCorrection=TAG)
        roc['properties'].setdefault('sourceUrl',XINJIANG)
    write(path,shard)


if __name__ == '__main__':
    swedish_rulers()
    wartime_china()


