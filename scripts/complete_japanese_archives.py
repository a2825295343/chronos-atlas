"""Dated Japanese offices. Reign columns only; never lifespan columns.

The emperor is a separate office in bakufu records, not a second shogun.
Annual transition years can contain more than one incumbent.
"""
import argparse,json,re,subprocess,urllib.parse,hashlib
from pathlib import Path
from territory_repair_stage import ROOT,read,write
from prepare_ancient_rosters import RosterTables,reign
from prepare_global_archive_review import human
from opencc import OpenCC
CACHE=ROOT/'.local/japan-complete';TAG='japan-complete-2026-11-02'
COURT='https://www.kunaicho.go.jp/e-about/genealogy/pdf/keizu-e.pdf'
BAKUFU='https://www.edo-tokyo-museum.or.jp/s-exhibition/house-of-tokugawa/'
CC=OpenCC('t2s')
def table(page):
 p=RosterTables();p.feed((CACHE/(page+'.html')).read_text(encoding='utf8'));return zip(p.rows,p.rowTables)
def candidates():
 out=[]
 for row,t in table('List_of_emperors_of_Japan'):
  if len(row)<6 or not re.match(r'^\d+$',row[0]['text']):continue
  raw=row[4]['text'].split('(')[0].replace('|',' ');raw=re.sub(r'\[[^]]*\]','',raw)
  if 'present'in raw:raw=raw.replace('present','2026')
  period=reign(raw)
  if not period or period[1]<538:continue
  title=next((n for n in row[3]['links']if n.startswith(('Emperor ','Empress '))or n=='Hirohito'),None)
  if not title:title=next((n for n in row[2]['links']if n in ['Akihito','Naruhito']),None)
  if not title:continue
  title={'Emperor Kōbun':'Prince Ōtomo','Empress Shōtoku':'Empress Kōken'}.get(title,title)
  cn=re.search(r'[\u3400-\u9fff]+天皇',row[3]['text'])
  label=cn[0]if cn else re.search(r'[\u3400-\u9fff]+',row[2]['text'])[0]+'天皇'
  out.append(dict(title=title,label=CC.convert(label),start=period[0],end=period[1],office='emperor',source=COURT))
 # Northern Court claimants are unnumbered in the modern official succession.
 for title,label,a,b in [('Emperor Kōgon','光严天皇',1331,1333),('Emperor Kōmyō','光明天皇',1336,1348),('Emperor Sukō','崇光天皇',1348,1351),('Emperor Go-Kōgon','后光严天皇',1352,1371),('Emperor Go-En\'yū','后圆融天皇',1371,1382),('Emperor Go-Komatsu','后小松天皇',1382,1392)]:
  out.append(dict(title=title,label=label,start=a,end=b,office='emperor',role='北朝天皇；与南朝皇统并立',source=COURT))
 for row,t in table('List_of_shoguns'):
  if t!=6 or len(row)<5 or not row[2]['links']:continue
  title=row[2]['links'][0]
  if not title.startswith('Tokugawa ')or 'de facto'in row[4]['text']:continue
  a=re.search(r'\d{4}',row[3]['text']);b=re.search(r'\d{4}',row[4]['text'])
  if not a or not b:continue
  lo,hi=int(a[0]),int(b[0])
  if title=='Tokugawa Ieyasu':lo,hi=1603,1605
  out.append(dict(title=title,start=lo,end=hi,office='shogun',country='Q205662',source=BAKUFU))
 # Civil-year dates; later ceremonial retention is not treated as control.
 clans=[('Minamoto no Yoritomo',1192,1199),('Minamoto no Yoriie',1202,1203),('Minamoto no Sanetomo',1203,1219),('Kujō Yoritsune',1226,1244),('Kujō Yoritsugu',1244,1252),('Prince Munetaka',1252,1266),('Prince Koreyasu',1266,1289),('Prince Hisaaki',1289,1308),('Prince Morikuni',1308,1333)]
 ash=[('Ashikaga Takauji',1338,1358),('Ashikaga Yoshiakira',1358,1367),('Ashikaga Yoshimitsu',1368,1394),('Ashikaga Yoshimochi',1394,1423),('Ashikaga Yoshikazu',1423,1425),('Ashikaga Yoshinori',1429,1441),('Ashikaga Yoshikatsu',1442,1443),('Ashikaga Yoshimasa',1449,1473),('Ashikaga Yoshihisa',1473,1489),('Ashikaga Yoshitane',1490,1493),('Ashikaga Yoshizumi',1494,1508),('Ashikaga Yoshitane',1508,1521),('Ashikaga Yoshiharu',1521,1546),('Ashikaga Yoshiteru',1546,1565),('Ashikaga Yoshihide',1568,1568),('Ashikaga Yoshiaki',1568,1573)]
 regs=[('Hōjō Tokimasa',1203,1205),('Hōjō Yoshitoki',1205,1224),('Hōjō Yasutoki',1224,1242),('Hōjō Tsunetoki',1242,1246),('Hōjō Tokiyori',1246,1256),('Hōjō Nagatoki',1256,1264),('Hōjō Masamura',1264,1268),('Hōjō Tokimune',1268,1284),('Hōjō Sadatoki',1284,1301),('Hōjō Morotoki',1301,1311),('Hōjō Munenobu',1311,1312),('Hōjō Hirotoki',1312,1315),('Hōjō Mototoki',1315,1316),('Hōjō Takatoki',1316,1326),('Hōjō Sadaaki',1326,1326),('Hōjō Moritoki',1326,1333)]
 for rs,country,office in [(clans,'Q736839','shogun'),(ash,'Q1154406','shogun'),(regs,'Q736839','shikken')]:
  for title,a,b in rs:out.append(dict(title=title,start=a,end=b,country=country,office=office,source='https://en.wikipedia.org/wiki/'+('Shikken'if office=='shikken'else'List_of_shoguns')))
 for title,country,a,b,office,role in [('Minamoto no Yoritomo','Q736839',1185,1191,'ruler','镰仓殿；1192年才正式任征夷大将军'),('Minamoto no Yoriie','Q736839',1199,1201,'ruler','镰仓殿；1202年才正式任将军'),('Kujō Yoritsune','Q736839',1219,1225,'ruler','幼年镰仓殿；政务由北条氏等主持，1226年才正式任将军'),('Ashikaga Yoshimochi','Q1154406',1425,1428,'shikken','退任将军后再度主持幕政；并非再任将军')]:out.append(dict(title=title,country=country,start=a,end=b,office=office,role=role,source='https://en.wikipedia.org/wiki/List_of_shoguns'))
 for title,label,country,a,b,role in [('Enomoto Takeaki','榎本武扬','local:ezo-government',1868,1869,'旧幕府军领袖／虾夷政权总裁；1868年末起'),('Matsudaira Katamori','松平容保','local:jp-northern-alliance',1868,1868,'会津藩主；联盟重要领袖之一，不是全联盟的君主'),('Date Yoshikuni','伊达庆邦','local:jp-northern-alliance',1868,1868,'仙台藩主；联盟重要领袖之一')]:out.append(dict(title=title,label=label,country=country,start=a,end=b,office='ruler',role=role,source='https://www.city.hokuto.hokkaido.jp/bunkazai/data/nen2-1.htm'))
 (CACHE/'candidates.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8');print('Office terms',len(out))
