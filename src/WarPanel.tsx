import {useEffect,useMemo,useState} from 'react';
import {ArrowLeft,ArrowRight,ExternalLink,MapPin,Search,Shield,Swords,Users} from 'lucide-react';
import {localName} from './data';
import {zhText} from './translate';
import {cowPolityName} from './archive-rules.mjs';
import {formatYear} from './history.mjs';
import {inferredCause,interpolateStrength,outcomeNames,participantsAt,warsAtYear} from './conflicts.mjs';
type Data={database:any;details:any;statistics:any;military:any};
let pending:Promise<Data>|undefined;
export function useConflicts(){
 const [data,setData]=useState<Data|null>(null),[error,setError]=useState(false);
 useEffect(()=>{let live=true;pending??=Promise.all(['/data/conflicts.json','/data/war-details.json','/data/statistics.json','/data/national-strength.json'].map(url=>fetch(url,{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error(url);return r.json();}))).then(([database,details,statistics,military])=>({database,details,statistics,military}));pending.then(d=>{if(live)setData(d);}).catch(()=>{pending=undefined;if(live)setError(true);});return()=>{live=false;};},[]);
 return {data,error};
}
const aliases:Record<string,string>={'National Liberation Front of South Vietnam':'越南南方民族解放阵线（越共武装）','North Vietnam':'北越','South Vietnam':'南越','Russia (Soviet Union)':'Russia','Vietnam (North Vietnam)':'North Vietnam','Myanmar (Burma)':'Myanmar','Cambodia (Kampuchea)':'Cambodia','Yemen (North Yemen)':'Yemen','DR Congo (Zaire)':'Democratic Republic of the Congo','Serbia (Yugoslavia)':'Serbia','Ivory Coast':'Ivory Coast','Madagascar (Malagasy)':'Madagascar','Zimbabwe (Rhodesia)':'Zimbabwe','North Macedonia':'North Macedonia','FLN':'民族解放阵线（阿尔及利亚）','IS':'“伊斯兰国”组织','AQIM':'伊斯兰马格里布基地组织','Taleban':'塔利班','Hamas':'哈马斯','Hezbollah':'真主党','Fatah':'法塔赫','UNLF':'乌干达民族解放阵线','USSR':'苏联'};
export function actorName(value:string,year:number,code?:string){
 const government=value.startsWith('Government of ');let raw=value.replace(/^Government of /,'').trim();
 if(raw==='Russia (Soviet Union)')raw=year<=1991?'Soviet Union':'Russia';
 else if(raw==='Vietnam (North Vietnam)')raw=year<=1975?'North Vietnam':'Vietnam';
 else if(raw==='China'&&year<1949)raw='Republic of China';
 else if(raw==='Serbia (Yugoslavia)')raw=year<=1991?'Yugoslavia':year<=2002?'Federal Republic of Yugoslavia':year<=2005?'Serbia and Montenegro':'Serbia';
 raw=aliases[raw]||raw;
 const result=localName(code?cowPolityName(code,raw,year):raw),translated=zhText(result);
 return translated+(government?'政府':'');
}
export function warTitle(war:any,year:number){
 if(war.detail?.title)return war.detail.title;
 if(war.location){const region=war.location.split(', ').map((n:string)=>actorName(n,year)).join('、');const a=war.annual?.[year];return `${region} · ${a?.issue===1?'领土与自治冲突':a?.issue===2?'政权冲突':'武装冲突'}`;}
 const title=zhText(localName(war.name));
 if(/[\u3400-\u9fff]/.test(title))return title;
 const first=participantsAt(war,year)[0];
 return `${first?actorName(first.name,year,first.code):'历史势力'} · ${war.category}（${war.from}年起）`;
}
const number=(value:number)=>value>=10000?`${(value/10000).toLocaleString('zh-CN',{maximumFractionDigits:1})} 万`:value.toLocaleString('zh-CN');
const outcome=(value:number)=>({1:'胜方',2:'败方',3:'妥协／平局',4:'战争类型转变',5:'记录截止时仍持续',6:'僵持',7:'降至战争门槛以下',8:'转变阵营'}[value]||'尚未编码');
function nationalStrength(data:Data,name:string,year:number,code?:string){
 const raw=name.replace(/^Government of /,'').trim();
 const normalized=(v:string)=>v.toLowerCase().replace(/[^a-z]/g,'');
 const nmcAliases:Record<string,string>={'Russia (Soviet Union)':'Russia','Soviet Union':'Russia','USSR':'Russia','Vietnam (North Vietnam)':'Vietnam','North Vietnam':'Vietnam','United States':'United States of America','Myanmar (Burma)':'Myanmar','Serbia (Yugoslavia)':'Yugoslavia','Yemen (North Yemen)':'Yemen','Cambodia (Kampuchea)':'Cambodia'};
 const nmc=code?data.military.countries[code]:Object.values(data.military.countries).find((e:any)=>normalized(e.name)===normalized(nmcAliases[raw]||aliases[raw]||raw)) as any;
 if(!(raw==='France'&&year>=1940&&year<=1944)&&nmc){const observation=interpolateStrength(nmc.observations,year);if(observation)return {...observation,source:'COW NMC 年度序列'};}
 // Modern Russia/Serbia/Germany/China are not numerical substitutes for USSR,
 // Yugoslavia, divided Germany, or other earlier territorial entities.
 if((/Russia|Soviet|USSR/.test(raw)&&year<=1991)||(/Serbia|Yugoslavia/.test(raw)&&year<=2006)||(/Germany|German/.test(raw)&&year<1991)||(/China/.test(raw)&&year<1971))return null;
 const match=Object.values(data.statistics).find((e:any)=>e.name===(aliases[raw]||raw)) as any;
 const observation=match?interpolateStrength(match.observations,year):null;return observation?{...observation,source:'世界银行'}:null;
}
export function WarPanel({data,error,year,onFly,initialId,polityLink}:{polityLink:(name:string,label?:string)=>React.ReactNode;initialId?:string|null;data:Data|null;error:boolean;year:number;onFly:(position:[number,number])=>void}){
 const wars=useMemo(()=>warsAtYear(data?.database,data?.details,year),[data,year]);
 const [id,setId]=useState<string|null>(initialId??null),[query,setQuery]=useState(''),[onlyMajor,setOnlyMajor]=useState(false);
 useEffect(()=>{setId(initialId??null);},[initialId]);
 const selected=wars.find(w=>w.id===id);
 const filtered=wars.filter(w=>(!onlyMajor||!w.annual||w.annual[year].intensity===2)&&(!query||(warTitle(w,year)+w.name+participantsAt(w,year).map((p:any)=>(p.displayName||actorName(p.name,year,p.code))).join('')).toLowerCase().includes(query.toLowerCase())));
 if(!data)return <div className="data-note">{error?'战争资料读取失败，请刷新页面重试。':'正在整理战争与参战方资料…'}</div>;
 if(!selected)return <div className="war-panel"><div className="panel-title"><span className="eyebrow">战争与冲突档案</span><h2>烽火中的世界</h2><p>{formatYear(year)} · {wars.length} 项已收录战争与武装冲突</p></div><div className="war-search"><Search size={14}/><input aria-label="搜索当前年份战争" placeholder="搜索战争、国家或势力…" value={query} onChange={e=>setQuery(e.target.value)}/></div><label className="war-filter"><input type="checkbox" checked={onlyMajor} onChange={e=>setOnlyMajor(e.target.checked)}/>仅显示战争级强度</label><div className="war-coverage">按实际活动年度筛选；低强度冲突与战争分开标记。{year>2025?'2026 年尚未接入年度核定数据，列表为空不代表和平。':year<1816?'此年代为重点战争补充，尚非穷尽。':'COW 1816—2014 · UCDP 1946—2025'}</div>{filtered.map(w=><button className="war-list-card" key={w.id} onClick={()=>setId(w.id)}><span className={'war-level '+(w.annual?.[year]?.intensity===1?'low':'')}><Swords size={13}/>{w.annual?.[year]?.intensity===1?'低强度武装冲突':'战争'}</span><strong>{warTitle(w,year)}</strong><small>{participantsAt(w,year).slice(0,4).map((p:any)=>(p.displayName||actorName(p.name,year,p.code))).join(' · ')}{participantsAt(w,year).length>4?' 等':''}</small><span className="war-card-bottom">{w.from}—{w.to} · {w.source}<ArrowRight size={14}/></span></button>)}{!filtered.length&&<div className="empty-state">当前条件没有检出记录。{year<=2025?'未收录不等于没有战争。':''}</div>}</div>;
 const participants=participantsAt(selected,year),annual=selected.annual?.[year];
 const side=(sideId:string)=>participants.filter(p=>p.side===sideId);
 const metric=(p:any)=>{
  if(p.peakTheaterForces)return {value:p.peakTheaterForces,label:'战区峰值兵力',estimated:false,kind:'theater',years:[]};
  const nationalist=p.polityPeriods?.some((r:any)=>r.name==='Republic of China'&&r.from<=year&&year<=r.to);
  const proxy=nationalStrength(data,nationalist&&year>=1949?'Republic of China':p.name,year,nationalist&&year>=1949?'713':p.code);return proxy?{...proxy,label:proxy.estimated?'全国军事人员 · 插值估算':`全国军事人员 · ${proxy.source}`,kind:'national'}:null;
 };
 const sides=['1','2'].map(k=>side(k).map(p=>({p,m:metric(p)})));
 const complete=sides.every(rows=>rows.length&&rows.every(({m})=>m?.kind==='theater'));
 const totals=sides.map(rows=>rows.reduce((sum,{m})=>sum+(m?.value||0),0));
 return <div className="war-panel war-detail"><button className="war-back" onClick={()=>setId(null)}><ArrowLeft size={14}/>返回 {year} 年全部冲突</button><div className="panel-title"><span className="eyebrow">{selected.category}</span><h2>{warTitle(selected,year)}</h2><p>{selected.from}—{selected.to} · {annual?.intensity===1?'低强度武装冲突':'战争级冲突'}</p></div>{selected.detail?.location&&<button className="wide-action" onClick={()=>onFly(selected.detail.location)}><MapPin size={14}/>前往主要战区</button>}<div className="section-label"><span/>本年交战阵营与参战方</div><p className="micro-note">{selected.scopeNote||'列出数据库收录的主要交战方与直接军事介入方。参战日期为年度交集，不表示各国全年均参战；援助国不自动算作参战国。'}</p><div className="war-sides">{sides.map((rows,index)=><section key={index} className={'war-side side-'+index}><h3><Shield size={14}/>{selected.detail?.sideNames?.[index]||['甲方阵营','乙方阵营'][index]}<b>{rows.length}</b></h3>{rows.length?rows.map(({p,m},i)=><article key={p.name+i}><strong>{p.name==='France'&&p.side==='2'&&year>=1940&&year<=1944?polityLink('Vichy France','法国（维希政府）'):polityLink(p.name,p.displayName||actorName(p.name,year,p.code))}</strong><small>{p.role||'数据库参战方'} · {p.periods.map((a:number[])=>a.join('—')).join('、')}</small>{m?<div className="war-force"><Users size={12}/><span>{number(m.value)} 人<small>{m.label}{m.estimated?'（'+m.years.join('、')+' 年线性插值）':''}</small></span></div>:<small className="muted">兵力暂无可比数值，未用战死人数代填</small>}{p.battleDeaths!=null&&<small>本方全参战期战斗死亡：{number(p.battleDeaths)} 人</small>}{p.outcome&&<small>事后结果编码：{outcome(p.outcome)}</small>}</article>):<p className="micro-note">原始数据未逐项列出本方势力。</p>}</section>)}</div>{complete&&totals[0]>0&&totals[1]>0&&<div className="force-comparison"><strong>各参战方战区峰值的相加对比 · {(totals[0]/totals[1]).toFixed(2)}∶1</strong><div><i style={{width:100*totals[0]/(totals[0]+totals[1])+'%'}}/></div><small>峰值可能出现在不同日期，属于规模参考，不是同日战场实力比。</small></div>}<p className="micro-note">全国军事人员只反映动员基础，不等于投入本场战争的兵力；COW 年度序列本身可能包含来源估计。不同口径不混算比例。插值仅用于同一实体、间隔不超过5年的两条观测之间。</p>{selected.detail?.commanders?.length>0&&<><div className="section-label"><span/>主要统帅</div><p className="detail-description">{selected.detail.commanders.join('；')}</p></>}{selected.detail?.strengthAssessment&&<div className="data-note"><strong>兵力与军队组织</strong><p>{selected.detail.strengthAssessment}</p></div>}{selected.detail?.battles?.length>0&&<><div className="section-label"><span/>主要战役与进程</div>{selected.detail.battles.map((b:any)=><article className="relationship-card war" key={b.name}><strong>{b.name}</strong><span>{b.date}</span><p>{b.result}</p></article>)}</>}<div className="section-label"><span/>战争原因与争议</div><p className="detail-description">{selected.detail?.cause||inferredCause(selected,year)}</p>{!selected.detail?.cause&&<span className="estimate-badge">{annual||selected.category!=='国家间战争'?'分类概括／推断':'资料缺项'}</span>}<div className="section-label"><span/>结果与后续影响 · 事后视角</div><p className="detail-description">{selected.detail?.result||(selected.id.startsWith('cow-inter')?'各参战国的结果编码分别列于上方，不将单一国家的胜负视为整个阵营的结果。':selected.outcomeCode?outcomeNames[selected.outcomeCode]||'尚未核定':annual?.episodeEnded?`本期冲突活动在 ${annual.episodeEndDate||year} 结束；该字段不说明谁获胜，也不代表根本争议解决。`:'本年度数据库没有给出胜负结论；末次收录年份不自动视为战争结束。')}</p>{selected.battleDeaths!=null&&<div className="data-note">全战争期战斗死亡估计：{number(selected.battleDeaths)} 人。此口径不等于全部军民死亡。</div>}<div className="section-label"><span/>活动阶段与资料依据</div><a className="source-link" href={data.military.url} target="_blank" rel="noreferrer">全国兵力参考：COW NMC（1816—2012）<ExternalLink size={12}/></a><p className="micro-note">{selected.periods.map((a:number[])=>a.join('—')).join('；')}。间断年份不会自动填成持续交战。</p><a className="source-link" href={selected.url} target="_blank" rel="noreferrer">{selected.source} 原始档案 <ExternalLink size={12}/></a>{selected.also?.map((w:any)=><a className="source-link" key={w.id} href={w.url} target="_blank" rel="noreferrer">并入：{zhText(localName(w.name))} · {w.source}<ExternalLink size={12}/></a>)}{selected.detail?.sources?.map((url:string)=><a className="source-link" key={url} href={url} target="_blank" rel="noreferrer">历史概述参考 <ExternalLink size={12}/></a>)}</div>;
}

