"""Distinct Qin successor identities and the Han–Xin–Han territorial handover."""
import copy,hashlib
from territory_repair_stage import Stage,read,write,clean,label_path
from shapely.geometry import shape,mapping,box
from shapely import union_all
TAG='qin-xin-transition-2026-11-02'
SHIJI='https://zh.wikisource.org/wiki/史記/卷007'
HANSHU='https://zh.wikisource.org/wiki/漢書/卷099下'
HOUHAN='https://zh.wikisource.org/wiki/後漢書/卷001上'

def main():
 s=Stage(TAG,[-3,0]);facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json');labels={};identities={};appointments=[]
 known={r.get('label'):r.get('value')for e in facts['entities'].values()for r in e['fields'].get('ruler',[])if r.get('label')and str(r.get('value','')).startswith('Q')}
 def entry(q,label,n,lo,hi,holders,source=SHIJI,kind='诸侯王国'):
  e=facts['entities'].setdefault(q,dict(label=label,en=n,description='按具体政权与时期区分的档案；不使用战争、人物名录或分封总目作为国家身份。',fields={}))
  e['label']=label;e['fields']['ruler']=[r for r in e['fields'].get('ruler',[])if r.get('supplement')!=TAG]
  for name,a,b,role in holders:
   person=known.get(name)or'local:person-'+hashlib.sha1(name.encode()).hexdigest()[:16]
   row=dict(value=person,label=name,roleLabel=role,at=None,citation=[source],supplement=TAG,**{'from':a,'to':b});e['fields']['ruler'].append(row);facts['labels'][person]=name;appointments.append(dict(country=q,**row))
  e['fields']['government']=[dict(value=kind,label=kind,citation=[source],**{'from':lo,'to':hi})]
  e['rulerScopeNote']='按年记载年内先后统治者；交接年并列不代表全年共治。疆界为来源分期概览，不声称已经核定每月实控线。'
  return q
 def rewrite(names,n,label,q,a,b,note):
  stops=sorted({a,b+1,*[y for f in s.rows if f['properties']['NAME']in names for y in [f['properties']['validFrom'],f['properties']['validTo']+1]if a<y<=b]})
  for lo,end in zip(stops,stops[1:]):
   w=s.world(lo);rows=[(p,g)for name,(p,g)in w.items()if name in names]
   if not rows:continue
   g=clean(union_all([g for p,g in rows]));p=copy.deepcopy(rows[0][0])
   for name in names:s.replaced[name].append((lo,end-1))
   # A later rewrite may consume a polity created in this same revision.
   # Stage.replaced trims original rows only, so trim staged rows too.
   pending=[]
   for f in s.new:
    r=f['properties']
    if r['NAME']not in names or r['validTo']<lo or r['validFrom']>=end:pending.append(f);continue
    for left,right in [(r['validFrom'],min(r['validTo'],lo-1)),(max(r['validFrom'],end),r['validTo'])]:
     if left<=right:v=copy.deepcopy(f);v['properties'].update(validFrom=left,validTo=right);pending.append(v)
   s.new=pending
   p.update(NAME=n,SUBJECTO=n,qid=q,entityId=q,displayName=label,sourceName=rows[0][0]['NAME'],sourceQid=p.get('sourceQid',rows[0][0].get('qid')),validFrom=lo,validTo=end-1,sourceRecord=TAG+':'+hashlib.sha1(f'{n}:{lo}:{end}'.encode()).hexdigest()[:16],sourceUrl=SHIJI,accuracy=note,labelPath=label_path(g,label),memberOf='',components='')
   s.new.append(dict(type='Feature',properties=p,geometry=mapping(g)))
  s.labels[n]=label;s.identities[n]=q
 note='秦亡后分封及楚汉战争中的具体诸侯国；原始轮廓作分期参考。国家名、战争名与十八诸侯的集合条目已经分开，交接年不视为全年持续控制。'
 states=[
  ('Western Chu','Western Chu','西楚','western-chu',[('项羽',-206,-202,'西楚霸王')]),
  ('Zhai','Zhai Kingdom','翟国','zhai',[('董翳',-206,-206,'翟王')]),('Sai','Sai Kingdom','塞国','sai',[('司马欣',-206,-206,'塞王')]),('Yong','Yong Kingdom','雍国','yong',[('章邯',-206,-205,'雍王；205年为废丘残余据点阶段')]),
  ('Dai','Dai Kingdom (Qin successor)','代国','dai',[('赵歇',-206,-205,'代王，后恢复赵王称号')]),('Chang-shan','Changshan Kingdom','常山国','changshan',[('张耳',-206,-205,'常山王')]),
  ('Jibei','Jibei Kingdom','济北国','jibei',[('田安',-206,-206,'济北王')]),('Jiaodong','Jiaodong Kingdom','胶东国','jiaodong',[('田市',-206,-206,'胶东王')]),
  ('Jiujiang','Jiujiang Kingdom','九江国','jiujiang',[('英布',-206,-203,'九江王')]),('Henan','Henan Kingdom','河南国','henan',[('申阳',-206,-205,'河南王')]),('Yin','Yin Kingdom','殷国','yin',[('司马卬',-206,-205,'殷王')]),
  ('Hán','Han Kingdom (Han Cheng)','韩国','han-cheng',[('韩成',-206,-206,'韩王'),('郑昌',-206,-205,'韩王'),('韩王信',-205,-201,'韩王；区别于淮阴侯韩信')]),
  ('Linjiang','Linjiang Kingdom','临江国','linjiang',[('共敖',-206,-204,'临江王'),('共尉',-204,-202,'临江王')]),('Liaodong','Liaodong Kingdom','辽东国','liaodong',[('韩广',-206,-206,'辽东王')]),
  ('Han','Han Kingdom (Liu Bang)','汉国','han-liu-bang',[('刘邦',-206,-202,'汉王；前202年称帝')]),('Wei','Western Wei Kingdom','西魏国','western-wei',[('魏豹',-206,-205,'西魏王')]),
  ('Qi','Qi Kingdom (Chu-Han)','齐国','qi-chuhan',[('田都',-206,-206,'齐王'),('田荣',-206,-205,'齐王'),('田广',-205,-203,'齐王')]),('Yan','Yan Kingdom (Chu-Han)','燕国','yan-chuhan',[('臧荼',-206,-202,'燕王')])]
 for original,n,zh,slug,holders in states:
  q=entry('local:qin-successor-'+slug,zh,n,-206,-202,holders);rewrite({original},n,zh,q,-206,-203,note)
 # Do not backdate Xiang Yu's 206 partition into the Qin/rebellion phase.
 restored=[({'Western Chu'},'Restored Chu','楚国','local:restored-chu',[('楚怀王熊心',-208,-206,'楚怀王，后尊为义帝')]),({'Dai'},'Restored Zhao','赵国','local:restored-zhao',[('赵歇',-208,-206,'赵王')]),({'Jibei'},'Restored Qi','齐国','local:restored-qi',[('田市',-208,-206,'齐王；田荣实际主持军政')])]
 for ns,n,zh,q,holders in restored:entry(q,zh,n,-208,-207,holders);rewrite(ns,n,zh,q,-208,-207,'秦末复国军政势力，尚未发生前206年项羽分封；未前推后来的诸侯国名称。')
 rewrite({'Zhai','Qin Dynasty'},'Qin Dynasty','秦朝','Q7183',-208,-207,'前206年之前此来源仍表示秦朝，而非后来分封的翟国。')
 # The initial partition did not persist unchanged through 204 BCE.
 hq='local:qin-successor-han-liu-bang';qiq='local:qin-successor-qi-chuhan'
 for original in ['Sai Kingdom','Zhai Kingdom']:
  rewrite({original,'Han Kingdom (Liu Bang)'},'Han Kingdom (Liu Bang)','汉国',hq,-205,-204,'三秦降服后的汉王控制范围；仍使用来源概化轮廓，不宣称是同月战线。')
 rewrite({'Jibei Kingdom','Jiaodong Kingdom','Qi Kingdom (Chu-Han)'},'Qi Kingdom (Chu-Han)','齐国',qiq,-205,-204,'田荣重组齐地后不再把济北、胶东继续显示为不变的独立王国。')
 for original in ['Henan Kingdom','Yin Kingdom','Western Wei Kingdom','Yong Kingdom']:
  rewrite({original,'Han Kingdom (Liu Bang)'},'Han Kingdom (Liu Bang)','汉国',hq,-204,-204,'诸侯先后降汉或被征服后的年度概览；不将初封十八国机械延续到战争末年。')
 # Correct the Xin dynasty's source interval (6–29) to 9–23. Its last
 # source slices lose much of the interior without a replacement polity.
 base=clean(union_all([g for f,g in zip(s.rows,s.geoms)if f['properties']['NAME']=='Xin Dynasty'and f['properties']['validFrom']<=9<=f['properties']['validTo']]))
 assert base.area>200
 rewrite({'Xin Dynasty','Han Dynasty'},'Han Dynasty','西汉','Q7209',6,8,'王莽居摄仍属西汉阶段；新朝始于公元9年，不能把6—8年直接标为新朝。')
 interior=clean(base.intersection(box(97,20,126,42)))
 for a,b in s.periods(interior,9,22):s.repair(interior,a,b,[('Xin Dynasty','新朝','local:china-xin-dynasty',interior,HANSHU,'按新朝初期来源轮廓补接内地遗漏，保留匈奴、高句丽等已有势力。此为名义郡县范围的概化，不表示起义时期处处由中央直接实控。',{})])
 # Gengshi, early Eastern Han and major regional regimes replace the stale
 # Xin label. Core boxes are explicitly approximate, clipped to Han-era land.
 s.replaced['Xin Dynasty'].append((23,29))
 geng='local:gengshi-han';cheng='local:chengjia';wei='local:longyou-wei-xiao';hexi='local:hexi-dou-rong';chimei='local:chimei-han';east='local:eastern-han-rivals'
 for q,zh,n,lo,hi,holders in [(geng,'更始汉','Gengshi Han',23,25,[('刘玄',23,25,'更始帝')]),(cheng,'成家','Chengjia',25,36,[('公孙述',25,36,'成家皇帝')]),(wei,'陇右隗氏政权','Longyou Wei Authorities',23,33,[('隗嚣',23,33,'陇右军政领袖'),('隗纯',33,34,'继承军政势力')]),(hexi,'河西窦氏军政','Hexi Dou Authorities',25,36,[('窦融',25,36,'河西五郡军政领袖；并非独立称帝')]),(chimei,'赤眉汉','Chimei Han',25,27,[('刘盆子',25,27,'赤眉军拥立的皇帝'),('樊崇',25,27,'赤眉军主要军事领袖')]),(east,'东方诸军政','Eastern Han Rival Authorities',25,29,[('刘永',25,27,'竞争称帝的刘氏领袖'),('张步',25,29,'齐地军政领袖；不代表本区域所有势力')])]:entry(q,zh,n,lo,hi,holders,HOUHAN,'新末汉初军政权力（角色见人物说明）')
 for y in range(23,30):
  rows=[]
  if y>=25:rows.extend([('Chengjia','成家',cheng,interior.intersection(box(102,27,108.5,33.5)),HOUHAN,'公孙述成家政权的四川盆地核心概化；轮廓不是郡县实测界。',{}),('Hexi Dou Authorities','河西窦氏军政',hexi,base.intersection(box(95,36,104,41)),HOUHAN,'窦融主持的河西五郡军政核心；并非称帝国家。',{'regionalCollection':True})])
  rows.append(('Longyou Wei Authorities','陇右隗氏政权',wei,base.intersection(box(104,33.8,107.5,36.6)),HOUHAN,'隗嚣在陇右的军政核心概化，保留其他已有势力。',{}))
  if 25<=y<=27:rows.append(('Chimei Han','赤眉汉',chimei,interior.intersection(box(106.5,33.5,110.5,35.8)),HOUHAN,'赤眉入关至失败阶段的关中参考范围；25年内与更始政权先后交接，不表示全年占有。',{}))
  if y>=25:rows.append(('Eastern Han Rival Authorities','东方诸军政',east,interior.intersection(box(113.5,32,121.5,37.8)),HOUHAN,'刘永、刘纡、张步等在东方的竞争势力地理概览；不是统一国家或单一共同统治者。',{'regionalCollection':True}))
  rows.append(('Gengshi Han'if y<25 else'Han Dynasty','更始汉'if y<25 else'东汉',geng if y<25 else'Q7209',interior,HOUHAN,'新朝于23年覆亡；此后由更始、东汉与各地军政势力分列。保留内地旧郡县地理作为概化，未把西域等早期最大版图直接归入更始或初立东汉。',{}))
  s.repair(base,y,y,rows)
 # Keep the independently documented Sichuan and Longyou cores after 29,
 # instead of swallowing them in the next all-Han source snapshot.
 for y in range(30,37):
  for n,zh,q,core in [('Chengjia','成家',cheng,interior.intersection(box(102,27,108.5,33.5))),('Longyou Wei Authorities','陇右隗氏政权',wei,base.intersection(box(104,33.8,107.5,36.6)))]:
   if n.startswith('Longyou')and y>33:continue
   s.repair(core,y,y,[(n,zh,q,core,HOUHAN,'独立军政势力延续期间的核心概化，不能把东汉名义疆域直接等同实际统一。',{})],remove=['Han Dynasty'])
 s.finish('qin-xin-transition-review.json')
 # Stage.finish updates identities; retain all manually initialized archives.
 cur=read('public/data/curated-facts.json');write('public/data/polity-facts.json',facts)
 report=read('public/data/qin-xin-transition-review.json');report['appointments']=appointments;report['limitations']+=['十八诸侯源轮廓本身仍为概化；本轮未制造逐月边界。','新末汉初地方势力用有出处的地理核心补绘，部分边缘与短期竞争者仍未细分。'];write('public/data/qin-xin-transition-review.json',report)
if __name__=='__main__':main()
