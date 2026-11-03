"""Build dated polity shards from Seshat Cliopatria; preserve upstream data separately."""
import collections,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.local/python'))
from shapely.geometry import shape,mapping
from shapely import make_valid

def main():
    source=ROOT/'.local/cliopatria.geojson'
    collection=json.loads(source.read_bytes())
    output=ROOT/'public/data/temporal';output.mkdir(parents=True,exist_ok=True)
    buckets=collections.defaultdict(list);entities={};relations=[];issues=[];counts=collections.Counter()
    for i,feature in enumerate(collection['features']):
        p=feature['properties'];name=p['Name'].strip();start=int(p['FromYear']);end=int(p['ToYear'])
        counts['sourceRecords']+=1
        if start>end:issues.append({'id':i,'name':name,'problem':'reversed dates'});continue
        if p['Type']=='RELATION':
            relations.append({'name':name,'from':start,'to':end,'members':p.get('Components','').split(';'),'source':'Cliopatria'});counts['relationRecordsExcludedFromTerritory']+=1;continue
        if name.startswith('(') and p.get('Components'):
            counts['aggregateTerritoriesExcluded']+=1;continue
        g=shape(feature['geometry'])
        if g.is_empty:issues.append({'id':i,'name':name,'problem':'empty geometry'});continue
        if not g.is_valid:g=make_valid(g);counts['geometriesRepaired']+=1
        if g.geom_type=='GeometryCollection':
            from shapely import union_all
            g=union_all([part for part in g.geoms if part.geom_type in ['Polygon','MultiPolygon']])
        if g.geom_type not in ['Polygon','MultiPolygon']:issues.append({'id':i,'name':name,'problem':'non-polygon geometry'});continue
        west,south,east,north=g.bounds
        if not(-180.001<=west<=east<=180.001 and -90.001<=south<=north<=90.001):issues.append({'id':i,'name':name,'problem':'invalid coordinate bounds'});continue
        qid={'Roman Empire':'Q2277','Han Dynasty':'Q7209','Livonian Confederation':'Q1064825'}.get(name,p.get('Wikidata',''));wiki=p.get('Wikipedia','');parent=p.get('MemberOf','')
        if name=='Roman Empire':start=max(start,-27)
        if name=='Han Dynasty':
            end=min(end,220)
            if 9<=start and end<=23:continue
            if start<9 and end<=23:end=min(end,8)
            elif 9<=start<=23:start=25
        if start>end:continue
        props={'NAME':name,'SUBJECTO':name,'entityId':qid or name,'qid':qid,'validFrom':start,'validTo':end,'source':'Cliopatria','sourceRecord':i,'sourceAreaKm2':p.get('Area'),'wikipedia':wiki,'memberOf':parent,'components':p.get('Components','')}
        geometry=mapping(g.simplify(.012,preserve_topology=True))
        row={'type':'Feature','id':i,'properties':props,'geometry':geometry}
        for century in range(start//100,end//100+1):buckets[century].append(row)
        entry=entities.setdefault(name,{'qid':qid,'wikipedia':wiki,'from':start,'to':end,'maxArea':0})
        entry['from']=min(entry['from'],start);entry['to']=max(entry['to'],end);entry['maxArea']=max(entry['maxArea'],p.get('Area') or 0)
        counts['polityRecords']+=1
    for century,rows in buckets.items():
        (output/f'{century}.geojson').write_text(json.dumps({'type':'FeatureCollection','features':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    changes=sorted({f['properties']['validFrom']for rows in buckets.values()for f in rows}|{f['properties']['validTo']+1 for rows in buckets.values()for f in rows})
    index={'source':'Seshat Global History Databank · Cliopatria','url':'https://github.com/Seshat-Global-History-Databank/cliopatria','license':'CC BY 4.0','from':-3400,'to':2024,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'centuries':sorted(buckets),'changeYears':changes,'counts':dict(counts)}
    (output/'index.json').write_text(json.dumps(index,ensure_ascii=False),encoding='utf-8')
    (ROOT/'.local/temporal-entities.json').write_text(json.dumps(entities,ensure_ascii=False),encoding='utf-8')
    (output/'relations.json').write_text(json.dumps(relations,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    audit={'scope':'全量结构、日期与几何检查；不等于逐条史实专家审定','sourceCounts':dict(counts),'issues':issues,'legacyFindings':[{'severity':'high','years':[1279,1300,1400],'problem':'SUBJECTO=Mongol Empire merges nominal relations into a fictitious unified territory.'},{'severity':'high','years':[1400],'problem':'Great Khanate polygon still includes Ming China; snapshot was incorrectly reused at 1444.'}],'rejectedReferenceData':[{'source':'g-lanza/InvaderGIS','reason':'Sample Abbasid geometry has swapped coordinates and its 750–1258 capital is listed as Cairo; not imported.'}]}
    (ROOT/'public/data/data-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'counts':dict(counts),'issues':len(issues),'shards':len(buckets),'entities':len(entities)}),flush=True)

if __name__=='__main__':main()
