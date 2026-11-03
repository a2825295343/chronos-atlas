"""Named leadership phases for the newly separated Japanese forces."""
import json,urllib.request,urllib.parse
from territory_repair_stage import ROOT,read,write
from prepare_global_archive_review import human
CACHE=ROOT/'.local/japanese-polities';TAG='japanese-leaders-2026-11-01'
ROSTERS={
 'local:jp-oda':[('Oda Nobunaga','织田信长',1559,1582),('Oda Nobukatsu','织田信雄',1583,1589)],
 'local:jp-takeda':[('Takeda Nobutora','武田信虎',1507,1541),('Takeda Shingen','武田信玄',1541,1573),('Takeda Katsuyori','武田胜赖',1573,1582)],
 'local:jp-nagao':[('Nagao Tamekage','长尾为景',1507,1536),('Nagao Harukage','长尾晴景',1536,1548),('Uesugi Kenshin','长尾景虎（上杉谦信）',1548,1560)],
 'local:jp-uesugi':[('Uesugi Kenshin','上杉谦信',1561,1578),('Uesugi Kagekatsu','上杉景胜',1578,1597)],
 'local:jp-tokugawa':[('Tokugawa Ieyasu','德川家康',1560,1599)],
 'local:tokugawa-government':[('Tokugawa Ieyasu','德川家康',1600,1602)],
 'local:jp-toyotomi':[('Toyotomi Hideyoshi','羽柴／丰臣秀吉',1583,1598),('Toyotomi Hideyori','丰臣秀赖',1598,1599)],
 'local:jp-mori':[('Mōri Motonari','毛利元就',1555,1571),('Mōri Terumoto','毛利辉元',1571,1599)],
 'local:jp-imagawa':[('Imagawa Yoshimoto','今川义元',1536,1560),('Imagawa Ujizane','今川氏真',1560,1568)],
 'local:jp-date':[('Date Terumune','伊达辉宗',1565,1584),('Date Masamune','伊达政宗',1584,1599)],
 'local:jp-saito':[('Saitō Dōsan','斋藤道三',1542,1556),('Saitō Yoshitatsu','斋藤义龙',1556,1561),('Saitō Tatsuoki','斋藤龙兴',1561,1567)],
 'local:jp-chosokabe':[('Chōsokabe Motochika','长宗我部元亲',1575,1599)],
}

def main():
 path=CACHE/'verified-people.json';pool=json.loads(path.read_bytes())if path.exists()else{};bytitle={e.get('sitelinks',{}).get('enwiki',{}).get('title'):q for q,e in pool.items()};wanted={n for rs in ROSTERS.values()for n,l,a,b in rs};missing=wanted-bytitle.keys()
 if missing:
  params=urllib.parse.urlencode({'action':'wbgetentities','format':'json','sites':'enwiki','titles':'|'.join(sorted(missing)),'props':'labels|claims|sitelinks','languages':'zh-hans|zh|en','redirects':'yes'})
  with urllib.request.urlopen(urllib.request.Request('https://www.wikidata.org/w/api.php?'+params,headers={'User-Agent':'GuanlanAtlas/1.9 educational history atlas'}),timeout=40)as r:d=json.load(r)
  pool.update({q:e for q,e in d['entities'].items()if human(e)});path.write_text(json.dumps(pool,ensure_ascii=False),encoding='utf8');bytitle={e.get('sitelinks',{}).get('enwiki',{}).get('title'):q for q,e in pool.items()}
 facts=read('public/data/polity-facts.json');records=[]
 for country,rows in ROSTERS.items():
  e=facts['entities'][country];existing=[r for r in e['fields'].get('ruler',[])if r.get('supplement')!=TAG];new=[]
  for name,cn,a,b in rows:
   q=bytitle.get(name)
   if not q:raise ValueError('Unresolved exact named person: '+name)
   source='https://en.wikipedia.org/wiki/'+urllib.parse.quote(name.replace(' ','_'))
   row={'value':q,'label':cn,'from':a,'to':b,'at':None,'rank':'preferred','roleLabel':'幼年名义继承者；政务由五大老、奉行等参与处理'if name=='Toyotomi Hideyori'else'该势力的主导者；不一概等同正式家督任期','citation':[source,'https://www.wikidata.org/wiki/'+q],'supplement':TAG,'inference':'按该势力主导阶段补录；继承或实际掌权与家督让位不完全一致，交接年允许先后任职者并列。'};new.append(row);facts['labels'][q]=cn;records.append({'country':country,**row})
  kept=[]
  for r in existing:
   if r.get('kind')!='collective':kept.append(r);continue
   spans=[(r['from'],r['to'])]
   for a,b in [(v['from'],v['to'])for v in new]:spans=[seg for lo,hi in spans for seg in [(lo,min(hi,a-1)),(max(lo,b+1),hi)]if seg[0]<=seg[1]]
   kept.extend({**r,'from':a,'to':b}for a,b in spans)
  e['fields']['ruler']=kept+new
 write('public/data/polity-facts.json',facts);write('public/data/japanese-leader-review.json',{'reviewedAt':'2026-11-01','records':records,'summary':{'appointments':len(records),'people':len({r['value']for r in records})}});print('Named Japanese leadership phases',len(records),flush=True)

if __name__=='__main__':main()
