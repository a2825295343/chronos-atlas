"""Chinese render labels for reviewed people; retain their stable entity IDs."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAMES={
 'Q13050073':'桑乔·加尔塞斯（索夫拉韦）','Q1058250':'加西亚·加林德斯','Q143202':'皮埃尔·德德克尔','Q16569064':'弗朗西斯科·哈维尔·乌斯塔里斯','Q1991754':'阿斯纳尔·加林德斯二世','Q2040593':'加林多·阿斯纳雷斯一世','Q2103494':'庞西亚诺·科拉尔·阿科斯塔','Q2298546':'加林多·阿斯纳雷斯二世','Q446472':'让-巴蒂斯特·诺通','Q472257':'巴泰勒米·德特·德梅兰','Q472276':'费利克斯·德米勒纳雷','Q527479':'亨利·德布鲁克尔','Q52969':'弗雷德里克·冯·奥特','Q533339':'阿尔贝·约瑟夫·戈布莱·达尔维埃拉','Q546727':'西尔万·范德韦耶尔','Q569138':'朱尔·德比尔莱','Q5858987':'费尔明·费雷尔','Q5945970':'何塞·贝南西奥·洛佩斯','Q678535':'朱尔·马卢','Q721772':'朱尔·范登佩雷博姆','Q721781':'保罗·德斯梅特·德奈耶尔','Q887506':'何塞·马里亚·埃斯特拉达','Q949320':'加林多·加尔塞斯',
 'Q442570':'西尔班纳库斯','Q367598':'尼波提安努斯',
 'Q4997590':'帕兰塔卡二世（孙达罗朱罗）','Q3536701':'乌塔玛朱罗','Q7929581':'毗讫罗摩朱罗','Q709302':'俱卢东伽二世','Q7285772':'罗阇罗阇二世','Q7285611':'罗阇提罗阇二世','Q7285774':'罗阇罗阇三世','Q7285985':'罗阇因陀罗三世','Q3522578':'塞纳萨玛塔·维克拉马巴胡','Q6368216':'卡拉利亚德·班达拉',
}
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def main():
 facts=read('public/data/polity-facts.json');text=read('src/localization/text.zh.json')
 for q,name in NAMES.items():
  old=facts['labels'].get(q)
  if old and old!=name:text[old]=name
  facts['labels'][q]=name
 for e in facts['entities'].values():
  for field in ['ruler','headOfGovernment']:
   for r in e['fields'].get(field,[]):
    if r.get('value')in NAMES:r['label']=NAMES[r['value']]
 write('public/data/polity-facts.json',facts);write('src/localization/text.zh.json',text)
 print('Reviewed Chinese person labels',len(NAMES),flush=True)
if __name__=='__main__':main()
