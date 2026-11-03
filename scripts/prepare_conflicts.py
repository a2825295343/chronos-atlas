"""Normalize COW and UCDP records. Keep annual activity and all participant terms.
Negative missing-value codes are never interpreted as troop or fatality counts.
"""
import csv,json,pathlib,collections,re
ROOT=pathlib.Path(__file__).resolve().parents[1];RAW=ROOT/'.local/conflicts';OUT=ROOT/'public/data'
SOURCE='https://correlatesofwar.org/data-sets/cow-war/'
def read(path):
 for encoding in ['utf-8-sig','cp1252']:
  try:return list(csv.DictReader(path.open(encoding=encoding,newline='')))
  except UnicodeDecodeError:pass
def n(value):
 try:
  x=float(str(value).strip());return int(x) if x>=0 else None
 except (ValueError,TypeError):return None
def clean(value):return str(value).strip() if value and not str(value).strip().startswith('-') else ''
def periods(row,short=False):
 result=[]
 for i in range(1,5 if short else 3):
  a=n(row.get(('StartYr' if short else 'StartYear')+str(i)));b=n(row.get(('EndYr' if short else 'EndYear')+str(i)))
  rawend=row.get(('EndYr' if short else 'EndYear')+str(i))
  if a and str(rawend).strip()=='-7':b=2014 if short else 2007
  if a and b and a<=b:result.append([a,b])
 return result
def participant(name,side,intervals,code=None,**extra):
 return dict(name=clean(name),side=str(side),periods=intervals,code=str(code) if n(code) else None,**{k:v for k,v in extra.items() if v is not None})
