import imperialAffiliations from './imperial-affiliations.json';
import {reviewedCapitals} from './capitals.mjs';
import capitalIndex from '../public/data/map-capitals.json';
import {useState,useMemo} from 'react';
import {zhText} from './translate';
import chineseBriefs from './localization/archive-summaries.zh.json';
import historicalPopulation from '../public/data/historical-population.json';
import chronologyWarnings from '../public/data/chronology-warning-index.json';
import archiveExceptions from '../public/data/modern-archive-exceptions.json';
import {ExternalLink,Flag,Landmark,MapPin,Shield,Swords,Users,HeartHandshake,ScrollText,Info} from 'lucide-react';
import type {FeatureCollection} from 'geojson';
import {groupedAlliances,dependenciesAt,relationMembers} from './relationships.mjs';
import {RulerPortrait,usePortraits} from './portraits';
import Officeholders from './Officeholders';
import {warTitle} from './WarPanel';
import {warInvolvesPolity} from './historical-wars.mjs';
import type {AtlasFeature} from './MapView';
import {localName,nameTranslationStatus} from './data';
import {formatYear} from './history.mjs';
import {useStatistics,useNationalStrength,dollars,StatisticsChart} from './statistics';
import {cowPolityName,leadershipFor} from './archive-rules.mjs';
import {applies,cowCode,curatedData,identityFor,scopedFacts,selectFlag,useArchive} from './archive';
const compact=(n:number)=>n>=1e8?`${(n/1e8).toFixed(2)} 亿`:n>=1e4?`${(n/1e4).toFixed(1)} 万`:Math.round(n).toLocaleString('zh-CN');
const names:Record<string,string>={government:'政体',capital:'首都',ruler:'统治者／国家元首',headOfGovernment:'政府首脑',religion:'宗教／国家礼制',ideology:'意识形态／政治思想',language:'语言',ethnicity:'族群资料'};
const types:Record<string,string>={alliance:'结盟与条约',royalMarriage:'王室联姻',personalUnion:'共主关系',war:'战争'};
const terms:Record<string,string>={defense:'共同防御',neutrality:'中立承诺',nonaggression:'互不侵犯',entente:'协商协约'};

