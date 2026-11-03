"""Repair reported chronology gaps using bounded geographic references."""
from copy import deepcopy
from territory_repair_stage import read, write, clean
from shapely.geometry import shape, mapping, box, Point
from shapely.ops import unary_union

TAG='regional-gaps-and-coasts'
IST='https://www.tuba.gov.tr/en/publications/non-periodical-publications/history/local-history-of-the-national-struggle-1918-1923-vol-11-istanbul/inter-allied-occupation-administration-in-istanbul'
MEX='https://guides.loc.gov/chronicling-america-mexican-revolution'
POL='https://www.aph-ihpan.edu.pl/images/APH121/11_Balkelis.pdf'
CHINA='https://en.wikipedia.org/wiki/Second_Zhili%E2%80%93Fengtian_War'
SOM='https://repository.out.ac.tz/409/1/Vol_7._Africa_under_Colonial_Domination_1880-1935_editor_A._ADUBOAHEN.pdf'
reference=read('public/data/world_2010.geojson')['features']
labels={}

def geom(f):return clean(shape(f['geometry']))
def union(gs):return unary_union(list(gs))
def ref(*names):return union(geom(f) for f in reference if f['properties']['NAME'] in names)
def name(f):return f['properties']['NAME']
def active(d,y):return [f for f in d['features'] if f['properties']['validFrom']<=y<=f['properties']['validTo']]
def set_geom(f,g):
    f['geometry']=mapping(clean(g))
    f['properties'].pop('labelPath',None)
    f['properties']['geometryCorrection']=TAG

def gap(region,rows):
    return clean(region.difference(union(geom(f).intersection(region) for f in rows
        if not f['properties'].get('controlArea') and shape(f['geometry']).intersects(region))))

def add(d,base,y,key,qid,label,area,source,note):
    if area.is_empty:return
    existing=next((f for f in active(d,y) if name(f)==key and
                   f['properties'].get('geometryCorrection')==TAG),None)
    if existing:
        set_geom(existing,geom(existing).union(area))
        return
    f=deepcopy(base)
    set_geom(f,area)
    p=f['properties']
    p.update(NAME=key,SUBJECTO=key,displayName=label,mapLabel=label,qid=qid,entityId=qid,
             validFrom=y,validTo=y,sourceUrl=source,accuracy=note,representationNote=note)
    d['features'].append(f)
    labels[key]=label

def main():
    path='public/data/temporal/13.geojson'
    d=read(path)
    blue=next(f for f in active(d,1386) if name(f)=='Blue Horde')
    gold=next(f for f in active(d,1386) if name(f)=='Golden Horde')
    set_geom(gold,geom(gold).union(geom(blue)))
    write(path,d)
    path='public/data/temporal/19.geojson'
    d=read(path)
    poland=next(f for f in active(d,1919) if name(f)=='Second Polish Republic')
    missing=gap(box(22,51.5,30,57),active(d,1919))
    pocket=next((p for p in getattr(missing,'geoms',[missing]) if p.covers(Point(25.28,54.68))),None)
    if pocket is not None:
        set_geom(poland,geom(poland).union(pocket))
        poland['properties'].update(sourceUrl=POL,representationNote='维尔纽斯周边缺口按1919年后期波军控制概化补绘。年内曾由立陶宛—白俄罗斯苏维埃共和国控制。')
    turkey=next(f for f in active(d,1924) if name(f)=='Republic of Turkey')
    # Restore the fine coastline inside the local straits reference window.
    window=box(28.18,40.73,29.95,41.52)
    istanbul=union(geom(f).intersection(window) for f in read('public/data/ne_10m_land.geojson')['features'])
    for y in range(1919,1924):
        rows=active(d,y)
        if y==1923:
            add(d,turkey,y,name(turkey),'Q43','土耳其共和国',gap(istanbul,rows),IST,'1923年末视图，协约国于10月撤出君士坦丁堡。以邻年海岸轮廓补绘城市周边。')
        else:
            base=next(f for f in rows if name(f)=='Ottoman Empire')
            add(d,base,y,'Allied Administration of Constantinople','Q12560','君士坦丁堡（协约国占领）',
                gap(istanbul,rows),IST,'协约国军事占领与行政管理区，轮廓仅示意博斯普鲁斯海峡周边。')
    roc=next(f for f in active(d,1924) if name(f)=='Republic of China')
    provinces=read('public/data/provinces.geojson')['features']
    jiang=union(geom(f) for f in provinces if f['properties'].get('native') in {'Jiangsu','Anhui'})
    remaining=gap(jiang,active(d,1924))
    if not remaining.is_empty:
        set_geom(roc,geom(roc).union(remaining))
        roc['properties'].update(sourceUrl=CHINA,representationNote='苏皖空白按民国省域概化补绘。江浙战争与军阀换防使实际控制在1924—1925年间多次变化。')
    mexico=next(f for f in active(d,1922) if name(f)=='Mexico')
    for y in range(1913,1920):
        add(d,mexico,y,'Mexico','Q96','墨西哥',gap(geom(mexico),active(d,y)),MEX,
            '墨西哥革命时期的国家地域概览。政府与革命各派并存，轮廓不表示中央政府实际控制全国。')
    for y in range(1900,1926):
        rows=active(d,y)
        for key,q,label,region,source,note,parent in [
            ('Southern Arabian Local Polities','local:south-arabian-local-polities','南阿拉伯地方诸势力',
             ref('Yemen','Oman').intersection(box(43.4,12,55.6,18.8)),
             'https://www.britannica.com/place/Yemen/The-age-of-imperialism',
             '以地理范围标示早期20世纪南阿拉伯尚未细分的地方势力，已绘制的苏丹国及殖民行政区优先保留。','Hadrami Sultanates and Tribal Societies'),
            ('Somali Local Polities','local:somali-local-polities','索马里地方诸势力',
             ref('Somalia','Somaliland'),SOM,
             '以地理范围标示早期20世纪索马里尚未细分的地方政治势力，包含德尔维希运动和当地社群活动的历史背景。已有领地优先保留。','Italian Africa')]:
            base=next((f for f in rows if name(f)==parent),None)
            if base:
                area=gap(region,rows)
                if area.area>.015:add(d,base,y,key,q,label,area,source,note)
    land=union(geom(f).intersection(box(177,70.5,180,71.75)).union(geom(f).intersection(box(-180,70.5,-177,71.75)))
        for f in read('public/data/ne_10m_land.geojson')['features'])
    def fill_wrangel(data):
        for f in data['features']:
            p=f['properties']
            if p['validFrom']>=1922 and name(f) in {'Union of Soviet Socialist Republics','Russian Federation','Russia'}:
                g=geom(f)
                if not g.covers(land):set_geom(f,g.union(land))
    for f in d['features']:
        p=f['properties']
        if name(f) in {'Southern Arabian Local Polities','Somali Local Polities','Allied Administration of Constantinople'}:
            for key in ('wikipedia','memberOf','components','sourceAreaKm2','foundedBy'):
                p.pop(key,None)
            if name(f).endswith('Local Polities'):
                p.update(regionalCollection=True,representationKind='regional-polities',inferredBoundary=True)
    fill_wrangel(d)
    write(path,d)
    modern_path='public/data/temporal/20.geojson'
    modern=read(modern_path)
    fill_wrangel(modern)
    write(modern_path,modern)
    for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
        data=read(path)
        data.update(labels)
        write(path,data)

if __name__=='__main__':main()



