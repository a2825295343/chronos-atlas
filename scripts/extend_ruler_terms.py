"""Reuse cached, office-matched P39 terms and add sourced dynastic reign tables.
Do not infer a person's reign from unrelated offices or a current officeholder.
"""
import json,pathlib,re,sys,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from enrich_polities import simplify,label
def main():
 raw={}
 for file in (ROOT/'.local/wikidata').glob('*.json'):
  for q,e in json.loads(file.read_bytes()).items():
   if e.get('claims'):raw[q]=e
 path=ROOT/'public/data/polity-facts.json';facts=json.loads(path.read_bytes());offices={};added=0
 for q,entity in facts['entities'].items():
  for field,prop in [('ruler','P1906'),('headOfGovernment','P1313')]:
   for claim in raw.get(q,{}).get('claims',{}).get(prop,[]):
    office=simplify(claim)
    if office:offices.setdefault(office['value'],[]).append((q,field))
 for person,e in raw.items():
  for c in e.get('claims',{}).get('P39',[]):
   term=simplify(c)
   if not term or term['from'] is None:continue
   for country,field in offices.get(term['value'],[]):
    rows=facts['entities'][country]['fields'].setdefault(field,[])
    if any(r['value']==person and r['from']==term['from'] and r['to']==term['to'] for r in rows):continue
    rows.append({**term,'value':person,'label':label(e),'dateSource':'office-matched P39 / '+term['value'],'citation':term['citation']or['https://www.wikidata.org/wiki/'+person]});added+=1
 path.write_text(json.dumps(facts,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 curatedPath=ROOT/'public/data/curated-facts.json';curated=json.loads(curatedPath.read_bytes());entities=json.loads((ROOT/'.local/temporal-entities.json').read_bytes());portraitsPath=ROOT/'public/data/portraits.json';portraits=json.loads(portraitsPath.read_bytes())
 tables={
 'Tang Dynasty':('唐朝皇帝列表',[
 [618,626,'唐高祖 李渊'],[626,649,'唐太宗 李世民'],[649,683,'唐高宗 李治'],[684,684,'唐中宗 李显'],[684,690,'唐睿宗 李旦'],[690,705,'武则天（武周）'],[705,710,'唐中宗 李显'],[710,710,'唐殇帝 李重茂'],[710,712,'唐睿宗 李旦'],[712,756,'唐玄宗 李隆基'],[756,762,'唐肃宗 李亨'],[762,779,'唐代宗 李豫'],[779,805,'唐德宗 李适'],[805,805,'唐顺宗 李诵'],[805,820,'唐宪宗 李纯'],[820,824,'唐穆宗 李恒'],[824,827,'唐敬宗 李湛'],[827,840,'唐文宗 李昂'],[840,846,'唐武宗 李炎'],[846,859,'唐宣宗 李忱'],[859,873,'唐懿宗 李漼'],[873,888,'唐僖宗 李儇'],[888,904,'唐昭宗 李晔'],[904,907,'唐哀帝 李柷']]),
 'Song Dynasty':('宋朝君主列表',[
 [960,976,'宋太祖 赵匡胤'],[976,997,'宋太宗 赵光义'],[997,1022,'宋真宗 赵恒'],[1022,1063,'宋仁宗 赵祯'],[1063,1067,'宋英宗 赵曙'],[1067,1085,'宋神宗 赵顼'],[1085,1100,'宋哲宗 赵煦'],[1100,1126,'宋徽宗 赵佶'],[1126,1127,'宋钦宗 赵桓'],[1127,1162,'宋高宗 赵构'],[1162,1189,'宋孝宗 赵昚'],[1189,1194,'宋光宗 赵惇'],[1194,1224,'宋宁宗 赵扩'],[1224,1264,'宋理宗 赵昀'],[1264,1274,'宋度宗 赵禥'],[1274,1276,'宋恭帝 赵㬎'],[1276,1278,'宋端宗 赵昰'],[1278,1279,'宋少帝 赵昺']]),
 'Yuan Dynasty':('元朝君主列表',[
 [1271,1294,'元世祖 忽必烈'],[1294,1307,'元成宗 铁穆耳'],[1307,1311,'元武宗 海山'],[1311,1320,'元仁宗 爱育黎拔力八达'],[1320,1323,'元英宗 硕德八剌'],[1323,1328,'泰定帝 也孙铁木儿'],[1328,1328,'天顺帝 阿速吉八'],[1328,1329,'元文宗 图帖睦尔'],[1329,1329,'元明宗 和世㻋'],[1329,1332,'元文宗 图帖睦尔'],[1332,1332,'元宁宗 懿璘质班'],[1333,1368,'元惠宗 妥懽帖睦尔']]),
 'Mongol Empire':('蒙古大汗列表',[
 [1206,1227,'成吉思汗 铁木真'],[1227,1229,'拖雷（监国）'],[1229,1241,'窝阔台'],[1241,1246,'乃马真后（称制）'],[1246,1248,'贵由'],[1248,1251,'海迷失后（称制）'],[1251,1259,'蒙哥'],[1260,1264,'阿里不哥（争位）'],[1260,1294,'忽必烈（1260年起争位）']]),
 'Nazi Germany':('纳粹德国',[[1933,1934,'保罗·冯·兴登堡（总统）'],[1934,1945,'阿道夫·希特勒（元首）'],[1945,1945,'卡尔·邓尼茨（总统）']]),
 }
 aliases={'Tang Dynasty':['Tang Dynasty','Tang'],'Song Dynasty':['Song Dynasty','Northern Song Dynasty','Southern Song Dynasty','Northern Song','Southern Song'],'Yuan Dynasty':['Yuan Dynasty'],'Mongol Empire':['Mongol Empire'],'Nazi Germany':['Nazi Germany']}
 count=0
 for canonical,(article,rows) in tables.items():
  for name in aliases[canonical]:
   q=entities.get(name,{}).get('qid')
   if not q:continue
   c=curated['polities'].setdefault(q,{});c['rulers']=rows;c['rulersSource']='https://zh.wikipedia.org/wiki/'+urllib.parse.quote(article);c.setdefault('source',c['rulersSource']);count+=len(rows)
   for a,b,text in rows:
    simple=re.sub(r'（.*?）','',text).strip().split()[-1]
    match=[(p,v) for p,v in portraits['people'].items() if v.get('label') in [simple,text]]
    if len(match)==1:portraits['manualRulers'][q+'|'+text]=match[0][0]
 curatedPath.write_text(json.dumps(curated,ensure_ascii=False,indent=2),encoding='utf-8');portraitsPath.write_text(json.dumps(portraits,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print('Additional office-matched terms',added,'dynastic reign rows',count,flush=True)
if __name__=='__main__':main()