export function CountryFlag({name,qid,year,feature}:{name:string;qid?:string;year:number;feature?:AtlasFeature}){
 const archive=useArchive(),portraits=usePortraits(),id=identityFor(name,qid),custom=curatedData.polities[id];
 if(['archaeological-culture','human-presence'].includes(feature?.properties.representationKind))return <div className="flag-unavailable"><ScrollText size={25} strokeWidth={1.2}/><div><strong>{feature?.properties.representationKind==='human-presence'?'古人类分布不适用国家旗帜':'考古文化不适用统一国家旗帜'}</strong><small>分布范围表示遗址与人群活动联系，不等同一个国家或王朝</small></div></div>;
 let selected=selectFlag(archive?.flags.entities[id]||[],year),role='';
 const special=(archiveExceptions as Record<string,any>)[name],exception=special&&special.from<=year&&year<=special.to?special:null;
 if(exception?.flagOwner){selected=selectFlag(archive?.flags.entities[exception.flagOwner]||[],year);role=exception.flagRole;}
 if(!selected.flag){
  const rulers=(custom?.rulers||[]).filter((r:any[])=>r[0]<=year&&year<=r[1]).map((r:any[])=>portraits?.manualRulers[id+'|'+r[2]]).filter(Boolean);
  const dated=scopedFacts(archive?.facts.entities[id],'ruler',year).rows.map(r=>String(r.value));
  for(const person of [...rulers,...dated]){const flag=selectFlag(archive?.flags.entities[person]||[],year);if(flag.flag){selected=flag;role='统治者王旗／代表旗';break;}}
 }
 if(!selected.flag&&name==='Estado Novo'&&feature?.properties.sourceQid&&feature.properties.sourceQid!==id){const flag=selectFlag(archive?.flags.entities[feature.properties.sourceQid]||[],year);if(flag.flag){selected=flag;role='同一国家的代表旗';}}
 if(!selected.flag&&feature?.properties.sovereignQid){const flag=selectFlag(archive?.flags.entities[feature.properties.sovereignQid]||[],year);if(flag.flag){selected=flag;role=['administration','federation','member'].includes(feature.properties.territoryType)?'管理方／所属政权代表旗':'宗主国代表旗';}}
 if(selected.flag){
  if(feature?.properties.sovereignName&&!role)role=feature.properties.sovereignQid===id?(feature.properties.jointRulers?'共管方代表旗':'主权方代表旗'):'领地旗';
  const type=role||selected.flag.role||(/Royal|Standard|Banner/i.test(selected.flag.file)?'王旗／统治者旗':/Army|Military|Naval|War flag|Vexillum/i.test(selected.flag.file)?'军旗／军用代表旗':'国旗／代表旗');
  return <figure className={'country-flag'+(id==='Q12536'&&selected.flag.file==='Black flag.svg'?' historical-black-banner':type==='波旁复辟白旗'?' historical-white-banner':'')}><img src={selected.flag.path} alt={`${localName(name)}的${type}`}/><figcaption><span title={selected.flag.periodNote}>{type}{selected.reference?' · 年代未细分':''}</span><a href={selected.flag.commons} target="_blank" rel="noreferrer" title={`图像许可：${selected.flag.license}`}><ExternalLink size={11}/></a></figcaption>{selected.flag.periodNote&&<p className="flag-period-note">{selected.flag.periodNote}{selected.flag.periodSource&&<a href={selected.flag.periodSource} target="_blank" rel="noreferrer" aria-label="旗帜年代依据"> 年代依据 ↗</a>}</p>}</figure>;
 }
 if(id==='local:buyid-state')return <div className="flag-unavailable"><Flag size={25}/><div><strong>布韦希旗帜形制待核定</strong><small>各支系有不同旗帜记录。<a href="https://www.iranicaonline.org/articles/flags-i/" target="_blank" rel="noreferrer">查看旗帜史料 ↗</a></small>{year>=1012&&year<=1024&&<small><a href="https://www.fint-ikmk.uni-tuebingen.de/ikmk/object?id=ID74&amp;lang=en" target="_blank" rel="noreferrer">苏丹·道莱时期银币 · 图宾根大学藏 ↗</a></small>}</div></div>;
 if(exception?.noUnifiedFlag)return <div className="flag-unavailable"><Flag size={25} strokeWidth={1.2}/><div><strong>此记录不适用统一国家旗帜</strong><small>{exception.flagNote}</small></div></div>;
 return <div className="flag-unavailable"><Flag size={25} strokeWidth={1.2}/><div><strong>{archive?'代表旗帜资料待补':'正在读取旗帜资料…'}</strong><small>可采用有出处的王旗、军旗；未使用虚构“古代国旗”</small></div></div>;
}

export function OccupationOfficeholders({qid,year}:{qid?:string;year:number}){
 const data=useArchive();
 const entity=qid?data?.facts.entities[qid]:undefined;
 const rows=scopedFacts(entity,'ruler',year).rows;
 if(!rows.length)return null;
 return <div className="ruler-card"><div className="section-label"><span/>当地政权领导人</div><Officeholders rows={rows} year={year}/></div>;
}

