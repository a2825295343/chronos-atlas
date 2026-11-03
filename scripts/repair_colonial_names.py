"""Repair current generated colony labels; rerun after upstream territory stages."""
import json
from colonial_naming import colonial_label
from territory_repair_stage import ROOT,read,write,label_path
SOURCE='https://tcmb.culture.tw/zh-tw/detail?id=20230901000001&indexCode=BOCH_CountryCulture_11'
TAG='colonial-geographic-names-2026-10-31'
def main():
    labels={};records=[]
    for path in (ROOT/'public/data/temporal').glob('*.geojson'):
        data=json.loads(path.read_bytes());changed=False
        for f in data['features']:
            p=f['properties'];name=p['NAME']
            if ' Colony - ' not in name:continue
            nation,country=name.split(' Colony - ',1)
            old=p.get('displayName',name);label=colonial_label(nation,country,old)
            if nation=='United Kingdom' and country=='China' and old=='英属香港及在华租借地':label=old
            if label==old and name!='Netherlands Colony - Taiwan':continue
            p.update(displayName=label,labelPath=label_path(f['geometry'],label))
            if name=='Netherlands Colony - Taiwan':
                p.update(qid='local:dutch-formosa',entityId='local:dutch-formosa',sourceQid=p.get('sourceQid','Q170072'),sovereignName='Dutch Republic',sovereignQid='Q170072',sourceUrl=SOURCE,identityReviewed=True,identityCorrection='按17世纪荷兰东印度公司在台湾的殖民行政区命名，不能套用1912年才成立的中华民国国名。',territoryType='colony',representationNote='荷兰东印度公司在台湾的殖民控制区；不表示荷兰已实际统治全岛所有原住民社群。内界沿用源GIS的概化轮廓。')
            labels[name]=label;changed=True;records.append({'name':name,'from':p['validFrom'],'to':p['validTo'],'label':label})
        if changed:path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    # Update every label surface rather than only the visible country heading.
    for filename in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
        names=read(filename);names.update(labels);names['Netherlands Colony - Taiwan']='荷属台湾';write(filename,names)
    path=ROOT/'src/color-groups.mjs';text=path.read_text(encoding='utf8');start=text.index('=')+1;groups=json.loads(text[start:].strip().removesuffix(';'));groups.update(labels);groups['Netherlands Colony - Taiwan']='荷属台湾';path.write_text('export const colorGroups='+json.dumps(groups,ensure_ascii=False)+';\n',encoding='utf8')
    # Preserve the existing color while correcting its geographic identity key.
    path=ROOT/'src/color-registry.mjs';text=path.read_text(encoding='utf8');start=text.index('=')+1;colors=json.loads(text[start:].strip().removesuffix(';'));colors.setdefault('荷属台湾',colors.get('荷属中华民国','#65a6ce'));path.write_text('// Fixed historical polity colors. Regenerate explicitly with scripts/prepare_stable_colors.mjs.\nexport const polityColors='+json.dumps(colors,ensure_ascii=False,indent=1)+';\n',encoding='utf8')
    cur=read('public/data/curated-facts.json');cur['identities']['Netherlands Colony - Taiwan']='local:dutch-formosa';write('public/data/curated-facts.json',cur)
    facts=read('public/data/polity-facts.json');e=facts['entities'].setdefault('local:dutch-formosa',{'label':'荷属台湾','en':'Dutch Formosa','description':'荷兰东印度公司在台湾的殖民行政区；与荷兰共和国中央政府、荷属东印度及后来中华民国分开。','fields':{}})
    def fact(value,label,field):return {'value':value,'label':label,'from':1624,'to':1662,'at':None,'citation':[SOURCE],'supplement':TAG,'roleLabel':field}
    e['fields']['government']=[fact('voc-colonial-administration','荷兰东印度公司殖民行政，由台湾长官及评议会管理，上承巴达维亚公司当局','殖民行政机构')]
    e['fields']['capital']=[fact('tayouan','大员／热兰遮堡（今台南安平）；为殖民行政中心，不是全岛原住民共同首都','行政中心')]
    facts['labels']['local:dutch-formosa']='荷属台湾';write('public/data/polity-facts.json',facts)
    write('public/data/colonial-name-review.json',{'revision':TAG,'reviewedAt':'2026-10-31','records':records,'source':SOURCE,'policy':'殖民地采用地理或当时行政名称；不从现代国家政体全称生成历史殖民地名。'})
    print('Corrected colonial label records',len(records),flush=True)
if __name__=='__main__':main()
