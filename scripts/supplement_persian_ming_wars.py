"""Ottoman–Iranian and late Ming campaigns, plus dated CCP participation."""
from territory_repair_stage import read,write
TAG='persian-ming-wars-2026-11-02'
SAF='https://islamicceramics.ashmolean.org/Iznik/safdwar.htm'
IRAN='https://www.iranicaonline.org/articles/ottoman-persian-relations-ii-afsharid-and-zand-periods/'
MING='https://zh.wikisource.org/wiki/清史稿/卷215'
def main():
 db=read('public/data/historical-wars-supplements.json');rows={r['war']['id']:r for r in db['wars']};added=[]
 def war(slug,title,a,b,left,right,cause,result,sources,location,commanders=()):
  ident='historic-'+slug;ps=[[a,b]]
  participants=[dict(name=n,side=s,periods=periods or ps,polityNames=aliases)for s,group in [('1',left),('2',right)]for n,aliases,periods in group]
  note='战争时期含作战、谈判及停战阶段，不表示逐年持续同等战斗；阵营为本条战事关系，不据此认定同侧所有势力相互结盟。未自动绘制未经核定的逐年占领线。'
  w=dict(id=ident,name=title,category='历史战争与战役',source='2026-11-02有来源补录',url=sources[0],participants=participants,periods=ps,scopeNote=note,**{'from':a,'to':b})
  d=dict(id=ident,title=title,cause=cause,result=result,sources=sources,location=location,commanders=list(commanders),scopeNote=note,strengthAssessment='尚无同一时点、同一战区且可比的完整兵力，不将传说数字、全国人口或伤亡数作为投入兵力。')
  rows[ident]=dict(war=w,detail=d);added.append(ident)
 ott=[('Ottoman Empire',['Ottoman Empire'],None)]
 saf=[('Safavid Dynasty',['Safavid Dynasty','Safavid Empire'],None)]
 for slug,title,a,b,cause,result,commanders in [
  ('ottoman-safavid-1532','奥斯曼—萨法维战争（1532—1555）',1532,1555,'两国围绕东安纳托利亚、阿塞拜疆、伊拉克及边疆附属势力的竞争，伴随宗教政治动员与王室争端。','1555年阿马西亚和约确认奥斯曼在伊拉克等地的控制与双方边界安排。主要远征分数轮，不把23年均画成持续交战。',['苏莱曼一世','塔赫玛斯普一世']),
  ('ottoman-safavid-1578','奥斯曼—萨法维战争（1578—1590）',1578,1590,'萨法维继承危机、边疆库尔德势力和高加索争端为奥斯曼扩张创造条件。','1590年伊斯坦布尔和约使萨法维承认重大领土损失；其中部分地区后来被阿拔斯一世收复。',['穆拉德三世','穆罕默德·胡达班达、阿拔斯一世']),
  ('ottoman-safavid-1603','奥斯曼—萨法维战争（1603—1612）',1603,1612,'阿拔斯一世利用奥斯曼内部危机，试图收复1590年割让的高加索与阿塞拜疆领土。','1612年纳苏赫帕夏和约大体恢复1555年边界，并规定丝绸等交付安排。',['阿拔斯一世','艾哈迈德一世']),
  ('ottoman-safavid-1615','奥斯曼—萨法维战争（1615—1618）',1615,1618,'前次和约的履行、贡丝与边境争执导致战争重开。','1618年塞拉夫和约维持主要边境安排并调整交付义务，未解决全部后续争端。',['阿拔斯一世','奥斯曼二世时期军队']),
  ('ottoman-safavid-1623','奥斯曼—萨法维战争（1623—1639）',1623,1639,'巴格达内部权力争夺与萨法维进军，引发奥斯曼为收复伊拉克而多次出征。','1638年奥斯曼夺回巴格达，1639年祖哈布和约确定长期有效的主要边界格局。',['阿拔斯一世、萨菲一世','穆拉德四世'])]:
  war(slug,title,a,b,ott,saf,cause,result,[SAF,'https://www.iranicaonline.org/articles/chronology-of-iranian-history-part-1/'],[44,37],commanders)
 war('ottoman-persia-1723','奥斯曼侵入波斯与霍塔克战争（1723—1727）',1723,1727,ott,[('波斯地方及萨法维残余抵抗',['Safavid Dynasty'],[[1723,1725]]),('Hotak Dynasty',['Hotak Dynasty','Hotak Empire'],[[1726,1727]])],'萨法维中央政权崩溃后，奥斯曼进军波斯西部和高加索；其后与霍塔克统治者争夺领土。','1727年哈马丹安排确认奥斯曼所占若干领土；波斯各竞争政权并非一个协调一致的联盟。',[IRAN],[47,35],['艾哈迈德三世','阿什拉夫·霍塔克'])
 for slug,title,a,b,result in [
  ('ottoman-persia-1730','奥斯曼—波斯战争（1730—1732）',1730,1732,'塔赫玛斯普二世的失败及1732年和约引发国内政治后果，纳迪尔随后废黜他。'),
  ('ottoman-persia-1733','纳迪尔与奥斯曼战争（1733—1736）',1733,1736,'经历巴格达围攻及高加索战事后，双方通过谈判恢复主要旧边界；1736年纳迪尔正式称沙阿。'),
  ('ottoman-persia-1743','奥斯曼—阿夫沙尔战争（1743—1746）',1743,1746,'1746年库尔丹条约大体确认1639年的边界，并处理宗教、朝觐及外交安排。')]:
  actors=[('纳迪尔及萨法维名义王权',['Safavid Dynasty','Afsharid Iran'],None)]if a<1736 else[('Afsharid Iran',['Afsharid Iran'],None)]
  war(slug,title,a,b,ott,actors,'波斯在萨法维崩溃后争取恢复西部与高加索控制，纳迪尔的军事扩张与宗教外交要求促成多轮战事。',result,[IRAN],[44,36],['纳迪尔','马哈茂德一世时期奥斯曼军队'])
 war('ottoman-zand-basra','桑德波斯围攻巴士拉与奥斯曼战争（1775—1779）',1775,1779,ott,[('Zand Dynasty',['Zand Dynasty'],None)],'卡里姆汗试图夺取巴士拉的商贸与海湾战略地位，并与奥斯曼属地统治者冲突。','1776年巴士拉陷落；1779年卡里姆汗去世后桑德驻军撤退，奥斯曼恢复当地控制。',[IRAN,'https://www.iranicaonline.org/articles/basra/'],[47.8,30.5],['卡里姆汗、萨迪克汗'])
 war('ottoman-qajar-1821','奥斯曼—卡扎尔战争（1821—1823）',1821,1823,ott,[('Qajar Dynasty',['Qajar Dynasty','Persia'],None)],'边境部族、朝觐与通商争端，加上双方区域竞争，引发东西两个战区的战争。','1823年第一次埃尔祖鲁姆条约结束战争，原则上承认既有主要边界；COW战斗门槛记录止于1822年，不等于1823年和约不存在。',['https://belgeler.gov.tr/eng/full-text/112/tur'],[44,39],['阿拔斯·米尔扎','穆罕默德·阿里·米尔扎'])
 war('ming-peasant-1627','明末农民战争（主要起事阶段）',1627,1644,[('Ming Dynasty',['Ming Dynasty'],None)],[('李自成及大顺军',['Li Zicheng','Shun Dynasty'],[[1630,1644]]),('张献忠及其军队',['Zhang Xianzhong','Daxi','Daxi Dynasty'],[[1630,1644]]),('其他地方起事武装',[],None)],'灾荒、财政和军饷危机、赋役负担以及地方社会冲突共同推动多地起事；各路军队并非始终统一行动。','1644年李自成攻入北京，明帝自尽；南明、大顺、大西及清军之间的战争继续，不能将1644年视为全部战争终结。',['https://zh.wikisource.org/wiki/明史/卷309'],[109,35],['李自成、张献忠','孙传庭、洪承畴等明将'])
 war('ming-qing-1618','后金／清与明战争（1618—1644）',1618,1644,[('明朝',['Ming Dynasty'],None)],[('后金',['Later Jin','Later Jin Dynasty'],[[1618,1635]]),('清朝',['Qing Dynasty'],[[1636,1644]])],'后金崛起、辽东权力与经济矛盾、明朝边防和双方政治对立引发多次战争。','萨尔浒、辽沈和松锦等战役改变辽东格局，1644年清军入关；此后与南明及其他势力的战争分另条记载。',['https://zh.wikisource.org/wiki/明史/卷259'],[123,41],['努尔哈赤、皇太极、多尔衮','熊廷弼、袁崇焕、洪承畴'])
 war('shanhai-1644','山海关之战',1644,1644,[('清军',['Qing Dynasty'],None),('吴三桂部',[],None)],[('大顺军',['Li Zicheng','Shun Dynasty'],None)],'明朝北京政权覆灭后，吴三桂与李自成决裂并与多尔衮联合，争夺山海关与入京通道。','大顺军战败撤退，清军随后进入北京；吴三桂部参战不等于所有明朝军队都与清结盟。',['https://zh.wikisource.org/wiki/清史稿/卷5'],[119.75,40],['多尔衮、吴三桂','李自成'])
 war('qing-southern-ming','清与南明战争（主要阶段）',1644,1662,[('清朝',['Qing Dynasty'],None)],[('南明诸政权',['Southern Ming'],None),('抗清地方军及前大西军',[],[[1647,1662]])],'清朝向南扩张，南明各朝廷与地方军事集团试图维持或恢复明朝统治。','弘光、隆武、永历等政权先后失败，1662年永历帝被杀；郑氏海上政权仍继续存在，不把1662年当作所有抗清力量的终点。',['https://zh.wikisource.org/wiki/南疆逸史'],[111,27],['多铎、洪承畴、吴三桂等','史可法、何腾蛟、瞿式耜、李定国、孙可望等（分阶段）'])
 war('hanzhong-resistance','陕南抗清战争（贺珍、孙守法等）',1645,1647,[('清朝',['Qing Dynasty'],None)],[('陕南抗清诸军',['Southern Shaanxi Anti-Qing Forces','Southern Ming'],None)],'部分原大顺、明军及地方武装在降清后反清，借明朝旗号或旧军组织动员，争夺汉中、兴安与秦岭通道。','1646年清军进入汉中，诸部转入兴安及山地；1647年孙守法等失败被杀，部分余部转移。',[MING],[108.5,33],['贺珍、孙守法、刘体纯、武大定','豪格、鳌拜、孟乔芳等'])
 db['wars']=list(rows.values());write('public/data/historical-wars-supplements.json',db)
 from merge_historical_wars import main as merge
 merge()
 conflict=read('public/data/conflicts.json');details=read('public/data/war-details.json');dd={r['id']:r for r in details['wars']}
 for w in conflict['wars']:
  if w['id']=='cow-intra-723.5':
   for p in w['participants']:
    if p['side']=='1':p.update(displayName='国民政府与国民党军',polityPeriods=[dict(name='Republic of China',**{'from':1945,'to':1950})])
    else:p.update(displayName='中国共产党及人民解放军',polityPeriods=[dict(name='Communist Party of China',**{'from':1945,'to':1950}),dict(name="People's Republic of China",**{'from':1949,'to':1950})])
   dd[w['id']]={**dd.get(w['id'],{}),'id':w['id'],'title':'解放战争／第二次国共内战','reviewedHistorical':True,'cause':'抗日战争结束后，国共围绕国家政权、军队整编和接收地区的冲突扩大。','result':'中国共产党领导的军队取得大陆主要地区控制，1949年中华人民共和国成立，国民政府迁台；COW本条至1950年，不等于后续海峡冲突全部结束。','sources':['https://history.state.gov/milestones/1945-1952/chinese-rev'],'location':[114,34]}
 dd['cow-extra-309']={**dd.get('cow-extra-309',{}),'id':'cow-extra-309','mergeHistorical':'historic-ottoman-qajar-1821'}
 # Annual UCDP inherits the coalition identities from COW. Use the same
 # explanation and title in overlap years instead of an unlabeled episode.
 dd['ucdp-202']={**dd.get('ucdp-202',{}),**dd['cow-intra-723.5'],'id':'ucdp-202'}
 details['wars']=list(dd.values());write('public/data/conflicts.json',conflict);write('public/data/war-details.json',details)
 write('public/data/persian-ming-wars-review.json',dict(reviewedAt='2026-11-02',added=added,updated=['cow-intra-723.5','ucdp-202','cow-extra-309'],limitations=['战争及战役条目并非全球穷尽。','复杂内战阵营不表示其各部相互结盟；缺少精确同日兵力时不虚构数字。']))
 print('Added campaign records',len(added))
if __name__=='__main__':main()
