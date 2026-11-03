"""Repair an Oman polygon incorrectly identified as a history-of-Qatar article.

Modern outer coast/border is a locating mask; the 1913 interior outline is a
dated reconstruction, not a claim to surveyed 1950 front lines.
"""
import copy
from territory_repair_stage import ROOT,Stage,read,write,clean
from shapely.geometry import shape,box
from shapely import union_all

TAG='qatar-oman-identity-2026-11-02'
QATAR='https://diwan.gov.qa/en/About-Qatar/History-of-Qatar'
TREATY='https://qdl.qa/en/keeping-lion-bay-anglo-qatar-treaty-1916'
OMAN='https://www.qdl.qa/en/financial-troubles-said-bin-taimur'
INTERIOR='https://www.rafmuseum.org.uk/research/online-exhibitions/an-enduring-relationship-a-history/oman-and-the-cold-war/'

def main():
 stage=Stage(TAG,[19,20])
 admin=read('.local/presentation/admin0.geojson')['features']
 def mask(n):return clean(union_all([shape(f['geometry'])for f in admin if f['properties']['NAME_EN']==n]))
 qatar=mask('Qatar');oman=mask('Oman')
 assert not qatar.is_empty and not oman.is_empty
 # The source's Qatar Protectorate polygon is actually the Oman outline.
 interior=clean(union_all([g for f,g in zip(stage.rows,stage.geoms)if f['properties']['NAME']=='Imamate of Oman'and f['properties']['validFrom']<=1913<=f['properties']['validTo']]).intersection(oman))
 assert interior.area>5
 stage.replaced['Qatar Protectorate'].append((1947,1955))
 stage.replaced['United Kingdom Colony - Qatar'].append((1916,2024))
 stage.replaced['United Kingdom Colony - Oman'].append((1947,2024))
 for a,b in stage.periods(qatar,1916,2024,[1971,1972]):
  name='Qatar Protectorate'if a<=1971 else'State of Qatar'
  extra=dict(sovereignName='United Kingdom',sovereignQid='Q145',territoryType='protectorate')if a<=1971 else{}
  note='1916年条约下的卡塔尔保护关系；1971年9月3日独立，交接年仍保留保护地阶段说明。外沿采用现代半岛定位参考，不表示争议边界当年已经划定。'if a<=1971 else'1971年独立后的卡塔尔；剔除英国殖民地残留轮廓。外沿为现代定位参考。'
  remove=[n for n in stage.world(a)if 'Qatar'in n or n in ['Sultanate of Muscat and Oman','United Kingdom Colony - Oman']]
  stage.repair(qatar,a,b,[(name,'卡塔尔','local:qatar-protectorate'if a<=1971 else'Q846',qatar,QATAR,note,extra)],remove=remove)
 # Re-identify the bad Oman polygon and remove the spurious British colony
 # partition. Keep the autonomous interior separate during the reviewed span.
 for a,b in stage.periods(oman,1947,2024,[1954,1956,1970,1971]):
  n='Sultanate of Muscat and Oman'if a<=1970 else'Sultanate of Oman'
  q='Q157734'if a<=1970 else'Q842';label='马斯喀特和阿曼'if a<=1970 else'阿曼'
  assignments=[]
  if a<=1955:assignments.append(('Imamate of Oman','阿曼伊玛目国','local:oman-imamate-1913',interior,INTERIOR,'内陆自治政权；沿用1913年来源轮廓作核心范围概化，1920年锡卜安排后延续自治。1954—1955年战事与年内控制变化未作逐日测绘。',{}))
  assignments.append((n,label,q,oman,OMAN,'马斯喀特苏丹国及后继阿曼；英国军事、外交影响不等于英国直接殖民统治。外沿按现代地理定位，内陆按本轮时期分列；1970年为改名与苏丹交接年。',{}))
  remove=['Qatar Protectorate','United Kingdom Colony - Oman','Sultanate of Muscat and Oman','Sultanate of Oman','Imamate of Oman']
  stage.repair(oman,a,b,assignments,remove=remove)
 # The old source extends into neighbouring territory. It is entirely an
 # identity error, so do not leave a Qatar-labelled remnant outside Oman.
 stage.replaced['Qatar Protectorate'].append((1947,1955))
 stage.finish('qatar-oman-identity-review.json')
 facts=read('public/data/polity-facts.json')
 old=copy.deepcopy(facts['entities']['Q944391'])
 old.update(label='卡塔尔',qid='local:qatar-protectorate',description='1916年条约下由阿勒萨尼家族治理的卡塔尔；英国掌握部分对外事务，1971年独立。')
 old['fields'].pop('instanceOf',None)
 old['fields']['government']=[dict(value='monarchy',label='世袭酋长制（英国保护关系）',**{'from':1916,'to':1971},citation=[TREATY])]
 old['fields']['religion']=[dict(value='Q432',label='伊斯兰教',**{'from':1916,'to':1971},citation=[QATAR])]
 facts['entities']['local:qatar-protectorate']=old
 imamate=copy.deepcopy(facts['entities']['Q2342282'])
 imamate.update(label='阿曼伊玛目国',en='Imamate of Oman (1913–1959)',description='以尼兹瓦为中心的阿曼内陆伊巴德派伊玛目政权；与马斯喀特苏丹国分列，不把历史地理区域本身当作国家。')
 imamate['fields'].pop('instanceOf',None)
 for field,label in [('government','伊巴德派推举伊玛目制'),('religion','伊斯兰教伊巴德派'),('capital','尼兹瓦')]:
  imamate['fields'][field]=[dict(value=label,label=label,citation=[INTERIOR],**{'from':1913,'to':1959})]
 facts['entities']['local:oman-imamate-1913']=imamate
 # A historical subject page must not act as a country or person office.
 facts['entities']['Q944391']['fields']['ruler']=[]
 write('public/data/polity-facts.json',facts)
 flags=read('public/data/flags.json')
 if flags['entities'].get('Q944391'):flags['entities']['local:qatar-protectorate']=copy.deepcopy(flags['entities']['Q944391'])
 if flags['entities'].get('Q2342282'):flags['entities']['local:oman-imamate-1913']=copy.deepcopy(flags['entities']['Q2342282'])
 write('public/data/flags.json',flags)
 cur=read('public/data/curated-facts.json')
 cur['identities']['Qatar Protectorate']='local:qatar-protectorate'
 cur['identities']['Imamate of Oman']='local:oman-imamate-1913'
 cur['relations']=[r for r in cur['relations']if not str(r.get('id','')).startswith(TAG)]
 cur['relations'].append(dict(id=TAG+':protection',kind='protectorate',child='Qatar Protectorate',parent='United Kingdom',**{'from':1916,'to':1971},title='英卡保护条约',detail='英国保障对外安全并限制卡塔尔独立对外交往；卡塔尔由本地统治者治理。1916年11月签署，1971年9月3日终止；不是英国直接统治的殖民省。',source=TREATY))
 write('public/data/curated-facts.json',cur)
 # Persist reviewed labels in raw geometry as well as map/detail localizers.
 from polity_display_names import DISPLAY_NAMES
 counts={}
 for c in stage.index['centuries']:
  path=f'public/data/temporal/{c}.geojson';db=read(path);changed=0
  for f in db['features']:
   p=f['properties'];label=DISPLAY_NAMES.get(p['NAME'])
   if p['NAME']=='Imamate of Oman'and 1913<=p['validFrom']<=1959:p.update(sourceQid=p.get('sourceQid',p['qid']),qid='local:oman-imamate-1913',entityId='local:oman-imamate-1913',displayName='阿曼伊玛目国');changed+=1
   if label and p.get('displayName')!=label:p['displayName']=label;changed+=1
  if changed:write(path,db);counts[c]=changed
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  d=read(path);d.update(DISPLAY_NAMES);write(path,d)
 report=read('public/data/qatar-oman-identity-review.json');report.update(nameUpdates=counts,explanation='原名Qatar Protectorate错误套用了阿曼地理轮廓并指向History of Qatar；已按地理位置重建身份。',sources=[QATAR,TREATY,OMAN,INTERIOR]);write('public/data/qatar-oman-identity-review.json',report)

if __name__=='__main__':main()

