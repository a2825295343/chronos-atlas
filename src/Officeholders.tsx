import {ExternalLink} from 'lucide-react';
import type {Fact} from './archive';
import {RulerPortrait} from './portraits';
import {formatYear} from './history.mjs';
import {zhText} from './translate';
export default function Officeholders({rows,year,renderContext}:{rows:Fact[];year:number;renderContext?:(row:Fact)=>React.ReactNode}){
 return <>{rows.map((r,i)=>{const needsReview=r.reviewAfter!=null&&year>r.reviewAfter,source=r.citation?.find(s=>/^https?:\/\//.test(s))||(/^Q\d+$/.test(String(r.value))?`https://www.wikidata.org/wiki/${r.value}`:undefined);return <div className="ruler-row" key={String(r.value)+'|'+i}>
  {['collective','vacancy','unrecorded'].includes(r.kind||'')?<div className="ruler-portrait missing-portrait"><span>{r.kind==='unrecorded'?'❧':'♜'}</span><small>{r.kind==='vacancy'?'职位空缺':r.kind==='unrecorded'?'无具名记录':'地方多主体'}</small></div>:<RulerPortrait qid={String(r.value)} name={zhText(r.label)}/>}
  <div><strong>{zhText(r.label)}</strong><span>{r.at!=null?`${formatYear(r.at)} · 来源观测`: `${r.from??'起年待考'}—${r.to??(r.verifiedThrough?`${needsReview?'任期终止待复核':r.rank==='preferred'?'任职中':'末年未记'}（核对至${r.verifiedThrough}年）`:'任期末年未记')}`}</span>
   {r.roleLabel&&<small className="office-role">{r.roleLabel}</small>}
   {renderContext?.(r)}
   {(r.appointments?.length||0)>1&&<details className="office-appointments"><summary>查看同年各项职务与领地任期</summary>{r.appointments?.map((a,j)=><p key={j}><strong>{a.roleLabel||'已收录任期'}</strong><span>{a.from??'起年未记'}—{a.to??'末年未记'}</span>{a.citation?.[0]&&<a className="source-link" href={a.citation[0]} target="_blank" rel="noreferrer">本项任期依据 ↗</a>}</p>)}</details>}
   {needsReview&&<small className="reference-tag" title={r.reviewNote}>任期存在不同记录 · 待复核</small>}
   {r.approximate&&<small className="reference-tag" title={r.inference}>约定纪年 · 存在不同说法</small>}
   {r.derived&&<small className="reference-tag" title={r.inference}>任期据史料补全</small>}
   {source&&<a className="source-link" href={source} target="_blank" rel="noreferrer" title={r.inference||'任期资料与出处'}>任期资料 <ExternalLink size={10}/></a>}
  </div></div>})}{rows.length>1&&<p className="year-change">年度视图可能包含年内交接、共治或职位空缺，以上记录不表示全部同时任职。</p>}</>;
}
