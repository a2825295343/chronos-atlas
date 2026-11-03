"""Build offline Chinese labels: Wikipedia interlanguage names, then marked MT drafts.

Public map labels only; original identifiers and research data are never rewritten.
"""
import ast, concurrent.futures, json, pathlib, re, sys, time, urllib.parse
from download_data import get, save, DEST, ROOT
sys.path.insert(0,str(ROOT/'.local'/'python'))
try:
    from opencc import OpenCC
    converter=OpenCC('t2s')
    simplified=converter.convert
except ImportError:
    simplified=lambda text:text

CACHE=ROOT/'.local'/'translations'
CACHE.mkdir(parents=True,exist_ok=True)

def normalize(name):return re.sub(r'\s+',' ',name.strip())
def main():
    names=set()
    for entry in json.loads((DEST/'manifest.json').read_text(encoding='utf-8')):
        for f in json.loads((DEST/entry['filename']).read_text(encoding='utf-8'))['features']:
            for key in ['NAME','SUBJECTO']:
                name=normalize(f['properties'].get(key) or '')
                if name:names.add(name)
    names=sorted(names)
    labels={};provenance={}
    batches=[names[i:i+35] for i in range(0,len(names),35)]
    def wiki_batch(item):
        i,batch=item;file=CACHE/f'wiki-{i}.json'
        if file.exists():return json.loads(file.read_text(encoding='utf-8'))
        query={'action':'query','titles':'|'.join(batch),'prop':'langlinks','lllang':'zh','lllimit':'500','format':'json','redirects':'1'}
        try:
            data=json.loads(get('https://en.wikipedia.org/w/api.php?'+urllib.parse.urlencode(query)))
            redirects={p['from']:p['to'] for p in data.get('query',{}).get('redirects',[])}
            normalized={p['from']:p['to'] for p in data.get('query',{}).get('normalized',[])}
            translations={p['title']:simplified(p['langlinks'][0]['*']) for p in data.get('query',{}).get('pages',{}).values() if p.get('langlinks')}
            result={}
            for name in batch:
                title=normalized.get(name,name)
                for _ in range(4):title=redirects.get(title,title)
                if title in translations:result[name]=translations[title]
            file.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
            return result
        except Exception as error:
            print(f'Wikipedia batch {i}: {type(error).__name__}',flush=True);return {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for i,result in enumerate(pool.map(wiki_batch,enumerate(batches)),1):
            labels.update(result);provenance.update({k:'wikipedia-zh' for k in result})
            if i%10==0:print(f'Wikipedia labels: {i}/{len(batches)} batches, {len(labels)} names',flush=True)
    raw=(ROOT/'src'/'data.ts').read_text(encoding='utf-8')
    manual=ast.literal_eval(re.search(r'export const names:Record<string,string>=(\{[^\n]*\});',raw).group(1))
    overrides=ROOT/'src'/'localization'/'overrides.zh.json'
    if overrides.exists():manual.update(json.loads(overrides.read_text(encoding='utf-8')))
    labels.update(manual);provenance.update({k:'reviewed' for k in manual})
    missing=[name for name in names if name not in labels]
    batches=[missing[i:i+20] for i in range(0,len(missing),20)]
    def translate_batch(item):
        i,batch=item;file=CACHE/f'mt-{i}.json'
        if file.exists():
            cached=json.loads(file.read_text(encoding='utf-8'))
            if list(cached)==batch:return cached
        query={'client':'gtx','sl':'en','tl':'zh-CN','dt':'t','q':'\n'.join(batch)}
        try:
            data=json.loads(get('https://translate.googleapis.com/translate_a/single?'+urllib.parse.urlencode(query)))
            text=''.join(part[0] or '' for part in data[0])
            lines=[line.strip() for line in text.splitlines() if line.strip()]
            if len(lines)!=len(batch):
                result={}
                for name in batch:
                    query['q']=name
                    data=json.loads(get('https://translate.googleapis.com/translate_a/single?'+urllib.parse.urlencode(query)))
                    result[name]=''.join(part[0] or '' for part in data[0]).strip()
            else:result=dict(zip(batch,lines))
            file.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
            return result
        except Exception as error:
            print(f'Translation batch {i}: {type(error).__name__}',flush=True);return {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for i,result in enumerate(pool.map(translate_batch,enumerate(batches)),1):
            labels.update(result);provenance.update({k:'machine-draft' for k in result})
            if i%10==0:print(f'Translated labels: {i}/{len(batches)} batches',flush=True)
    for key,value in labels.items():
        labels[key]=simplified(value)
    transliterations=ROOT/'src'/'localization'/'transliterations.zh.json'
    if transliterations.exists():
        drafts=json.loads(transliterations.read_text(encoding='utf-8'))
        labels.update(drafts);provenance.update({name:'transliteration-draft' for name in drafts})
    folder=ROOT/'src'/'localization';folder.mkdir(exist_ok=True)
    (folder/'names.zh.json').write_text(json.dumps({name:labels.get(name,name) for name in names},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (folder/'provenance.json').write_text(json.dumps({name:provenance.get(name,'untranslated') for name in names},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    unresolved=[name for name in names if not re.search(r'[\u3400-\u9fff]',labels.get(name,''))]
    (CACHE/'unresolved.json').write_text(json.dumps(unresolved,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Labels written: {len(names)}, unresolved: {len(unresolved)}',flush=True)

if __name__=='__main__':main()
