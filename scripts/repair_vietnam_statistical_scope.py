"""Military intervention is not US sovereignty over southern Vietnam.

Also remove Hainan from a ROC source polygon after the 1950 transition.
"""
from territory_repair_stage import Stage,read,write,clean
from shapely.geometry import box,shape
TAG='vietnam-statistical-scope-2026-11-02'
VIETNAM='https://history.state.gov/milestones/1969-1976/ending-vietnam'
def main():
 s=Stage(TAG,[19,20]);region=box(102,8,110,18)
 south=s.world(1960)['Republic of Vietnam'][1];south=clean(south.intersection(region))
 for a,b in s.periods(south,1967,2005,extra=[1973,1976]):
  if a<=1972:
   assignments=[('Republic of Vietnam','南越','Q180573',south,VIETNAM,'修正原始记录把美国军事介入区当成美国领土的关联错误；南越国家范围不等于政府逐村实际控制。',{'yearConvention':'南越与北越分别建档；美军参战在战争档案展示，不变成美国主权领土。'})]
  else:assignments=[]
  s.repair(south,a,b,assignments,remove=['United States of America'])
 hainan=box(108,18,112,20.5)
 for a,b in s.periods(hainan,1951,2026):
  s.repair(hainan,a,b,[],remove=['Republic of China'])
 s.finish('vietnam-statistical-scope-review.json')
 report=read('public/data/vietnam-statistical-scope-review.json');report['statisticalScope']={'Republic of China':{'before1949':'COW 710, China','from1949':'COW 713, Taiwan','1991Population':read('public/data/national-strength.json')['countries']['713']['observations']['1991']['population'],'note':'COW NMC按千人取整；不把中国大陆人口或GDP填进台湾。'}};write('public/data/vietnam-statistical-scope-review.json',report)
if __name__=='__main__':main()
