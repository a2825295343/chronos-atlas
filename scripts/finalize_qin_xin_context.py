"""Person media identities and war aliases for corrected Qin/Xin map states."""
import hashlib,json,subprocess,urllib.parse
from territory_repair_stage import ROOT,read,write
from prepare_global_archive_review import human
from enrich_polities import simplify
from merge_historical_wars import main as merge
CACHE=ROOT/'.local/qin-xin-people';CACHE.mkdir(exist_ok=True)
NAMES={'Emperor Gaozu of Han':'刘邦','Xiang Yu':'项羽','Wang Mang':'王莽','Gongsun Shu':'公孙述','Gengshi Emperor':'刘玄','Liu Penzi':'刘盆子','Fan Chong':'樊崇','Wei Xiao':'隗嚣','Dou Rong':'窦融','Ying Bu':'英布','Zhang Han (Qin dynasty)':'章邯','Sima Xin':'司马欣','Sima Ang':'司马卬','Gong Ao':'共敖','Gong Wei':'共尉','Tian An':'田安','Tian Du':'田都','Tian Shi':'田市','Zhao Xie':'赵歇','Zhang Er':'张耳','Zang Tu':'臧荼','Han Guang':'韩广','Wei Bao':'魏豹','Shen Yang (ruler)':'申阳','Dong Yi (Qin dynasty)':'董翳','Han Cheng':'韩成','Zheng Chang':'郑昌','Xin of Han':'韩王信'}

def main():
 pool={};titles=sorted(NAMES)
 for i in range(0,len(titles),25):
  params=urllib.parse.urlencode(dict(action='wbgetentities',format='json',sites='enwiki',titles='|'.join(titles[i:i+25]),props='labels|claims|sitelinks',languages='zh-hans|zh|en',redirects='yes'));p=CACHE/(hashlib.sha1(params.encode()).hexdigest()+'.json')
  if not p.exists():subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','https://www.wikidata.org/w/api.php?'+params,'--output',str(p)],check=True)
  pool.update({q:e for q,e in json.loads(p.read_bytes())['entities'].items()if human(e)})
 write('.local/qin-xin-people/verified-people.json',pool)
 bytitle={e.get('sitelinks',{}).get('enwiki',{}).get('title'):q for q,e in pool.items()};people={name:bytitle[title]for title,name in NAMES.items()if title in bytitle}
 facts=read('public/data/polity-facts.json');changed=0
 for e in facts['entities'].values():
  for field in ['ruler','headOfGovernment']:
   for r in e.get('fields',{}).get(field,[]):
    if r.get('supplement')!='qin-xin-transition-2026-11-02'or r.get('label')not in people:continue
    q=people[r['label']];life=pool[q].get('claims',{})
    born=[int(v['value']['time'][:5])for c in life.get('P569',[])if(v:=simplify(c))and isinstance(v['value'],dict)and'time'in v['value']]
    died=[int(v['value']['time'][:5])for c in life.get('P570',[])if(v:=simplify(c))and isinstance(v['value'],dict)and'time'in v['value']]
    if any(y>r['to']for y in born)or any(y<r['from']for y in died):continue
    r['value']=q;r['citation']=list(dict.fromkeys([*r.get('citation',[]),'https://www.wikidata.org/wiki/'+q]));facts['labels'][q]=r['label'];changed+=1
 write('public/data/polity-facts.json',facts)
 db=read('public/data/historical-wars-supplements.json');entries={r['war']['id']:r for r in db['wars']}
 chu=entries['historic-chu-han']['war']
 for p in chu['participants']:p['polityNames']=['Han Kingdom (Liu Bang)','Han Dynasty']if p['side']=='1'else['Western Chu']
 kun=entries['historic-cn-kunyang']['war']
 for p in kun['participants']:
  if p['side']=='1':p.update(name='更始汉与绿林军',polityNames=['Gengshi Han'])
 def war(ident,title,a,b,participants,cause,result):
  ps=[[a,b]];url='https://zh.wikisource.org/wiki/後漢書/卷001上'
  entries[ident]=dict(war=dict(id=ident,name=title,category='中国历史战争与战役',source='2026-11-02新末汉初补录',url=url,periods=ps,participants=[dict(name=n,side=s,periods=periods,polityNames=ns)for n,s,ns,periods in participants],**{'from':a,'to':b}),detail=dict(id=ident,title=title,cause=cause,result=result,location=[112,33],sources=[url],scopeNote='多阶段内战概览；各派并非始终结盟，地方势力与军队控制范围随战事变化。'))
 war('historic-xin-collapse','绿林、赤眉起事与新朝覆亡',17,23,[('新朝','1',['Xin Dynasty'],[[17,23]]),('绿林及更始势力','2',['Gengshi Han'],[[17,23]]),('赤眉军','2',[],[[18,23]])],'灾荒、赋役及制度改革冲突等多重因素推动起事，各地军政集团逐渐扩大。','23年新朝覆亡；更始、赤眉及其他地区势力随后继续争夺政权，不能把起事视为一个始终统一的组织。')
 war('historic-eastern-han-unification','东汉建立及统一战争',25,36,[('刘秀及东汉军队','1',['Han Dynasty'],[[25,36]]),('赤眉汉','2',['Chimei Han'],[[25,27]]),('陇右隗氏','2',['Longyou Wei Authorities'],[[25,33]]),('成家','2',['Chengjia'],[[25,36]]),('东方竞争势力','2',['Eastern Han Rival Authorities'],[[25,29]])],'新朝覆亡后的诸政权争夺名义继承、郡县、军队及地方支持，刘秀逐步扩大控制。','赤眉、东方诸军、陇右与成家先后失败，36年东汉基本统一主要内地；对方阵营只是与东汉分别交战，不表示它们彼此结盟。')
 db['wars']=list(entries.values());write('public/data/historical-wars-supplements.json',db);merge()
 write('public/data/qin-xin-people-review.json',dict(reviewedAt='2026-11-02',matchedPeople=len(people),updatedOffices=changed,unresolvedTitles=[t for t in titles if t not in bytitle],note='精确人物条目且生卒年与任期相容者才替换本地人物ID；其余保留有史籍出处的本地身份，不误借同名人物画像。'))
 print('Exact person identities',len(people),'updated offices',changed)
if __name__=='__main__':main()
