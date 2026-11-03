"""Offline Wikidata enrichment with preserved date qualifiers and claim provenance."""
import concurrent.futures,hashlib,json,pathlib,re,sys,time,urllib.parse,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.local/python'))
from opencc import OpenCC
CC=OpenCC('t2s');CACHE=ROOT/'.local/wikidata';CACHE.mkdir(exist_ok=True)
PROPS={'P122':'government','P140':'religion','P1142':'ideology','P36':'capital','P35':'ruler','P6':'headOfGovernment','P37':'language','P172':'ethnicity','P463':'membership','P607':'conflict','P41':'flag','P94':'arms','P571':'founded','P576':'dissolved','P31':'instanceOf'}

def request(url):
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'GuanlanAtlas/1.2 (local historical research)'})
            with urllib.request.urlopen(req,timeout=45) as response:return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code==429:
                if attempt==2:raise
                time.sleep(min(60,max(20,int(error.headers.get('Retry-After','60')))));continue
            if attempt==2:raise
            time.sleep(2*(attempt+1))
        except Exception:
            if attempt==2:raise
            time.sleep(2*(attempt+1))

def batch(ids,props='labels|descriptions|claims'):
    key=hashlib.sha256((props+'|'.join(ids)).encode()).hexdigest()[:20];path=CACHE/(key+'.json')
    if path.exists():return json.loads(path.read_text(encoding='utf-8'))
    query={'action':'wbgetentities','ids':'|'.join(ids),'props':props,'languages':'zh-hans|zh|en','format':'json'}
    time.sleep(1.5)
    result=request('https://www.wikidata.org/w/api.php?'+urllib.parse.urlencode(query))['entities']
    path.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8');return result

def load_many(ids,props='labels|descriptions|claims'):
    ids=sorted(set(ids));groups=[ids[i:i+40] for i in range(0,len(ids),40)];result={}
    def safe(group):
        try:return batch(group,props)
        except Exception as error:print('Skipped batch after retries:',str(error),flush=True);return {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1)as pool:
        for i,data in enumerate(pool.map(safe,groups),1):
            result.update(data)
            if i%8==0:print(f'Wikidata {props}: {i}/{len(groups)} batches',flush=True)
    return result

def label(entity):
    values=entity.get('labels',{})
    return CC.convert(next((values[k]['value'] for k in ['zh-hans','zh','en'] if k in values),entity.get('id','')))
def year(value):
    if not isinstance(value,dict)or'time'not in value:return None
    found=re.match(r'([+-])(\d+)-',value['time'])
    return (-1 if found[1]=='-'else 1)*int(found[2]) if found else None
def value(snak):return snak.get('datavalue',{}).get('value')
def simplify(claim):
    v=value(claim.get('mainsnak',{}));qual=claim.get('qualifiers',{})
    if v is None or claim.get('rank')=='deprecated':return None
    def date(prop):return next((year(value(x))for x in qual.get(prop,[])if year(value(x))is not None),None)
    qid=v.get('id') if isinstance(v,dict)else None
    sources=[value(s)for ref in claim.get('references',[])for s in ref.get('snaks',{}).get('P854',[])if isinstance(value(s),str)]
    return {'value':qid or (year(v)if isinstance(v,dict)and'time'in v else v),'from':date('P580'),'to':date('P582'),'at':date('P585'),'rank':claim.get('rank','normal'),'citation':sources[:3]}

def main():
    polity=json.loads((ROOT/'.local/temporal-entities.json').read_text(encoding='utf-8'))
    ids={p['qid']for p in polity.values()if re.fullmatch(r'Q\d+',p['qid']or'')}
    entities=load_many(ids)
    simplified={};refs=set();leaders=set();conflicts=set()
    for qid,entity in entities.items():
        fields={}
        for prop,name in PROPS.items():
            rows=[simple for c in entity.get('claims',{}).get(prop,[])if(simple:=simplify(c))]
            if rows:fields[name]=rows[:80]
            for row in rows[:80]:
                if isinstance(row['value'],str)and re.fullmatch(r'Q\d+',row['value']):refs.add(row['value'])
                if prop in ['P35','P6']and isinstance(row['value'],str):leaders.add(row['value'])
                if prop=='P607'and isinstance(row['value'],str):conflicts.add(row['value'])
        desc=entity.get('descriptions',{});description=next((desc[k]['value']for k in ['zh-hans','zh','en']if k in desc),'')
        simplified[qid]={'label':label(entity),'en':entity.get('labels',{}).get('en',{}).get('value',''),'description':CC.convert(description),'fields':fields}
    ref_entities=load_many(refs-entities.keys(),'labels')
    labels={qid:label(entity)for qid,entity in {**entities,**ref_entities}.items()}
    for qid,entity in simplified.items():
        for rows in entity['fields'].values():
            for row in rows:row['label']=labels.get(str(row['value']),str(row['value']))
    # Add reign dates from the ruler's own position-held statements when a country's
    # head-of-state field omitted dates. Unscoped current officeholders stay unscoped.
    leader_entities=load_many([qid for qid in leaders if re.fullmatch(r'Q\d+',qid)])
    for entity in simplified.values():
        for field in ['ruler','headOfGovernment']:
            for row in entity['fields'].get(field,[]):
                if row['from']is not None or row['to']is not None:continue
                candidates=[]
                for claim in leader_entities.get(row['value'],{}).get('claims',{}).get('P39',[]):
                    simple=simplify(claim)
                    if simple and simple['from']is not None:candidates.append(simple)
                row['positionReferences']=candidates[:15]
    output=ROOT/'public/data/polity-facts.json'
    output.write_text(json.dumps({'source':'Wikidata','license':'CC0','entities':simplified,'labels':labels},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (ROOT/'.local/wikidata-conflict-ids.json').write_text(json.dumps(sorted(conflicts)),encoding='utf-8')
    print('Enriched polities:',len(simplified),'labelled references:',len(labels),'conflicts:',len(conflicts),flush=True)

if __name__=='__main__':main()
