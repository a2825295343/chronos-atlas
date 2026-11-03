"""Named late rulers for newly separated states, with conflicting dates visible."""
from territory_repair_stage import read,write
TAG='coverage-ruler-followups-2026-11-01'
def main():
 facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json');records=[]
 for e in facts['entities'].values():e['fields']['ruler']=[r for r in e['fields'].get('ruler',[])if r.get('supplement')!=TAG]
 def add(country,key,label,a,b,source,**extra):
  r={'value':key,'label':label,'from':a,'to':b,'at':None,'roleLabel':'苏丹／本地君主','citation':source if isinstance(source,list)else[source],'supplement':TAG,'identitySource':'具名历史名录；local:person 身份表示未关联到已核定的唯一维基人物实体。',**extra};facts['entities'][country]['fields'].setdefault('ruler',[]).append(r);facts['labels'][key]=label;records.append({'country':country,**r})
 source='https://en.wikipedia.org/wiki/Dahham_ibn_Dawwas'
 add('local:riyadh-dahham','local:person:khumayyis-riyadh','胡迈伊斯',1737,1740,source,roleLabel='扎拉阿家族幼主的摄政；1740年交接')
 add('local:riyadh-dahham','local:person:dahham-ibn-dawwas','达哈姆·本·达瓦斯',1740,1744,source,roleLabel='扎拉阿家族幼主的摄政')
 add('local:riyadh-dahham','local:person:dahham-ibn-dawwas','达哈姆·本·达瓦斯',1745,1773,source,roleLabel='利雅得地方统治者；1773年被第一沙特国家取代')
 add('local:travancore','Q1766094','奇蒂拉·蒂鲁纳尔·巴拉拉马·瓦尔马',1924,1949,'https://en.wikipedia.org/wiki/Chithira_Thirunal_Balarama_Varma',roleLabel='名义君主（1924年继位，1931年取得完全执政权）')
 add('local:travancore','local:person:sethu-lakshmi-bayi','塞图·拉克希米·巴伊',1924,1931,'https://en.wikipedia.org/wiki/Sethu_Lakshmi_Bayi',roleLabel='摄政女王，未当作君主去世后才继位')
 source=['https://en.wikipedia.org/wiki/Kathiri','https://www.chiefacoins.com/Database/Countries/Kathiri_State_of_Seiyun.htm']
 for key,label,a,b in [('ghalib-muhsin','加利卜·本·穆赫辛',1848,1870),('mansur-ghalib','曼苏尔·本·加利卜',1870,1880),('muhsin-ghalib','穆赫辛·本·加利卜',1880,1929),('ali-mansur','阿里·本·曼苏尔',1929,1938),('jafar-mansur','贾法尔·本·曼苏尔',1938,1949)]:add('local:kathiri-sultanate','local:person:kathiri-'+key,label,a,b,source,approximate=True,inference='部分名录交接年有一年左右差异；依具名苏丹名录补入，不以出生或死亡年份推断任期。')
 add('local:kathiri-sultanate','local:person:kathiri-husayn-ali','侯赛因·本·阿里（姓名异文待复核）',1949,1967,source,approximate=True,reviewAfter=1948,reviewNote='公开名录存在侯赛因／穆赫辛及1948／1949年交接的差异，需要用当时文书继续核定。',inference='保留名录分歧，不将不同拼写伪装成多个同时在位的苏丹。')
 source=['https://ci.nii.ac.jp/ncid/BD14749694','https://en.wikipedia.org/wiki/Qu%27aiti']
 for key,label,a,b in [('awadh-umar','阿瓦德一世·本·欧麦尔',1867,1909),('ghalib-awadh','加利卜一世·本·阿瓦德',1909,1922),('umar-awadh','欧麦尔·本·阿瓦德',1922,1936),('salih-ghalib','萨利赫·本·加利卜',1936,1956),('awadh-salih','阿瓦德二世·本·萨利赫',1956,1966),('ghalib-second','加利卜二世·本·阿瓦德',1966,1967)]:add('local:quaiti-sultanate','local:person:quaiti-'+key,label,a,b,source,approximate=True,inference='采用名录与专门传记所用年表；部分交接年在公开资料中有一年差异，1935／1936和1955／1956年的差异保留待核。')
 # Protectorate status is a relationship, not an assertion that the British
 # monarch is the local sultan. Local reigns above remain the primary display.
 cur['relations']=[r for r in cur['relations']if r.get('supplement')!=TAG]
 for n,lo,source in [('Kathiri Sultanate',1918,'https://en.wikipedia.org/wiki/Kathiri'),('Quaiti Sultanate',1888,'https://en.wikipedia.org/wiki/Qu%27aiti')]:cur['relations'].append({'id':TAG+':'+n,'kind':'protectorate','child':n,'parent':'United Kingdom','from':lo,'to':1967,'detail':'英国保护关系与本地苏丹的王权、内部行政分开表示；并非英国国王取代本地苏丹。','source':source,'supplement':TAG})
 write('public/data/polity-facts.json',facts);write('public/data/curated-facts.json',cur);write('public/data/coverage-ruler-followup.json',{'reviewedAt':'2026-11-01','records':records,'summary':{'records':len(records),'countries':len({r['country']for r in records})},'limitations':['部分南阿拉伯名录存在姓名拼写和交接年份差异，已逐条保留说明。','已知姓名的历史人物可以使用本地稳定身份，不捏造一个维基数据Q编号。']});print('Additional sourced local reigns',len(records),flush=True)
if __name__=='__main__':main()
