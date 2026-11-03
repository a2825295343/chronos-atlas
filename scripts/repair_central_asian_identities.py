"""Distinguish divided khanates; do not share one Wikidata identity or ruler list."""
import copy, hashlib, json, shutil
from territory_repair_stage import ROOT, read, write, clean
from prepare_political_presentation import label_path
from shapely.geometry import shape, mapping, box, Polygon
from shapely import union_all

TAG='central-asian-identities-2026-11-01'
QARA='https://www.iranicaonline.org/articles/qarakhanid/'
YARK='https://www.iranicaonline.org/articles/yarkand/'
TARIKH='https://en.wikisource.org/wiki/Page:The_Tarikh-i-Rashidi_-_Mirza_Muhammad_Haidar,_Dughl%C3%A1t_-_tr._Edward_D._Ross_(1895).djvu/129'
UNESCO='https://uzbekliterature.uz/sites/default/files/history-of-civilizations-of-central-asia-vol-5.pdf'
NAMES={
 'Eastern Kara-Khanids':('东喀喇汗国','local:eastern-karakhanids',QARA),
 'Western Karakhanid Khanate':('西喀喇汗国','local:western-karakhanids',QARA),
 'Eastern Moghulistan':('叶尔羌汗国','local:yarkand-khanate',YARK),
 'Western Moghulistan':('天山蒙兀儿诸部','local:tian-shan-moghul-communities',TARIKH),
 'Kyrgyz Tian Shan Communities':('天山吉尔吉斯诸部','local:tian-shan-kyrgyz-communities',TARIKH),
 'Turpan Khanate':('吐鲁番汗国','local:turpan-khanate',UNESCO)}
# Minimum Turpan depression core; the old source puts its actual capital just
# outside the Tarim polygon, in the much larger Tumed polygon. This explicit
# reconstruction is dated and cut out of that older map, never added on top.
TURPAN_CORE=Polygon([(88.35,42.35),(88.4,43.2),(89.65,43.25),(90.0,42.7),(89.3,42.15),(88.35,42.35)])


