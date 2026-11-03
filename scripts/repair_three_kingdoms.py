"""Repair the 221–223 gap and add sourced, named Three Kingdoms sovereigns.

Only the target records in century 2 are changed. Reruns retain unrelated
repairs and replace only this script's facts. Cached people must be real Q5s.
"""
import copy,json,shutil
from territory_repair_stage import ROOT,read,write,clean
from prepare_political_presentation import label_path
from prepare_global_archive_review import human
from shapely.geometry import shape,mapping
from shapely import union_all

TAG='three-kingdoms-2026-11-01'
CACHE=ROOT/'.local/three-kingdoms'
SHU='https://www.archontology.org/nations/china/shu_han/00_219_264_s.php'
WEI='https://en.wikipedia.org/wiki/Cao_Wei'
WU='https://en.wikipedia.org/wiki/Eastern_Wu'
ROSTERS={
 'Q320925':(SHU,[('Liu Bei','刘备',221,223,'蜀汉昭烈帝；221年称帝，223年去世'),('Liu Shan','刘禅',223,263,'蜀汉后主；223年继位，263年末降魏')]),
 'Q320930':(WEI,[('Cao Pi','曹丕',220,226,'魏文帝；220年受禅称帝'),('Cao Rui','曹叡',226,239,'魏明帝'),('Cao Fang','曹芳',239,254,'魏帝；254年被废为齐王'),('Cao Mao','曹髦',254,260,'魏帝；260年被弑'),('Cao Huan','曹奂',260,266,'魏元帝；传统纪年咸熙二年受禅，对应公历266年2月')]),
 'Q274488':(WU,[('Sun Quan','孙权',200,220,'江东孙氏政权领袖；此阶段尚未称吴王或皇帝'),('Sun Quan','孙权',221,228,'吴王；221年受封，222年改元，229年称帝'),('Sun Quan','孙权',229,252,'吴大帝'),('Sun Liang','孙亮',252,258,'吴帝；258年被废'),('Sun Xiu','孙休',258,264,'吴景帝'),('Sun Hao','孙皓',264,280,'吴末帝；280年降晋')]),
 'Q204077':('https://en.wikipedia.org/wiki/Cao_Cao',[('Cao Cao','曹操',196,220,'汉丞相／魏公、魏王；未生前称帝，220年追尊魏武帝')]),
}