def fetch():
 candidates=json.loads((CACHE/'candidates.json').read_bytes());pool={}
 for f in [ROOT/'.local/japanese-polities/verified-people.json',CACHE/'verified-people.json']:
  if f.exists():pool.update(json.loads(f.read_bytes()))
 names={e.get('sitelinks',{}).get('enwiki',{}).get('title'):q for q,e in pool.items()}
 wanted=sorted({r['title']for r in candidates}-names.keys())
 for i in range(0,len(wanted),25):
  params=urllib.parse.urlencode(dict(action='wbgetentities',format='json',sites='enwiki',titles='|'.join(wanted[i:i+25]),props='labels|claims|sitelinks',languages='zh-hans|zh|en',redirects='yes'))
  p=CACHE/('people-'+hashlib.sha1(params.encode()).hexdigest()[:16]+'.json')
  if not p.exists():subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','--retry','2','https://www.wikidata.org/w/api.php?'+params,'--output',str(p)],check=True)
  pool.update({q:e for q,e in json.loads(p.read_bytes())['entities'].items()if human(e)})
 (CACHE/'verified-people.json').write_text(json.dumps(pool,ensure_ascii=False),encoding='utf8');print('Verified human entities',len(pool))
def apply():
 candidates=json.loads((CACHE/'candidates.json').read_bytes());pool=json.loads((CACHE/'verified-people.json').read_bytes());bytitle={e.get('sitelinks',{}).get('enwiki',{}).get('title'):q for q,e in pool.items()}
 facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json');review=[]
 # All named offices from this source replace previous duplicates within their
 # covered office periods; older clan leadership elsewhere is preserved.
 for q in ['local:japanese-imperial-court','Q736839','Q1154406','Q205662','Q188712','Q17','local:ezo-government','local:jp-northern-alliance']:
  entity=facts['entities'].setdefault(q,dict(label={'local:ezo-government':'虾夷政权','local:jp-northern-alliance':'奥羽越列藩同盟'}.get(q,'日本'),en='',description='',fields={}))
  for field in entity['fields']:entity['fields'][field]=[r for r in entity['fields'][field]if r.get('supplement')!=TAG]
 for r in candidates:
  q=bytitle.get(r['title'])
  if not q:raise ValueError('Exact human identity unresolved: '+r['title'])
  person=pool[q];label=r.get('label')or next((person.get('labels',{}).get(k,{}).get('value')for k in ['zh-hans','zh','zh-hant']if person.get('labels',{}).get(k)),None)
  if not label or not re.search('[\u3400-\u9fff]',label):raise ValueError('Chinese person label missing '+r['title'])
  label=CC.convert(label);facts['labels'][q]=label
  scopes=[(r['country'],r['start'],r['end'],'headOfGovernment'if r['office']=='shikken'else'ruler')]if r['office']!='emperor'else[('local:japanese-imperial-court',max(538,r['start']),min(1867,r['end']),'ruler'),('Q188712',max(1867,r['start']),min(1947,r['end']),'ruler'),('Q17',max(1947,r['start']),r['end'],'ruler'),*[(k,max(a,r['start']),min(b,r['end']),'imperialSovereign')for k,a,b in [('Q736839',1185,1333),('Q1154406',1338,1573),('Q205662',1603,1867)]]]
  for country,a,b,field in scopes:
   if a>b:continue
   rows=facts['entities'][country]['fields'].setdefault(field,[])
   role=r.get('role')or {'emperor':'天皇；幕府时期不等于幕府实际执政者','shogun':'征夷大将军；正式在职年表','shikken':'镰仓幕府执权；与将军职务分列'}.get(r['office'],'势力领导人')
   row=dict(value=q,label=label,from_=a,to=b,at=None,rank='preferred',roleLabel=role,citation=[r['source'],'https://en.wikipedia.org/wiki/'+urllib.parse.quote(r['title'].replace(' ','_'))],supplement=TAG);row['from']=row.pop('from_')
   if b==2026:row['verifiedThrough']=2026
   # Eliminate vague place-holders in the newly documented interval only.
   kept=[]
   for old in rows:
    if old.get('kind')!='collective' or old.get('from')is None or old.get('to')is None:kept.append(old);continue
    for lo,hi in [(old['from'],min(old['to'],a-1)),(max(old['from'],b+1),old['to'])]:
     if lo<=hi:kept.append({**old,'from':lo,'to':hi})
   facts['entities'][country]['fields'][field]=kept+[row];review.append(dict(country=country,field=field,**row))
 for q in ['Q736839','Q1154406','Q205662']:
  e=facts['entities'][q];e['rulerScopeNote']='将军、天皇与执权分别列职；空位期不把前任延任。年内交接可并列，幕府控制范围不等于全日本直接领地。'
 for a,b,text in [(1426,1428,'正式将军职位空缺；足利义持退任后主持幕政'),(1444,1448,'正式将军职位空缺；足利义政于1449年正式就任'),(1566,1567,'正式将军职位空缺；足利义辉遇害后至义荣就任前')]:
  row={'value':f'vacancy:ashikaga:{a}','label':text,'from':a,'to':b,'at':None,'kind':'vacancy','roleLabel':'已核对的职位空缺，不把前任延任；不表示期间没有管领、大名或其他实际掌权者。','citation':['https://en.wikipedia.org/wiki/List_of_shoguns'],'supplement':TAG};facts['entities']['Q1154406']['fields'].setdefault('ruler',[]).append(row);review.append({'country':'Q1154406','field':'ruler',**row})
 for n,q in [('Northern Alliance of Japanese Domains','local:jp-northern-alliance'),('Ezo Island Government','local:ezo-government')]:cur['identities'][n]=q
 for label,a,b in [('京都；江户于1868年改称东京，朝廷移驻过程跨越1868—1869年',1867,1868),('东京',1869,1947)]:
  rows=facts['entities']['Q188712']['fields'].setdefault('capital',[]);rows.append({'value':label,'label':label,'from':a,'to':b,'at':None,'citation':['https://www.city.hokuto.hokkaido.jp/bunkazai/data/nen2-1.htm'],'supplement':TAG})
 flags=read('public/data/flags.json');reference=next(r for r in flags['entities']['Q17']if r.get('from')==1870)
 for country,a,b in [('Q205662',1854,1867),('Q188712',1868,1869)]:
  rows=flags['entities'].setdefault(country,[]);rows[:]=[r for r in rows if r.get('supplement')!=TAG]
  rows.append({**reference,'from':a,'to':b,'role':'日之丸船舶识别旗／代表旗','representative':True,'supplement':TAG,'periodNote':'1854年幕府规定白地日之丸作为日本船舶识别旗。本图用后来的定式作代表，不表示当时已有1870年的法定尺寸与比例。','periodSource':'https://www.pref.kagoshima.jp/aa02/pr/gaiyou/itiban/hatu/hinomaru.html'})
 write('public/data/flags.json',flags)
 people={r['value']for r in review if r['value'].startswith('Q')}
 write('public/data/polity-facts.json',facts);write('public/data/curated-facts.json',cur);write('public/data/japan-complete-review.json',dict(reviewedAt='2026-11-02',terms=len(candidates),appointments=len(review),people=len(people),records=review,sources=[COURT,BAKUFU],limitations=['538年以前的传说帝系不当作可考年度事实。','南北朝同时存在皇位主张；列职不意味着共享一个统一统治权。','将军空位期不强行填上一位将军；执权名单另列。','未补齐全部摄政、关白、院政人物及每个大名的家督阶段。']))
 print('Applied office appointments',len(review),'people',len(people))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['candidates','fetch','apply']);stage=p.parse_args().stage;globals()[stage]()