def main():
 backup=ROOT/'.local'/TAG/'original-shards';backup.mkdir(parents=True,exist_ok=True)
 counts={};changes=[]
 for c in [10,11,15,16]:
  file=f'public/data/temporal/{c}.geojson';saved=backup/f'{c}.geojson'
  if not saved.exists():shutil.copyfile(ROOT/file,saved)
  data=json.loads(saved.read_bytes());out=[]
  for f in data['features']:
   p=f['properties'];name=p['NAME']
   if name not in NAMES:
    if name in ['Tümed','Oirats','Mongol Khanate','Golden Horde']and p['validFrom']<=1686 and p['validTo']>=1519 and shape(f['geometry']).intersects(TURPAN_CORE):
     for a,b,cut in [(p['validFrom'],min(1518,p['validTo']),False),
                     (max(1519,p['validFrom']),min(1686,p['validTo']),True),
                     (max(1687,p['validFrom']),p['validTo'],False)]:
      if a>b:continue
      row=copy.deepcopy(f);row['properties'].update(validFrom=a,validTo=b)
      if cut:
       row['geometry']=mapping(clean(shape(row['geometry']).difference(TURPAN_CORE)))
       row['properties'].update(sourceRecord=TAG+':turpan-cut:'+str(p['sourceRecord']),geometryCorrection=TAG)
      out.append(row)
    else:out.append(f)
    continue
   if name=='Western Moghulistan':
    intervals=[(p['validFrom'],min(1525,p['validTo']),name),
               (max(1526,p['validFrom']),p['validTo'],'Kyrgyz Tian Shan Communities')]
   elif name=='Eastern Moghulistan':
    intervals=[(p['validFrom'],min(1569,p['validTo']),name),
               (max(1570,p['validFrom']),p['validTo'],name)]
   else:intervals=[(p['validFrom'],p['validTo'],name)]
   for a,b,n in intervals:
    if a>b:continue
    r=copy.deepcopy(f);label,q,url=NAMES[n];rp=r['properties']
    rp.update(NAME=n,SUBJECTO=n,displayName=label,qid=q,entityId=q,sourceQid=p.get('qid'),
              validFrom=a,validTo=b,sourceName=name,sourceUrl=url,identityCorrection=TAG)
    if n.startswith('Kyrgyz')or n=='Western Moghulistan':
     rp.update(regionalCollection=True,representationKind='regional-polities',
               accuracy='原图称西部蒙兀儿斯坦的天山地域。1525—1526年前后蒙兀儿汗廷部众南迁后，'
                        '此处以吉尔吉斯诸部的地方分布概览表示，不假定有统一汗廷或整片地区始终由同一君主直接控制。',
               representationNote='按《拉失德史》关于蒙兀儿部众南迁与吉尔吉斯势力的记载纠正政权标签；范围沿用源图地域概化，非精确部落边界。')
    if n=='Eastern Moghulistan':
     r['geometry']=mapping(clean(union_all([shape(r['geometry']),TURPAN_CORE])))
     rp.update(accuracy='1514年后以叶尔羌为中心的察合台后裔汗政权。原始图源名为Eastern Moghulistan，'
                        '不能据其英文方向名称机械对应王朝分支；吐鲁番在1570年前另作核心区示意。'
                        '轮廓仍为概化，不表示年内军事进退已逐处核定。')
     if a<=1569:
      # Only the Turpan/Qarashahr geographic core, not an invented full eastern half.
      g=clean(shape(r['geometry']));core=clean(g.intersection(box(85.5,40.5,94.5,44.5)))
      if not core.is_empty and core.area>.01:
       r['geometry']=mapping(clean(g.difference(core)))
       t=copy.deepcopy(r);tp=t['properties'];tn='Turpan Khanate';tl,tq,tu=NAMES[tn]
       tp.update(NAME=tn,SUBJECTO=tn,displayName=tl,qid=tq,entityId=tq,sourceUrl=tu,
                 inferredBoundary=True,accuracy='吐鲁番、焉耆一带汗政权的核心概化；根据1516年后曼速尔分支与叶尔羌分立的记载，'
                 '从原图对应地域裁分，并补正被误放入土默特轮廓的吐鲁番城附近核心。内部线用地理范围辅助定位，'
                 '不是精确历史国界。1570年起按叶尔羌统合阶段展示。')
       t['geometry']=mapping(core);tp['labelPath']=label_path(core,tl)
       tp['sourceRecord']=TAG+':'+hashlib.sha1(f'{p["sourceRecord"]}|{tn}|{a}|{b}'.encode()).hexdigest()[:16]
       out.append(t)
    rp['labelPath']=label_path(r['geometry'],label)
    rp['sourceRecord']=TAG+':'+hashlib.sha1(f'{p["sourceRecord"]}|{n}|{a}|{b}'.encode()).hexdigest()[:16]
    out.append(r);counts[n]=counts.get(n,0)+1
   changes.append({'sourceName':name,'from':p['validFrom'],'to':p['validTo']})
  data['features']=out;write(file,data)
 labels={n:v[0]for n,v in NAMES.items()}
 for file in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  d=read(file);d.update(labels);write(file,d)
 cur=read('public/data/curated-facts.json');facts=read('public/data/polity-facts.json')
 for n,(label,q,url)in NAMES.items():
  cur['identities'][n]=q
  note=('地方诸部集合，不存在已核定适用于全域的共同君主。'if 'Communities'in n or n=='Western Moghulistan'else
        '与同源王朝其他分支分别建档，不套用整个王朝的首都、统治者和存续日期。')
  fields={}
  for key,text in [('government','地方部落与首领并存'if 'Communities'in n or n=='Western Moghulistan'else'汗国君主制'),
                   ('religion','伊斯兰教；地方社群信仰并非完全一致'),
                   ('capital',{'Eastern Kara-Khanids':'八剌沙衮、喀什噶尔','Western Karakhanid Khanate':'撒马尔罕',
                               'Eastern Moghulistan':'叶尔羌','Turpan Khanate':'吐鲁番'}.get(n,'无统一首都'))]:
   fields[key]=[{'value':text,'label':text,'from':1040 if 'Kara'in n else 1519,'to':1212 if 'Kara'in n else 1686,
                 'at':None,'citation':[url],'supplement':TAG}]
  if 'Communities'in n or n=='Western Moghulistan':
   fields['ruler']=[{'value':note,'label':note,'from':1526 if 'Communities'in n else 1519,'to':1635 if 'Communities'in n else 1525,
                     'at':None,'kind':'collective','citation':[url],'supplement':TAG}]
  facts['entities'][q]={'label':label,'en':n,'description':note,'fields':fields};facts['labels'][q]=label
 relations=[{'id':TAG+':qara','kind':'historicalDivision','members':['Eastern Kara-Khanids','Western Karakhanid Khanate'],
              'from':1046,'to':1084,'title':'喀喇汗国的东西分立','detail':'约1040年前后形成两个汗国，同出喀喇汗王族，但已分立；王朝渊源不等于当年结盟、附庸或共同君主。','source':QARA},
             {'id':TAG+':moghul','kind':'historicalDivision','members':['Eastern Moghulistan','Turpan Khanate'],
              'from':1519,'to':1569,'title':'叶尔羌与吐鲁番的王朝分支','detail':'同出察合台后裔汗族；1516年后分别以叶尔羌、吐鲁番为统治中心。这里记录政权渊源，不据此虚构全年结盟或共主。','source':UNESCO}]
 cur['relations']=[r for r in cur['relations']if not r.get('id','').startswith(TAG)]+relations
 write('public/data/curated-facts.json',cur);write('public/data/polity-facts.json',facts)
 index=read('public/data/temporal/index.json');allrows=[f for c in index['centuries']for f in read(f'public/data/temporal/{c}.geojson')['features']]
 index['counts']['polityRecords']=len({f['properties']['sourceRecord']for f in allrows})
 index['changeYears']=sorted(set(index['changeYears'])|{1526,1570});index['centralAsianIdentityRevision']=TAG
 write('public/data/temporal/index.json',index)
 write('public/data/central-asian-identities-review.json',{'revision':TAG,'counts':counts,'records':changes,
       'sources':[QARA,YARK,TARIKH,UNESCO],'limitations':['吐鲁番为地理辅助裁分的核心示意；未声称精确复原全部领国。','天山地方诸部不是统一国家，未虚构共同国王。']})
 print('Central Asian identities:',counts,flush=True)


if __name__=='__main__':main()
