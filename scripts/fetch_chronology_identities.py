"""Resolve reviewed, disambiguated article titles; cache source responses for audit.
This does not guess an identity from matching short names.
"""
import json,pathlib,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
TITLES=['Đinh dynasty','Early Lê dynasty','Lý dynasty','Trần dynasty','Hồ dynasty','Post-Angkor period','Kalmyk Khanate','Duchy of Kraków','Tambralinga','Johor Sultanate','Kingdom of Kotte','Kingdom of Dambadeniya','Kingdom of Gampola']
def main():
 p=ROOT/'.local/chronology-successions-identities.json'
 if p.exists():data=json.loads(p.read_bytes())
 else:
  query=urllib.parse.urlencode({'action':'query','format':'json','redirects':1,'prop':'pageprops','ppprop':'wikibase_item','titles':'|'.join(TITLES)})
  req=urllib.request.Request('https://en.wikipedia.org/w/api.php?'+query,headers={'User-Agent':'GuanlanAtlas/1.3 (historical atlas identity review)'})
  with urllib.request.urlopen(req,timeout=60)as r:data=json.load(r)
  p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 for row in data['query']['pages'].values():print(json.dumps([row['title'],row.get('pageprops',{}).get('wikibase_item','MISSING')],ensure_ascii=True))
if __name__=='__main__':main()