export default function CountryArchive({name,feature,area,year,onFly,world,currentWars,onWar,polityLink}:{polityLink:(name:string,label?:string)=>React.ReactNode;name:string;feature:AtlasFeature;area:number;year:number;world:FeatureCollection|null;onFly:()=>void;currentWars?:any[];onWar?:(id:string)=>void}){
 const data=useArchive(),id=identityFor(name,feature.properties.qid),entity=data?.facts.entities[id],custom=curatedData.polities[id];
 const special=(archiveExceptions as Record<string,any>)[name],exception=special&&special.from<=year&&year<=special.to?special:null;
 const chronologyWarning=(chronologyWarnings as Record<string,{before:number|null;after:number|null;reasons:string[]}>)[name+'|'+id];
 const needsChronologyReview=chronologyWarning&&((chronologyWarning.before!=null&&year<chronologyWarning.before-1)||(chronologyWarning.after!=null&&year>chronologyWarning.after+1));
 const portraits=usePortraits();
 const [tab,setTab]=useState<'overview'|'society'|'diplomacy'|'sources'>('overview'),[expanded,setExpanded]=useState(false);
 const {economy,observation}=useStatistics(name,year);
 const archaeological=['archaeological-culture','human-presence'].includes(feature.properties.representationKind);
 const source=custom?.source||feature.properties.contextSource||feature.properties.sourceUrl||`https://www.wikidata.org/wiki/${id}`;
 const brief=(chineseBriefs as Record<string,{text:string;method:string}>)[id];
 const rulerRows=(custom?.rulers||[]).filter((row:any[])=>row[0]<=year&&year<=row[1]);
 const superiorId=feature.properties.controlArea?feature.properties.controllerQid:feature.properties.sovereignQid;
 const superior=superiorId?data?.facts.entities[superiorId]:undefined;
 const leadership=leadershipFor(exception?.leadershipCountry?data?.facts.entities[exception.leadershipCountry]:entity,superior,year);
 const heads=leadership.rows,governmentHeads=leadership.governmentRows;
 const imperialHeads=scopedFacts(entity,'imperialSovereign',year).rows;
 const headIds=new Set([...heads.map(r=>String(r.value)),...rulerRows.map((r:any[])=>portraits?.manualRulers[id+'|'+r[2]]).filter(Boolean)]);
 const separateGovernmentHeads=governmentHeads.filter(r=>!headIds.has(String(r.value)));
 const known=(field:string)=>{
  const manual=(custom?.facts||[]).filter((row:any)=>row.field===field&&applies(row,year));
  if(manual.length)return {text:manual.map((row:any)=>row.value).join('；'),reference:false};
  const fromWiki=scopedFacts(entity,field,year);
  return {text:[...new Set(fromWiki.rows.map(row=>zhText(row.label)))].join('；'),reference:fromWiki.reference};
 };
 const field=(key:string)=>{const capitals=key==='capital'?reviewedCapitals(capitalIndex,id,year,name):[];const fact=capitals.length?{text:capitals.map(row=>row[0]).join('、'),reference:false}:known(key),cultureNames:Record<string,string>={government:'社会与政治组织',religion:'信仰与仪式证据',ideology:'解释边界',conflictEvidence:'冲突与防御证据'};return <div key={key}><dt>{archaeological?cultureNames[key]||names[key]:names[key]}</dt><dd className={fact.text?'':'muted'}>{fact.text||'该年资料尚未核定'}{capitals.length>0&&<small className="reference-tag"><a href={capitals[0][6]} target="_blank" rel="noreferrer">首都资料来源 ↗</a></small>}{fact.text&&fact.reference&&<small className="reference-tag">条目时期参考 · 未细分年度</small>}</dd></div>;};
 const curatedRelations=(curatedData.relations as any[]).filter(r=>relationMembers(r).includes(name)&&applies(r,year));
 const code=data&&!feature.properties.sovereignName?cowCode(name,entity,data.diplomacy.countries,year):undefined;
 const census=(historicalPopulation as Record<string,Record<string,{population:number;source:string;label:string;scope:string}>>)[name]?.[year];
 const historicalNational=useNationalStrength(code,year,name),population=census?.population||observation?.population||historicalNational?.population,military=observation?.military||historicalNational?.military;
 const alliances=useMemo(()=>code&&year>=1816&&year<=2012?groupedAlliances(data?.diplomacy.alliances||[],code,year):[],[code,data,year]);
 const rawWarParticipations=code&&year>=1816&&year<=2007?(data?.diplomacy.wars||[]).filter(r=>r.code===code&&applies(r,year)):[];
 const relationships=useMemo(()=>dependenciesAt(world,data?.relations||[],year,curatedData.relations),[world,data,year]);
 const equivalent=(a:string,b:string)=>a===b||localName(a)===localName(b);
 const superiors=relationships.filter(r=>!['union','jointRule'].includes(r.kind)&&equivalent(r.child,name));
 const subjects=relationships.filter(r=>!['union','jointRule'].includes(r.kind)&&equivalent(r.parent,name));
 const unions=relationships.filter(r=>['union','jointRule'].includes(r.kind)&&(equivalent(r.child,name)||equivalent(r.parent,name)));
 const linkedWars=(currentWars||[]).filter(w=>warInvolvesPolity(w,name,year,code));
 const linkedIds=new Set(linkedWars.flatMap(w=>[w.id,...(w.also||[]).map((x:any)=>x.id)]));
 const warParticipations=rawWarParticipations.filter(r=>!linkedIds.has('cow-inter-'+r.warId));
 const counts={alliance:alliances.length+curatedRelations.filter(r=>r.kind==='alliance').length,war:warParticipations.length+curatedRelations.filter(r=>r.kind==='war'&&!linkedWars.some(w=>(w.detail?.title||w.name)===r.title)).length+linkedWars.length,royalMarriage:curatedRelations.filter(r=>r.kind==='royalMarriage').length+unions.length};
 const imperialContext=id==='Q12548'?(row:{value:string|number})=>{
  const context=imperialAffiliations[String(row.value) as keyof typeof imperialAffiliations];
  if(!context)return null;
  const titles=context.titles.filter(title=>title.from<=year&&year<=title.to);
  return <div className="imperial-affiliation"><small>所属家族 · {context.house} <a href={context.source} target="_blank" rel="noreferrer" aria-label="家族来源">↗</a></small>
   {titles.map(title=><small key={title.polity}>同年兼领 · {polityLink(title.polity,title.label)}（{title.role}） <a href={title.source} target="_blank" rel="noreferrer" aria-label="兼领来源">↗</a></small>)}
  </div>;
 }:undefined;
 const linkedNames=(members:string[])=>[...new Set(members)].map((member,i)=><span key={member}>{i>0?'、':''}{polityLink(member)}</span>);
 const renderCurated=(kind:string)=>curatedRelations.filter(r=>r.kind===kind&&(kind!=='war'||!linkedWars.some(w=>warTitle(w,year)===r.title))).map(r=><article className={'relationship-card '+kind} key={r.id}><div className="relationship-title"><strong>{r.title}</strong><a href={r.source} target="_blank" rel="noreferrer" aria-label="关系资料来源"><ExternalLink size={12}/></a></div><span>{r.from}—{r.to}{r.from===year||r.to===year?' · 年内可能变更':''}</span><p>{r.detail}</p><small>{linkedNames(relationMembers(r).filter(member=>!equivalent(member,name)))}</small></article>);
 return <div className="country-archive">{feature.properties.coastalReference&&<p className="micro-note">{feature.properties.boundaryGeometry?'本年份的版图采用统一的现代地理边界参考。':(feature.properties.worldCoastalGeometry||feature.properties.historicalCoastGeometry)?'近岸缺口按同期政权轮廓和海岸底图概化补绘。':feature.properties.historicalIslandGeometry?'部分岛屿依据本年代的政权轮廓与海岸底图补绘，归属范围为概化。':'本年份的近岸轮廓按地理底图校准。'} <a className="source-link" href={feature.properties.coastalReference} target="_blank" rel="noreferrer">海岸线参考 ↗</a></p>}{feature.properties.representationNote&&<div className="data-note"><strong>{archaeological?'考古文化分布记录':'地域与控制范围说明'}</strong><p>{feature.properties.representationNote}</p></div>}
  <div className="archive-tabs">{([['overview','概览',Landmark],['society','社会',Users],['diplomacy','外交',Shield],['sources','资料',ScrollText]]as const).map(([value,label,Icon])=><button key={value} className={tab===value?'active':''} onClick={()=>setTab(value)}><Icon size={12}/>{label}{value==='diplomacy'&&counts.war>0&&<i/>}</button>)}</div>
  {exception?.leadershipCountry&&<div className="data-note">{exception.leadershipNote}</div>}
  {leadership.fromSovereign&&<div className="data-note">下列为{polityLink((feature.properties.controlArea?feature.properties.controller:feature.properties.sovereignName)||'管理方')}当年的中央元首与政府首脑；不是当地总督或地方政府名单，也不表示领土主权已经转移。</div>}
  {needsChronologyReview&&<div className="data-note"><strong>年代关联待复核</strong><p>此年源记录与关联实体的存续年代存在差异，可能涉及前身、后继或名称沿用。此处疆界与档案尚不能视为已经核定。</p><a className="source-link" href="/audit.html" target="_blank" rel="noreferrer">查看全球核查线索 <ExternalLink size={11}/></a></div>}
  {feature.properties.temporalResolution&&<div className="data-note"><strong>{archaeological?'分期考古资料 · 分布概览':'按有效时期细分 · 概化重建'}</strong><p>{feature.properties.yearConvention}</p><p>{feature.properties.accuracy}</p><a className="source-link" href={feature.properties.contextSource||feature.properties.sourceUrl||feature.properties.regionalControlSource} target="_blank" rel="noreferrer">年代与分布依据 <ExternalLink size={11}/></a></div>}
  {feature.properties.regionalControlNote&&<div className="data-note"><p>{feature.properties.regionalControlNote}</p><a className="source-link" href={feature.properties.regionalControlSource} target="_blank" rel="noreferrer">地区控制资料 <ExternalLink size={11}/></a></div>}
  {tab==='sources'&&<>{feature.properties.boundarySource&&<><a className="source-link" href={feature.properties.boundarySource} target="_blank" rel="noreferrer">历史分区与重建边界来源 <ExternalLink size={12}/></a><p className="micro-note">{feature.properties.credit} · {feature.properties.license}</p></>}<a className="source-link" href="/coverage-review.html" target="_blank" rel="noreferrer">印度、高加索、阿拉伯与早期文化核查 <ExternalLink size={12}/></a>{year>=1945&&year<=1955&&<a className="source-link" href={'/postwar-archive.html?year='+year} target="_blank" rel="noreferrer">1945—1955年元首与管理关系核查 <ExternalLink size={12}/></a>}<a className="source-link" href="/modern-archive.html" target="_blank" rel="noreferrer">现代国旗、元首与政府首脑核查 <ExternalLink size={12}/></a><a className="source-link" href="/audit.html" target="_blank" rel="noreferrer">全球时序核查：已修正与待复核清单 <ExternalLink size={12}/></a>{feature.properties.identityCorrection&&<div className="data-note">实体已核对：{feature.properties.identityCorrection}。原始关联保留为 {feature.properties.sourceQid}。</div>}{feature.properties.geometryMethod&&<p className="micro-note">轮廓方法：{feature.properties.geometryMethod}</p>}</>}
  {tab==='overview'&&<>
   <div className="ruler-card"><div className="section-label"><span/>{archaeological?'人物与政治组织记载':leadership.fromSovereign?'上层政权／管理方中央元首':exception?.leadershipCountry?'控制方中央领导人':'国家元首／统治者'}</div>{rulerRows.length?rulerRows.map((row:any[],i:number)=><div className="ruler-row" key={i}><RulerPortrait qid={portraits?.manualRulers[id+'|'+row[2]]} name={row[2]}/><div><strong>{row[2]}</strong><span>{formatYear(row[0])}—{formatYear(row[1])}</span></div></div>):heads.length?<><Officeholders rows={heads} year={year} renderContext={imperialContext}/>{entity?.rulerScopeNote&&<p className="micro-note">{entity.rulerScopeNote}</p>}</>:<p className="micro-note">{archaeological?'人群活动与考古分布不对应一个统一国家，不据此设定一位共同统治者。':exception?.leadershipNote||'该年元首资料尚待补全；战时多方控制或非国家分组不一定适用单一元首。'}</p>}{rulerRows.length>1&&<p className="year-change">年度视图包含交接或共治，以上记录不表示全部同时任职。</p>}{rulerRows.length>0&&<a className="source-link" href={custom.rulersSource} target="_blank" rel="noreferrer">任期资料来源 <ExternalLink size={11}/></a>}{governmentHeads.length>0&&!separateGovernmentHeads.length&&<p className="micro-note">{governmentHeads.some(r=>r.derived)?'据对应职务资料补全：国家元首同时承担政府首脑角色。':'国家元首同时兼任政府首脑。'}</p>}</div>
   {separateGovernmentHeads.length>0&&<div className="ruler-card"><div className="section-label"><span/>政府首脑</div><Officeholders rows={separateGovernmentHeads} year={year}/></div>}
   {imperialHeads.length>0&&<div className="ruler-card"><div className="section-label"><span/>{id==='local:buyid-state'?'巴格达阿拔斯哈里发':'朝廷天皇 · 与幕府执政分列'}</div><Officeholders rows={imperialHeads} year={year}/><p className="micro-note">{id==='local:buyid-state'?'哈里发与各支系埃米尔的职权分列。':'皇位与幕府将军、执权是不同职务；南北朝时期可有并立的皇位主张。'}</p></div>}
   <p className="detail-description">{feature.properties.jointRulers?<>{feature.properties.displayName||localName(name)}。联合管理方为{linkedNames(feature.properties.jointRulers)}。</>:feature.properties.sovereignName?<>{feature.properties.displayName||localName(name)}。上层政权／管理方为{polityLink(feature.properties.sovereignName)}。中央任期资料不代替当地总督档案。</>:custom?.summary||brief?.text||zhText(entity?.description)||`${localName(name)}的疆界来自有有效时期的历史 GIS。下列资料区分适用年份与未定年条目参考。`}</p>
   <div className="stat-grid"><div><span><MapPin size={13}/>{archaeological?'分布示意面积':'地图计算面积'}</span><strong>{compact(area)}</strong><small>km² · 概化多边形估算</small></div><div><span><Users size={13}/>人口</span><strong className={population?'':'missing'}>{population?compact(population):'待核定'}</strong><small>{census?<a href={census.source} target="_blank" rel="noreferrer" title={census.scope}>{year} 年 · {census.label} ↗</a>:population?`${observation?.population?year:historicalNational.observationYear} 年${historicalNational?.reference&&!observation?.population?'参考':''} · ${observation?.population?'世界银行':'COW 年度序列（含来源估计）'}`:'未把其他年份人口套用到此年'}</small></div></div>
   {historicalNational?.reference&&<p className="micro-note">{historicalNational.scopeNote}</p>}<dl className="fact-list">{(archaeological?['government','religion','conflictEvidence','ideology']:['government','capital','religion','ideology']).map(field)}</dl>
   <div className="diplomacy-summary"><button onClick={()=>setTab('diplomacy')}><Shield size={15}/><strong>{counts.alliance}</strong><span>已收录条约</span></button><button onClick={()=>setTab('diplomacy')}><HeartHandshake size={15}/><strong>{counts.royalMarriage}</strong><span>王室纽带</span></button><button onClick={()=>setTab('diplomacy')}><Swords size={15}/><strong>{counts.war}</strong><span>战争记录</span></button></div><p className="micro-note">计数仅表示已收录的有效记录；0 条不等于已证实没有此类关系。</p>
   <button className="wide-action" onClick={onFly}><MapPin size={14}/>前往这一势力</button>
  </>}
  {tab==='society'&&<><div className="section-label"><span/>社会、宗教与政治思想</div><dl className="fact-list">{['religion','ideology','language','ethnicity','headOfGovernment'].map(field)}<div><dt>GDP</dt><dd>{observation?.gdp?`${dollars(observation.gdp)} · ${year} 年`:'该年资料尚未核定'}</dd></div>{observation?.gdp&&observation.population&&<div><dt>人均 GDP</dt><dd>{dollars(observation.gdp/observation.population)}</dd></div>}<div><dt>军队人数</dt><dd>{military?`${compact(military)} 人 · ${observation?.military?year:historicalNational?.observationYear} 年${historicalNational?.reference?'参考':''} · ${observation?.military?'世界银行':'COW NMC 年度序列，含来源估计'}`:'该年资料尚未核定'}</dd></div></dl>{economy&&<StatisticsChart economy={economy} year={year}/>}<div className="data-note">族群、宗教与历史政体不等同现代民族国家分类。未定年条目仅作该政权的背景参考，不视作所选年份的精确结论。</div></>}
  {tab==='diplomacy'&&<>
   <div className="archive-coverage"><Info size={14}/><p>按所选年份筛选条约、王室纽带和参战记录。近现代结盟数据库覆盖 1816—2012 年、国家间战争数据库覆盖 1816—2007 年；更早时期由单独有来源的记录补充。</p></div>
   <div className="section-label"><span/>结盟、互不侵犯与中立条约</div>{renderCurated('alliance')}{(expanded?alliances:alliances.slice(0,10)).map(group=><article className="relationship-card alliance" key={group.peer}><div className="relationship-title"><strong>{polityLink(cowPolityName(group.peer,group.peerName,year))}</strong><a href={group.commitments[0].url} target="_blank" rel="noreferrer"><ExternalLink size={12}/></a></div>{group.commitments.map((r:any,i:number)=><div className="treaty-commitment" key={i}><p>{r.terms.map((term:string)=>terms[term]).join('、')}</p><span>{r.from}—{r.to}{r.rightCensored?' · 截至数据库末年':''}</span><small>{r.outgoing&&r.incoming?'双方相互承诺':r.outgoing?'本国向对方承担承诺':'对方向本国承担承诺'}</small></div>)}</article>)}{alliances.length>10&&!expanded&&<button className="wide-action" onClick={()=>setExpanded(true)}>展开其余 {alliances.length-10} 条记录</button>}{counts.alliance===0&&<p className="micro-note">当前收录范围内未检出条约；不据此判定该国没有盟友。</p>}
   {curatedRelations.some(r=>r.kind==='historicalDivision')&&<><div className="section-label"><span/>历史分立与王朝渊源</div>{renderCurated('historicalDivision')}</>}
   <div className="section-label"><span/>王室联姻</div>{renderCurated('royalMarriage')}{!curatedRelations.some(r=>r.kind==='royalMarriage')&&<p className="micro-note">尚无已核定适用于这一年的王室联姻记录。不是“无联姻”的结论。</p>}
   <div className="section-label"><span/>战争与参战状态</div>{renderCurated('war')}{linkedWars.map(w=><article className="relationship-card war" key={w.id}><div className="relationship-title"><strong>{warTitle(w,year)}</strong></div><span>{w.from}—{w.to} · 本年存在相关参战记录</span><p>{w.detail?.cause}</p><button className="wide-action" onClick={()=>onWar?.(w.id)}>查看交战双方、战役与结果 <ExternalLink size={12}/></button></article>)}{warParticipations.map(r=>{const opponents=(data?.diplomacy.wars||[]).filter(other=>other.warId===r.warId&&other.side!==r.side&&applies(other,year));return <article className="relationship-card war" key={r.id}><div className="relationship-title"><strong>{localName(r.name)}</strong><a href={r.url} target="_blank" rel="noreferrer"><ExternalLink size={12}/></a></div><span>本国参战：{r.from}—{r.to}</span><p>对方阵营：{opponents.length?linkedNames(opponents.map(other=>cowPolityName(other.code,other.country,year))):'该年对方记录未完整关联'}</p><small>同一战争同侧参战不等于彼此交战；本条不自动生成占领区。</small></article>;})}{counts.war===0&&<p className="micro-note">尚无适用的战争记录，不据此宣告和平状态。</p>}
   <div className="section-label"><span/>宗主国与上层关系</div>{superiors.map((r,i)=><article className="relationship-card dependency" key={i}><strong>{polityLink(r.parent)}</strong><span>{r.kind==='overseas'?'主权所属／海外领地关系':r.kind==='colony'?'宗主国／殖民统治':r.kind==='protectorate'?'保护国／保护条约关系':r.kind==='administration'?'管理方／过渡行政关系':r.kind==='federation'?'联邦上层政权':r.kind==='vassal'?'宗主国／封臣关系':r.kind==='allegiance'?'名义效忠对象':'复合政权／联盟'}</span><p>{r.detail}</p><small>{r.from}—{r.to} · {r.source}</small></article>)}{superiors.length===0&&<p className="micro-note">未收录适用于此年的上层隶属关系。</p>}
   <div className="section-label"><span/>附属国、殖民地与成员</div>{subjects.map((r,i)=><article className="relationship-card dependency" key={i}><strong>{polityLink(r.child)}</strong><span>{r.kind==='overseas'?'海外领地／属地':r.kind==='colony'?'殖民地／属地':r.kind==='protectorate'?'保护国／受保护关系':r.kind==='administration'?'管理地区／过渡行政':r.kind==='federation'?'联邦组成地区':r.kind==='vassal'?'附属国／封臣':r.kind==='allegiance'?'名义效忠／朝贡':'复合政权成员'}</span><small>{r.from}—{r.to} · {r.source}</small></article>)}{subjects.length===0&&<p className="micro-note">当前收录范围未检出；不据此认定没有附属国。</p>}
   <div className="section-label"><span/>政治联合、共主与联合统治</div>{curatedRelations.filter(r=>r.kind==='politicalUnion').map(r=><article className="relationship-card personalUnion" key={r.id}><strong>{r.title}</strong><p>{r.detail}</p><small>{linkedNames(relationMembers(r).filter(member=>!equivalent(member,name)))}</small><small>{r.from}—{r.to}</small><a className="source-link" href={r.source} target="_blank" rel="noreferrer">联合条约与说明 ↗</a></article>)}{unions.map((r,i)=><article className="relationship-card personalUnion" key={i}><strong>{polityLink(equivalent(r.child,name)?r.parent:r.child)}</strong>{r.title&&<span>{r.title}</span>}<p>{r.detail}</p><small>{r.from}—{r.to}</small><a className="source-link" href={r.source.startsWith('https://')?r.source:undefined} target="_blank" rel="noreferrer">关系资料来源 ↗</a></article>)}{unions.length===0&&<p className="micro-note">当前收录范围未检出适用于此年的实际共主关系。</p>}
  </>}
  {tab==='sources'&&<>{feature.properties.boundarySource&&<><a className="source-link" href={feature.properties.boundarySource} target="_blank" rel="noreferrer">历史分区与重建边界来源 <ExternalLink size={12}/></a><p className="micro-note">{feature.properties.credit} · {feature.properties.license}</p></>}{entity?.description&&<details className="archive-original"><summary>原始简介与中文整理说明</summary>{brief&&<p>{brief.method}</p>}<p lang="en">{entity.description}</p></details>}<div className="section-label"><span/>资料范围与出处</div><dl className="fact-list"><div><dt>疆界来源</dt><dd>{feature.properties.source||'Cliopatria／Seshat'}</dd></div><div><dt>本图形有效期</dt><dd>{feature.properties.validFrom}—{feature.properties.validTo}</dd></div><div><dt>实体编号</dt><dd>{id||'尚未关联'}</dd></div><div><dt>中文译名</dt><dd>{nameTranslationStatus(name)}</dd></div></dl><a className="source-link" href="https://github.com/Seshat-Global-History-Databank/cliopatria" target="_blank" rel="noreferrer">疆界数据与方法 <ExternalLink size={12}/></a>{id.startsWith('Q')&&<a className="source-link" href={`https://www.wikidata.org/wiki/${id}`} target="_blank" rel="noreferrer">结构化条目与逐字段来源 <ExternalLink size={12}/></a>}{custom&&<a className="source-link" href={source} target="_blank" rel="noreferrer">人工补充档案来源 <ExternalLink size={12}/></a>}{custom?.flagPolicy&&<div className="data-note">{custom.flagPolicy}<a className="source-link" href={custom.flagPolicySource} target="_blank" rel="noreferrer">旗帜核对依据 <ExternalLink size={11}/></a></div>}<a className="source-link" href="/data/data-audit.json" target="_blank" rel="noreferrer">全量检查报告与已知问题 <ExternalLink size={12}/></a><div className="data-note">完成结构、日期、实体匹配与明显错误检查，不等于所有边界和每个字段都已由史学专家逐条审定。</div></>}
 </div>;
}