def main():
 CACHE.mkdir(exist_ok=True);path=ROOT/'public/data/temporal/2.geojson'
 if not(CACHE/'2.before.geojson').exists():shutil.copyfile(path,CACHE/'2.before.geojson')
 index=read('public/data/temporal/index.json');world=read('public/data/temporal/2.geojson');fs=world['features'];changes=[]
 def new(f,n,q,label,a,b,note,g=None):
  r=copy.deepcopy(f);p=r['properties'];p.update(NAME=n,SUBJECTO=n,qid=q,entityId=q,displayName=label,validFrom=a,validTo=b,sourceRecord=TAG+':'+n+':'+str(a),threeKingdomReview=TAG,sourceRecordBefore=p['sourceRecord'],sourceUrl=SHU if n=='Shu Han'else WEI if n=='Cao Wei'else WU,accuracy=note,representationNote=note,geometryMethod='沿用相邻已收录分期的概化轮廓；修正身份和日期，不宣称已经复原逐年战线。')
  if g is not None:r['geometry']=mapping(g)
  p['labelPath']=label_path(r['geometry'],label);changes.append({'name':n,'from':a,'to':b,'note':note});return r
 if index.get('threeKingdomsRevision')!=TAG:
  shu=next(f for f in fs if f['properties']['NAME']=='Shu Han'and f['properties']['validFrom']==224)
  occupied=union_all([shape(f['geometry'])for f in fs if f['properties']['validFrom']<=221<=f['properties']['validTo']])
  fs.append(new(shu,'Shu Han','Q320925','蜀汉',221,223,'刘备221年称帝，不能从224年才显示蜀汉。用224年已收录的成都、益州和汉中概化轮廓回补221—223年缺项，并扣除同期已有归属；夷陵战役的逐月进退尚未复原。',clean(shape(shu['geometry']).difference(occupied))))
  for f in list(fs):
   p=f['properties'];n=p['NAME']
   if n=='Cao Cao'and p['validFrom']==215 and p['validTo']==223:
    fs.append(new(f,'Cao Wei','Q320930','曹魏',220,223,'220年曹丕受禅建魏；将原来延续到223年的曹操势力记录按建国年切分。年内不按月拆分，北方轮廓沿用源记录。'));p['validTo']=219
   if n=='Cao Wei'and p['validFrom']==263 and p['validTo']==264:
    p.update(validTo=265,threeKingdomReview=TAG,representationNote='西晋代魏发生于传统咸熙二年十二月，换算为公历266年2月；265年不提前显示西晋。');changes.append({'name':n,'from':263,'to':265})
   if n=='Western Jin'and p['validFrom']==265:
    p.update(validFrom=266,validTo=280,threeKingdomReview=TAG)
   if n=='Eastern Wu'and p['validTo']==282:
    p.update(validTo=280,threeKingdomReview=TAG,representationNote='东吴280年灭亡，年度概览保留灭亡当年的政权记录；281年起不再显示。')
  jin=next(f for f in fs if f['properties']['NAME']=='Western Jin'and f['properties']['validFrom']==283)
  fs.append(new(jin,'Western Jin',jin['properties']['qid'],'西晋',281,282,'280年晋灭吴，281年起采用已收录的统一后轮廓，不延续东吴到282年。'))
  write('public/data/temporal/2.geojson',world)
  allrows=[f for c in index['centuries']for f in read(f'public/data/temporal/{c}.geojson')['features']]
  index['counts']['polityRecords']=len({f['properties']['sourceRecord']for f in allrows});index['changeYears']=sorted(set(index['changeYears'])|{220,221,223,224,266,281,283});index['threeKingdomsRevision']=TAG;write('public/data/temporal/index.json',index)
 facts=read('public/data/polity-facts.json');ids=json.loads((CACHE/'title-ids.json').read_bytes());people=json.loads((CACHE/'verified-people.json').read_bytes());records=[]
 for q,(source,rows)in ROSTERS.items():
  e=facts['entities'][q]
  if not(CACHE/(q+'.rulers-before.json')).exists():(CACHE/(q+'.rulers-before.json')).write_text(json.dumps(e['fields'].get('ruler',[]),ensure_ascii=False),encoding='utf8')
  e['fields']['ruler']=[]
  for title,cn,a,b,role in rows:
   person=ids[title];assert human(people[person]),title
   r={'value':person,'label':cn,'from':a,'to':b,'at':None,'roleLabel':role,'supplement':TAG,'rank':'preferred','citation':[source,'https://www.wikidata.org/wiki/'+person],'dateSource':'具名君主名录；按继位／退位年份，不以年号起年或出生年代替','inference':'交接年显示先后任职的君主，不表示共同在位；公历与传统年号跨年处注明换算。'}
   e['fields']['ruler'].append(r);facts['labels'][person]=cn;records.append({'country':q,**r})
  e['rulerScopeNote']='年度视图在继位或退位年可并列显示前后君主；不将追尊皇帝当作生前在位。'
  if q!='Q204077':
   a,b=min(r[2]for r in rows),max(r[3]for r in rows)
   e['fields']['government']=[{'value':'imperial-monarchy','label':'皇帝君主制、中央官署与地方州郡体系'+('；孙权称帝前为江东政权及吴王阶段'if q=='Q274488'else''),'from':a,'to':b,'at':None,'citation':[source],'supplement':TAG}]
 write('public/data/polity-facts.json',facts)
 prior=read('public/data/three-kingdoms-review.json')if(ROOT/'public/data/three-kingdoms-review.json').exists()else{}
 write('public/data/three-kingdoms-review.json',{'reviewedAt':'2026-11-01','geometryChanges':changes or prior.get('geometryChanges',[]),'rulers':records,'summary':{'rulerAppointments':len(records),'people':len({r['value']for r in records})},'sources':[SHU,WEI,WU],'limitations':['只修复已发现的起讫与身份断点，未重绘三国每一年的真实战争前线。','221—223年蜀汉的回补轮廓来自已收录224年几何，不等于刘备东征时最大势力范围。','263年灭蜀沿用源地图年末归属；年度界面不具备逐日控制线。']})
 print('Three Kingdoms appointments',len(records),'geometry fixes',len(changes),flush=True)

if __name__=='__main__':main()
