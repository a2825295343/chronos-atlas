"""Named, dated additions where a broad country office list is insufficient."""
import json,time,urllib.parse,urllib.request
from prepare_global_archive_review import ROOT,fetch,human
from enrich_polities import label
CACHE=ROOT/'.local/reviewed-reigns';CACHE.mkdir(exist_ok=True)
# Country ID, source roster, approximate early chronology, (person article, from, to)
ROSTERS=[
 ('Q62943','Maurya_Empire',True,[('Chandragupta Maurya',-322,-297),('Bindusara',-297,-273),('Ashoka',-268,-232),('Dasharatha Maurya',-232,-224),('Samprati',-224,-215),('Shalishuka',-215,-202),('Devavarman',-202,-195),('Shatadhanvan',-195,-187),('Brihadratha Maurya',-187,-185)]),
 ('Q11774','Gupta_Empire',True,[('Chandragupta I',319,335),('Samudragupta',335,375),('Chandragupta II',375,415),('Kumaragupta I',415,455),('Skandagupta',455,467)]),
 ('Q6806806','List_of_Chola_emperors',True,[('Vijayalaya Chola',848,871),('Aditya I',871,907),('Parantaka I',907,955),('Gandaraditya',955,957),('Arinjaya Chola',956,957),('Sundara Chola',957,970),('Uttama Chola',970,985),('Rajaraja I',985,1014),('Rajendra I',1014,1044),('Rajadhiraja I',1044,1052),('Rajendra II',1052,1064),('Virarajendra',1063,1070),('Kulothunga I',1070,1122),('Vikrama Chola',1118,1135),('Kulothunga II',1133,1150),('Rajaraja II',1146,1173),('Rajadhiraja II',1166,1178),('Kulothunga III',1178,1218),('Rajaraja III',1216,1256),('Rajendra III',1246,1279)]),
 ('Q83891','List_of_monarchs_of_the_Sasanian_Empire',True,[('Ardashir I',224,242),('Shapur I',240,270),('Hormizd I',270,271),('Bahram I',271,274),('Bahram II',274,293),('Narseh',293,302),('Hormizd II',302,309),('Shapur II',309,379),('Ardashir II',379,383),('Shapur III',383,388),('Bahram IV',388,399),('Yazdegerd I',399,420),('Bahram V',420,438),('Yazdegerd II',438,457),('Peroz I',459,484),('Balash',484,488),('Kavad I',488,496),('Kavad I',498,531),('Khosrow I',531,579),('Hormizd IV',579,590),('Khosrow II',590,590),('Khosrow II',591,628),('Yazdegerd III',632,651)]),
 ('Q184536','Mansa_(title)',True,[('Sundiata Keita',1235,1255),('Mansa Musa',1312,1337),('Mansa Sulayman',1341,1360)]),
 ('Q28573','Sapa_Inca',True,[('Pachacuti',1438,1471),('Topa Inca Yupanqui',1471,1493),('Huayna Capac',1493,1527),('Huáscar',1527,1532),('Atahualpa',1532,1533)]),
 ('Q2608489','List_of_rulers_of_Tenochtitlan',True,[('Acamapichtli',1375,1395),('Huitzilihuitl',1395,1417),('Chimalpopoca',1417,1427),('Itzcoatl',1427,1440),('Moctezuma I',1440,1469),('Axayacatl',1469,1481),('Tizoc',1481,1486),('Ahuitzotl',1486,1502),('Moctezuma II',1502,1520),('Cuitláhuac',1520,1520),('Cuauhtémoc',1520,1521)]),
 ('local:kingdom-of-kotte','Kingdom_of_Kotte',True,[('Parakramabahu VI of Kotte',1412,1467),('Bhuvanekabahu VI of Kotte',1469,1477),('Dharma Parakramabahu IX',1489,1513)]),
 ('local:kingdom-of-kandy','Kingdom_of_Kandy',True,[('Senasammata Vikramabahu',1469,1511),('Jayaweera Astana',1511,1551),('Karaliyadde Bandara',1551,1581)]),
 ('local:yettishar','Yaqub_Beg',False,[('Yaqub Beg',1865,1877)]),
]
def main():
 pool=json.loads((ROOT/'.local/global-archive-review/entities.json').read_bytes());ids_path=CACHE/'title-ids.json';ids=json.loads(ids_path.read_bytes())if ids_path.exists()else{}
 for cached in ['verified-people.json','downloaded-people.json']:
  if(CACHE/cached).exists():pool.update(json.loads((CACHE/cached).read_bytes()))
 aliases={'Sundara Chola':'Parantaka II','Uttama Chola':'Uttama (Chola dynasty)','Kulothunga I':'Kulottunga I','Mansa Sulayman':'Sulayman of Mali','Parakramabahu VI of Kotte':'Parakramabahu VI','Bhuvanekabahu VI of Kotte':'Bhuvanaikabahu VI','Dharma Parakramabahu IX':'Parakramabahu IX','Jayaweera Astana':'Jayaweera Bandara','Karaliyadde Bandara':'Karalliyadde Bandara','Yaqub Beg':'Yakub Beg of Yettishar'}
 # Cached exact English labels are identities, never a fuzzy name match.
 bylabel={e.get('labels',{}).get('en',{}).get('value'):q for q,e in pool.items()if human(e)}
 for _,_,_,rows in ROSTERS:
  for name,_,_ in rows:
   if name in bylabel:ids.setdefault(name,bylabel[name])
 titles=sorted({aliases.get(n,n)for _,_,_,rows in ROSTERS for n,_,_ in rows if n not in ids})
 for i in range(0,len(titles),40):
  params=urllib.parse.urlencode({'action':'wbgetentities','format':'json','sites':'enwiki','titles':'|'.join(titles[i:i+40]),'props':'labels|claims|sitelinks','languages':'zh-hans|zh|en','redirects':'yes'})
  req=urllib.request.Request('https://www.wikidata.org/w/api.php?'+params,headers={'User-Agent':'GuanlanAtlas/1.6 educational historical atlas'})
  with urllib.request.urlopen(req,timeout=45)as r:entities=json.load(r)['entities']
  for q,e in entities.items():
   if not human(e):continue
   pool[q]=e
   title=e.get('sitelinks',{}).get('enwiki',{}).get('title')
   if title:ids[title]=q
  for old,new in aliases.items():
   if new in ids:ids[old]=ids[new]
  ids_path.write_text(json.dumps(ids,ensure_ascii=False),encoding='utf8');(CACHE/'downloaded-people.json').write_text(json.dumps({q:e for q,e in pool.items()if q in ids.values()},ensure_ascii=False),encoding='utf8');print('Named reign identities',min(i+40,len(titles)),'/',len(titles),flush=True);time.sleep(3)
 # Aliases redirected by enwiki may have a different canonical page title.
 # Only exact stored titles/labels are accepted; unresolved rows stay in report.
 facts=json.loads((ROOT/'public/data/polity-facts.json').read_bytes());tag='reviewed-named-reigns-2026-10-31';added=[];missing=[]
 for e in facts['entities'].values():e['fields']['ruler']=[r for r in e['fields'].get('ruler',[])if r.get('supplement')!=tag]
 for country,source,approx,rows in ROSTERS:
  if country not in facts['entities']:continue
  e=facts['entities'][country]
  for name,a,b in rows:
   q=ids.get(name)
   if not q or not human(pool.get(q,{})):missing.append(name);continue
   record={'value':q,'label':label(pool[q]),'from':a,'to':b,'at':None,'roleLabel':e['label']+'君主','supplement':tag,'citation':['https://en.wikipedia.org/wiki/'+source,'https://www.wikidata.org/wiki/'+q],'derived':True,'approximate':approx,'dateSource':'reviewed named reign chronology','inference':'在位年代取君主名录与人物资料；传统纪年、共治、继承争位可能有不同说法，交接年允许并列；不是从出生或去世日期推定任期。'if approx else'按政权统治者生平的已知执政阶段补充。'}
   e['fields'].setdefault('ruler',[]).append(record);facts['labels'][q]=record['label'];added.append({'country':country,**record})
 (ROOT/'public/data/polity-facts.json').write_text(json.dumps(facts,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 people={r['value']:pool[r['value']]for r in added};(CACHE/'verified-people.json').write_text(json.dumps(people,ensure_ascii=False),encoding='utf8')
 report={'reviewedAt':'2026-10-31','records':added,'unresolved':missing,'summary':{'records':len(added),'people':len(people),'countries':len({r['country']for r in added})}}
 (ROOT/'public/data/reviewed-reigns.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8');print(report['summary'],'unresolved',missing,flush=True)
if __name__=='__main__':main()
