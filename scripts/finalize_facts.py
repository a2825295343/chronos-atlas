"""Resolve verified entity IDs, office-specific ruler terms, and new Chinese labels."""
import json,pathlib,re,sys,urllib.parse,concurrent.futures,hashlib
from enrich_polities import ROOT,load_many,label,simplify,CC
from download_data import get

def main():
    path=ROOT/'public/data/polity-facts.json';data=json.loads(path.read_text(encoding='utf-8'))
    raw={}
    for file in (ROOT/'.local/wikidata').glob('*.json'):
        for qid,entity in json.loads(file.read_text(encoding='utf-8')).items():
            if entity.get('claims'):raw[qid]=entity
    extra=load_many(['Q2277','Q7209','Q1064825','Q145','Q161885','Q174193']);raw.update(extra)
    from enrich_polities import PROPS
    refs=set()
    for qid,entity in extra.items():
        fields={}
        for prop,name in PROPS.items():
            rows=[simple for claim in entity.get('claims',{}).get(prop,[])if(simple:=simplify(claim))]
            if rows:fields[name]=rows[:80]
            refs.update(row['value'] for row in rows if isinstance(row['value'],str)and re.fullmatch(r'Q\d+',row['value']))
        data['entities'][qid]={'label':label(entity),'en':entity.get('labels',{}).get('en',{}).get('value',''),'description':CC.convert(entity.get('descriptions',{}).get('zh',{}).get('value','')),'fields':fields}
    missing=refs-data['labels'].keys();newrefs=load_many(missing,'labels')
    data['labels'].update({q:label(e)for q,e in {**extra,**newrefs}.items()})
    derived=0
    for qid,entity in data['entities'].items():
        country=raw.get(qid,{}).get('claims',{})
        for field,prop in [('ruler','P1906'),('headOfGovernment','P1313')]:
            offices={s['value']for claim in country.get(prop,[])if(s:=simplify(claim))}
            rows=entity['fields'].get(field,[]); additions=[]
            for row in rows:
                if row['from'] is not None or row['to'] is not None:continue
                for claim in raw.get(row['value'],{}).get('claims',{}).get('P39',[]):
                    term=simplify(claim)
                    if term and term['value'] in offices and term['from'] is not None:
                        additions.append({**row,'from':term['from'],'to':term['to'],'citation':term['citation']or row['citation'],'dateSource':'office-matched P39 / '+str(term['value'])});derived+=1
            if additions:entity['fields'][field]=list({(r['value'],r['from'],r['to'],r['at']):r for r in rows+additions}.values())
        for rows in entity['fields'].values():
            for row in rows:row['label']=data['labels'].get(str(row['value']),str(row['value']))
    data['officeMatchedTerms']=derived
    path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    polities=json.loads((ROOT/'.local/temporal-entities.json').read_text(encoding='utf-8'))
    folder=ROOT/'src/localization';labels=json.loads((folder/'names.zh.json').read_text(encoding='utf-8'));provenance=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
    for name,p in polities.items():
        entity=data['entities'].get(p['qid'])
        if name not in labels and entity and re.search('[\u3400-\u9fff]',entity['label']):labels[name]=entity['label'];provenance[name]='wikidata-zh'
    dip=json.loads((ROOT/'public/data/diplomacy.json').read_text(encoding='utf-8'))
    names=set(polities)|set(dip['countries'].values())|{r['name']for r in dip['wars']}|{r['fromName']for r in dip['alliances']}|{r['toName']for r in dip['alliances']}
    missing=sorted(name for name in names if name not in labels)
    def translate(batch):
        cache=ROOT/'.local/translations'/('temporal-'+hashlib.sha256('|'.join(batch).encode()).hexdigest()[:12]+'.json')
        if cache.exists():return json.loads(cache.read_text(encoding='utf-8'))
        query={'client':'gtx','sl':'en','tl':'zh-CN','dt':'t','q':'\n'.join(batch)}
        result=json.loads(get('https://translate.googleapis.com/translate_a/single?'+urllib.parse.urlencode(query)))
        lines=''.join(p[0]or''for p in result[0]).strip().splitlines()
        if len(lines)!=len(batch):
            return {name:translate([name])[name]for name in batch} if len(batch)>1 else {batch[0]:''.join(lines)}
        output={name:CC.convert(v.strip())for name,v in zip(batch,lines)}
        cache.write_text(json.dumps(output,ensure_ascii=False),encoding='utf-8');return output
    batches=[missing[i:i+20]for i in range(0,len(missing),20)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        for result in pool.map(translate,batches):labels.update(result);provenance.update({n:'machine-draft'for n in result})
    overrides={'United Kingdom of Great Britain and Ireland':'大不列颠及爱尔兰联合王国','United Kingdom':'英国','Kingdom of Great Britain':'大不列颠王国','Roman Empire':'罗马帝国','Han Dynasty':'汉朝','Han':'韩（战国）','Ming Dynasty':'明朝','Qing Dynasty':'清朝','Four Oirats':'瓦剌四部','Livonian Confederation':'利沃尼亚邦联','Golden Horde':'金帐汗国','Chagatai Khanate':'察合台汗国','Union of Soviet Socialist Republics':'苏维埃社会主义共和国联盟','Russian Federation':'俄罗斯联邦','Kingdom of England':'英格兰王国','Kingdom of France':'法兰西王国','Polish–Lithuanian Commonwealth':'波兰立陶宛联邦','First World War':'第一次世界大战','World War I':'第一次世界大战','World War II':'第二次世界大战'}
    labels.update(overrides);provenance.update({n:'reviewed'for n in overrides})
    (folder/'temporal.zh.json').write_text(json.dumps({n:labels[n]for n in sorted(names|set(overrides))},ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Final facts',len(data['entities']),'office-matched reigns',derived,'newly translated',len(missing),'total polity labels',len(names),flush=True)
if __name__=='__main__':main()