def main():
 wars={}
 def war(key,row,category,version,intervals):
  if key not in wars:wars[key]={'id':key,'name':row['WarName'].strip(),'category':category,'source':'COW '+version,'url':SOURCE,'participants':[],'periods':[], 'outcomeCode':n(row.get('Outcome'))}
  w=wars[key];w['periods']=sorted({tuple(x) for x in w['periods']+intervals});return w
 for row in read(ROOT/'.local/cow/war.csv'):
  spans=periods(row)
  if not spans:continue
  w=war('cow-inter-'+row['WarNum'],row,'国家间战争','国家间战争 4.0',spans)
  w['participants'].append(participant(row['StateName'],row['Side'],spans,row['ccode'],outcome=n(row['Outcome']),battleDeaths=n(row['BatDeath']),initiator=row['Initiator']=='1'))
 for row in read(RAW/'Extra-StateWarData_v4.0.csv'):
  spans=periods(row)
  if not spans:continue
  w=war('cow-extra-'+row['WarNum'],row,'殖民／帝国战争','体系外战争 4.0',spans)
  w['participants'].append(participant(row['SideA'],'1',spans,row['ccode1'],battleDeaths=n(row['BatDeath'])))
  if clean(row['SideB']):w['participants'].append(participant(row['SideB'],'2',spans,row['ccode2'],battleDeaths=n(row['NonStateDeaths'])))
 for row in read(RAW/'INTRA-STATE WARS v5.1 CSV.csv'):
  spans=periods(row,True)
  if not spans:continue
  w=war('cow-intra-'+row['WarNum'],row,'内战／国内冲突','国内战争 5.1',spans)
  w['participants']=[participant(row['SideA'],'1',spans,row['CcodeA']),participant(row['SideB'],'2',spans)]
  w['battleDeaths']=n(row['TotalBDeaths'])
 for row in read(RAW/'INTRA-STATE_State_participants v5.1 CSV.csv'):
  w=wars.get('cow-intra-'+row['WarNum']);spans=periods(row,True)
  if not w or not spans:continue
  for side in ['A','B']:
   if not clean(row['Side'+side]):continue
   p=participant(row['Side'+side],'1' if side=='A' else '2',spans,row.get('Ccode'+side),peakTheaterForces=n(row.get('Side'+side+'Peak TheatForces',row.get('Side'+side+'PeakTheatForces'))),peakNationalForces=n(row.get('Side'+side+'PeakTotForces')),battleDeaths=n(row.get('Deaths '+side)))
   old=next((x for x in w['participants'] if x['name']==p['name'] and x['side']==p['side'] and x['periods']==spans),None)
   if old:old.update({k:v for k,v in p.items() if v is not None})
   else:w['participants'].append(p)
 for row in read(RAW/'Non-StateWarData_v4.0.csv'):
  a=n(row['StartYear']);b=n(row['EndYear']);spans=[[a,b]] if a and b else []
  if not spans:continue
  w=war('cow-nonstate-'+row['WarNum'],row,'非国家势力战争','非国家战争 4.0',spans)
  for side in ['A','B']:
   for k in range(1,6):
    name=clean(row.get('Side'+side+str(k)))
    if name:w['participants'].append(participant(name,'1' if side=='A' else '2',spans))
  w['battleDeaths']=n(row['TotalCombatDeaths'])
 for row in read(RAW/'UcdpPrioConflict_v26_1.csv'):
  key='ucdp-'+row['conflict_id'];year=int(row['year'])
  if key not in wars:wars[key]={'id':key,'name':row['location']+' · '+('Government' if row['incompatibility']=='2' else row['territory_name'] or 'Territory'),'category':'年度武装冲突','source':'UCDP／PRIO 26.1','url':'https://ucdp.uu.se/conflict/'+row['conflict_id'],'annual':{},'participants':[],'periods':[],'location':row['location']}
  w=wars[key];w['annual'][str(year)]={'sideA':[row['side_a'].strip()],'sideB':[x.strip() for x in row['side_b'].split(',') if x.strip()],'secondaryA':[x.strip() for x in row['side_a_2nd'].split(',') if x.strip()],'secondaryB':[x.strip() for x in row['side_b_2nd'].split(',') if x.strip()],'intensity':int(row['intensity_level']),'type':int(row['type_of_conflict']),'issue':int(row['incompatibility']),'territory':row['territory_name'],'episodeEnded':row['ep_end']=='1','episodeEndDate':row['ep_end_date']}
 for w in wars.values():
  if w.get('annual'):
   ys=sorted(map(int,w['annual']));w['periods']=[]
   for y in ys:
    if w['periods'] and y==w['periods'][-1][1]+1:w['periods'][-1][1]=y
    else:w['periods'].append([y,y])
  w['from']=min(x[0] for x in w['periods']);w['to']=max(x[1] for x in w['periods'])
  # Dedup overlapping participant rows, retaining distinct dated service periods.
  unique={json.dumps(p,sort_keys=True):p for p in w['participants']};w['participants']=list(unique.values())
 previous=OUT/'conflicts.json';historical=[w for w in json.loads(previous.read_bytes())['wars'] if w['id'].startswith('historic-')] if previous.exists() else []
 output={'wars':list(wars.values())+historical,'coverage':{'COW':[1816,2014],'UCDP':[1946,2025]},'citations':['Sarkees & Wayman (2010), Resort to War.','Dixon & Sarkees (2016), A Guide to Intra-State Wars.','Davies, Pettersson & Öberg (2026), Organized violence 1989–2025, doi:10.1093/jopres/xjag046.'],'sources':[SOURCE,'https://ucdp.uu.se/downloads/'],'downloadMirror':'https://github.com/mateosuster/cow_data','notes':['UCDP 年度冲突不等于已达到每年一千人战死的战争；强度分开显示。','同一战争不是每年连续活跃；只按实际活动年度筛选。','兵力峰值属于整个战争／参战期，不代表每一年或相同日期的兵力。','COW 的战斗死亡不是全部军民死亡。','结果编码与按议题概括的原因分别显示，不将推断伪装为史料。']}
 (OUT/'conflicts.json').write_text(json.dumps(output,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print('Wars:',len(wars),'COW:',sum(k.startswith('cow') for k in wars),'UCDP conflict-years:',sum(len(w.get('annual',{})) for w in wars.values()),flush=True)
if __name__=='__main__':main()
