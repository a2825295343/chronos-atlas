"""Dated governments/religious context and identity handovers without new territory."""
import copy,hashlib
from territory_repair_stage import ROOT,read,write
TAG='world-context-2026-11-02'
def main():
 facts=read('public/data/polity-facts.json');contexts=[]
 for e in facts['entities'].values():
  for field in ['government','religion']:e['fields'][field]=[r for r in e['fields'].get(field,[])if r.get('supplement')!=TAG]
 for q,a,b,gov,religion,source in [
  ('Q179876',927,1413,'君主制；王权、贵族、教会和逐渐形成的议会之间权力关系变化','拉丁基督教与教会礼制居核心，境内亦有其他信仰群体','https://en.wikipedia.org/wiki/Kingdom_of_England'),
  ('Q70972',987,1328,'卡佩王权；世袭君主制，王室领地与封建诸侯权力并存','拉丁基督教与天主教教会在王权礼制中居核心','https://en.wikipedia.org/wiki/Kingdom_of_France'),
  ('Q45670',1139,1821,'君主制；王权、贵族、教会及等级会议的权力随时期变化','罗马天主教为王室及国家礼制的核心','https://en.wikipedia.org/wiki/Kingdom_of_Portugal'),
  ('Q45670',1822,1827,'立宪君主制；制宪、摄政与王位交接仍有争执','罗马天主教具有国家宗教地位','https://en.wikipedia.org/wiki/Constitution_of_Portugal_(1822)'),
  ('Q45670',1828,1833,'米格尔王权与立宪派对立；内战期间并非统一有效的宪政秩序','罗马天主教具有国家宗教地位','https://en.wikipedia.org/wiki/Liberal_Wars'),
  ('Q45670',1834,1910,'立宪君主制；王室与议会、内阁分担权力','罗马天主教为国家宗教，宗教政策随时期变化','https://en.wikipedia.org/wiki/Constitution_of_Portugal_(1826)'),
  ('Q1062422',1752,1885,'缅甸君主制与宫廷官僚体系；掸邦等附属地区有地方统治者','上座部佛教受王室护持；地方及少数群体信仰并不统一','https://en.wikipedia.org/wiki/Konbaung_dynasty'),
  ('Q878309',1009,1225,'大瞿越／大越君主制，宫廷官僚和地方权力并存','佛教受王室护持，儒家礼制、道教及地方祭祀并存','https://en.wikipedia.org/wiki/L%C3%BD_dynasty'),
  ('Q3111454',1225,1400,'大越皇帝与上皇制度；退位上皇及宗室可能继续掌握实权','佛教、儒家礼制、道教及地方信仰并存','https://en.wikipedia.org/wiki/Tr%E1%BA%A7n_dynasty'),
  ('Q6500483',1802,1882,'皇帝制与省级官僚体系；地方行政在明命时期改制','儒家国家礼制、祖先祭祀与佛教、道教、地方信仰并存；基督教社群受到不同时期政策影响','https://en.wikipedia.org/wiki/Nguy%E1%BB%85n_dynasty'),
  ('Q6500483',1883,1945,'法国保护下的王朝君主制；实际权力受殖民行政限制，1945年多次变更','王室儒家礼制与多种地方宗教信仰并存','https://en.wikipedia.org/wiki/Nguy%E1%BB%85n_dynasty'),
  ('Q722071',1701,1896,'阿散蒂赫内与地方诸酋组成的复合王国；不能等同欧洲式单一中央集权','阿肯宗教、祖先祭祀及金凳国家礼制；地方信仰并不完全一致','https://en.wikipedia.org/wiki/Ashanti_Empire'),
  ('Q207521',1632,1974,'皇帝制；中央与地方诸王、贵族和军队的权力随时期显著变化','埃塞俄比亚正教在皇权礼制中居核心；境内有穆斯林及其他信仰群体','https://en.wikipedia.org/wiki/Ethiopian_Empire'),
  ('Q1028',1666,1911,'苏丹君主制；马赫赞与地方部族、宗教权威的关系随时期变化','逊尼派伊斯兰教，马立克学派及苏菲传统具有重要地位','https://en.wikipedia.org/wiki/Alaouite_dynasty'),
  ('Q217230',1824,1889,'1824年宪法下的君主制，皇帝享有调节权；1831—1840年正式君主年幼，由摄政执政','罗马天主教为官方宗教，其他信仰受当时宪法及法律限制','https://en.wikipedia.org/wiki/Constitution_of_Brazil_(1824)'),
  ('Q155',1890,1930,'联邦总统共和制；旧共和时期地方寡头与军政力量影响显著','共和国1890年确立政教分离，不再设官方国教','https://en.wikipedia.org/wiki/First_Brazilian_Republic'),
  ('Q298',1833,1890,'1833年宪法下的总统共和制','罗马天主教为官方宗教；这一制度在1925年宪法后改变','https://en.wikipedia.org/wiki/Constitution_of_Chile_(1833)'),
  ('Q298',1891,1920,'总统共和制度形式下通常所称的议会共和时期，内阁受国会支配显著','罗马天主教的官方地位仍在，直到1925年政教分离','https://en.wikipedia.org/wiki/Parliamentary_Republic_(Chile)'),
  ('Q414',1862,1916,'1853年宪法框架下的联邦总统共和制，统一与选举制度逐步发展','联邦政府支持罗马天主教；这不表示所有居民必须同属一种信仰','https://en.wikipedia.org/wiki/Constitution_of_Argentina')]:
  e=facts['entities'][q]
  for field,label in [('government',gov),('religion',religion)]:
   row=dict(value='local:'+TAG+':'+hashlib.sha1(f'{q}:{field}:{a}'.encode()).hexdigest()[:14],label=label,at=None,rank='preferred',supplement=TAG,citation=[source],**{'from':a,'to':b})
   if not any(x.get('supplement')==TAG and x.get('from')==a for x in e['fields'].get(field,[])):e['fields'].setdefault(field,[]).append(row)
   contexts.append(dict(country=q,field=field,**row))
 write('public/data/polity-facts.json',facts)
 # Rename period-specific source rows rather than globally merging regimes.
 oldreport=read('public/data/world-context-review.json')if(ROOT/'public/data/world-context-review.json').exists()else{}
 changed=list(oldreport.get('identityChanges',[]));stops=set()
 for c in read('public/data/temporal/index.json')['centuries']:
  path=f'public/data/temporal/{c}.geojson';db=read(path);out=[];modified=False
  for f in db['features']:
   p=f['properties'];n=p['NAME'];a,b=p['validFrom'],p['validTo'];segments=[]
   if n=='Argentine Confederation'and b>=1862:segments=[(a,min(b,1861),n),(max(a,1862),b,'Argentine Republic')]
   elif n=='Burma'and a>=1752 and b<=1885:segments=[(a,b,'Konbaung Dynasty')]
   else:out.append(f);continue
   for x,y,target in segments:
    if x>y:continue
    z=copy.deepcopy(f);r=z['properties'];r.update(validFrom=x,validTo=y)
    if target!=n:
     q,label=('Q414','阿根廷共和国')if target=='Argentine Republic'else('Q1062422','缅甸')
     r.update(NAME=target,SUBJECTO=target,qid=q,entityId=q,displayName=label,sourceName=r.get('sourceName',n),sourceQid=r.get('sourceQid',p.get('qid')),sourceRecord=str(p['sourceRecord'])+':'+TAG+':'+str(x),identityReview=TAG)
     if target=='Argentine Republic':r.update(sourceUrl='https://en.wikipedia.org/wiki/List_of_heads_of_state_of_Argentina',accuracy='1862年起按统一后的阿根廷共和国关联总统档案，不把阿根廷邦联的名称与身份延续到20世纪；保留原始时期几何。')
     else:r.update(sourceUrl='https://en.wikipedia.org/wiki/Konbaung_dynasty',accuracy='将1820—1885年来源中的Burma关联到当时贡榜缅甸王国，而不是套用现代缅甸国家档案；保留原始几何。')
     changed.append(dict(old=n,name=target,qid=q,**{'from':x,'to':y}));stops.update([x,y+1])
    out.append(z)
   modified=True
  if modified:db['features']=out;write(path,db)
 # Map headings retain the source identity but show a country, not just a family.
 cur=read('public/data/curated-facts.json');cur['identities']['Konbaung Dynasty']='Q1062422';cur['identities']['Argentine Republic']='Q414';write('public/data/curated-facts.json',cur)
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  d=read(path);d.update({'Konbaung Dynasty':'缅甸','Argentine Republic':'阿根廷共和国'});write(path,d)
 for c in [17,18,19]:
  path=f'public/data/temporal/{c}.geojson';d=read(path);dirty=False
  for f in d['features']:
   if f['properties']['NAME']=='Konbaung Dynasty':f['properties']['displayName']='缅甸';dirty=True
  if dirty:write(path,d)
 index=read('public/data/temporal/index.json');index['changeYears']=sorted(set(index['changeYears'])|stops);index['counts']['polityRecords']=len({f['properties']['sourceRecord']for c in index['centuries']for f in read(f'public/data/temporal/{c}.geojson')['features']});write('public/data/temporal/index.json',index)
 write('public/data/world-context-review.json',dict(reviewedAt='2026-11-02',contexts=contexts,identityChanges=changed,limitations=['政体与宗教条目按国家及分期描述，不代替每个居民的身份或全部地方政治状态。','名称和档案身份修订保留来源几何，没有把政治名义范围自动扩大为实控领土。']))
 print('Context fields',len(contexts),'period identity records',len(changed))
if __name__=='__main__':main()
