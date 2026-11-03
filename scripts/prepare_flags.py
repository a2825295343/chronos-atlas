"""Cache Commons flag images and their source/license metadata; reject fictional flags."""
import collections,concurrent.futures,hashlib,html,json,pathlib,re,time,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
def get(url):
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'GuanlanAtlas/1.2 (historical atlas; local research)'})
            with urllib.request.urlopen(req,timeout=35)as response:return response.read()
        except Exception:
            if attempt==2:raise
            time.sleep(2+attempt)
def year(snak):
    time_value=snak.get('datavalue',{}).get('value',{}).get('time','')
    match=re.match(r'([+-])(\d+)-',time_value)
    return int(match[2])*(-1 if match[1]=='-'else 1)if match else None
def plain(value):return html.unescape(re.sub('<[^>]+>','',value or ''))
def main():
    entities={}
    for path in (ROOT/'.local/wikidata').glob('*.json'):
        for qid,e in json.loads(path.read_text(encoding='utf-8')).items():
            if e.get('claims'):entities[qid]=e
    records=[];files=set();excluded=[]
    for qid,e in entities.items():
        for claim in e.get('claims',{}).get('P41',[]):
            if claim.get('rank')=='deprecated':continue
            file=claim.get('mainsnak',{}).get('datavalue',{}).get('value')
            if not isinstance(file,str):continue
            if re.search(r'fictit|fiction|imaginary|proposed|fantasy|unofficial',file,re.I):excluded.append(file);continue
            qualifiers=claim.get('qualifiers',{})
            def date(prop):return next((year(s)for s in qualifiers.get(prop,[])if year(s)is not None),None)
            record={'qid':qid,'file':file,'from':date('P580'),'to':date('P582'),'at':date('P585'),'rank':claim.get('rank','normal'),'source':'https://www.wikidata.org/wiki/'+qid+'#P41','commons':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(file.replace(' ','_'))}
            records.append(record);files.add(file)
    files=sorted(files);infos={};cache=ROOT/'.local/commons';cache.mkdir(exist_ok=True)
    for i in range(0,len(files),40):
        part=files[i:i+40];key=hashlib.sha256('|'.join(part).encode()).hexdigest()[:16];path=cache/(key+'.json')
        try:
            if path.exists():data=json.loads(path.read_text(encoding='utf-8'))
            else:
                query={'action':'query','titles':'|'.join('File:'+f for f in part),'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':400,'format':'json','redirects':1}
                data=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(query)));path.write_text(json.dumps(data),encoding='utf-8')
                time.sleep(.5)
            normalized={p['from']:p['to']for p in data.get('query',{}).get('normalized',[])}
            redirects={p['from']:p['to']for p in data.get('query',{}).get('redirects',[])}
            pages={p['title']:p for p in data.get('query',{}).get('pages',{}).values()}
            for file in part:
                name=normalized.get('File:'+file,'File:'+file)
                for _ in range(3):name=redirects.get(name,name)
                page=pages.get(name,{})
                if page.get('imageinfo'):infos[file]=page['imageinfo'][0]
            print(f'Flag metadata {min(i+40,len(files))}/{len(files)}',flush=True)
        except Exception as error:print('Flag metadata batch unavailable:',str(error),flush=True)
    destination=ROOT/'public/data/flags';destination.mkdir(exist_ok=True)
    def image(file):
        info=infos.get(file)
        if not info:return file,None
        meta=info.get('extmetadata',{});description=plain(meta.get('ImageDescription',{}).get('value',''))
        if re.search(r'fictitious|fictional|imaginary flag',description,re.I):return file,None
        url=info.get('thumburl')or info['url'];extension='.svg'if urllib.parse.urlsplit(url).path.lower().endswith('.svg')else'.png'
        name=hashlib.sha256(file.encode()).hexdigest()[:20]+extension;path=destination/name
        try:
            if not path.exists():path.write_bytes(get(url))
            return file,{'path':'/data/flags/'+name,'license':plain(meta.get('LicenseShortName',{}).get('value','See Commons source')),'artist':plain(meta.get('Artist',{}).get('value','')),'description':description[:500]}
        except Exception as error:return file,None
    with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:images=dict(pool.map(image,files))
    by_entity=collections.defaultdict(list)
    for record in records:
        if images.get(record['file']):by_entity[record['qid']].append({**record,**images[record['file']]})
    result={'entities':dict(by_entity),'count':sum(bool(value)for value in images.values()),'excludedFictionalFiles':sorted(set(excluded)),'policy':'没有适用年代的旗帜只作条目参考；虚构旗帜不作为史实国旗。每幅图像保留原始许可及来源。'}
    (ROOT/'public/data/flags.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('Flags cached:',result['count'],'entities:',len(by_entity),'rejected fictional:',len(set(excluded)),flush=True)
if __name__=='__main__':main()
